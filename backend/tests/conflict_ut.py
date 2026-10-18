import copy
import json
import unittest
from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from unittest.mock import patch

from app.conflict import METERS_TO_FEET, detect_conflicts, haversine_nm
from app.models import AircraftState
from app.predictor import compute_trajectories

DATASET_PATH = Path(__file__).parent / "resources" / "data.json"
PREDICTION_OFFSETS = list(range(0, 301, 30))


def load_states(path):
	with path.open(encoding="utf-8") as file:
		return [AircraftState.model_validate(record) for record in json.load(file)]


def build_trajectories(states):
	history = defaultdict(list)
	for state in states:
		history[state.icao24].append(state)
	return compute_trajectories(history)


def is_predictable(state):
	altitude = (
		state.geo_altitude
		if state.geo_altitude is not None
		else state.barometric_altitude
	)
	required = (state.latitude, state.longitude, state.true_track, state.velocity, altitude)
	return all(value is not None for value in required)


def point_at(trajectory, offset):
	return next(
		point for point in trajectory["predicted_points"]
		if point["t_offset_s"] == offset
	)


def make_twin(trajectory, altitude_shift_ft=0.0, icao24="twin01"):
	twin = copy.deepcopy(trajectory)
	twin["icao24"] = icao24
	twin["callsign"] = "TWIN"
	shift_m = altitude_shift_ft / METERS_TO_FEET
	for point in twin["predicted_points"]:
		point["altitude"] += shift_m
	return twin


def reference_conflicts(trajectories, horizontal_nm=5.0, vertical_ft=1000.0):
	found = set()
	for first, second in combinations(trajectories, 2):
		first_points = {point["t_offset_s"]: point for point in first["predicted_points"]}
		second_points = {point["t_offset_s"]: point for point in second["predicted_points"]}
		for offset in sorted(first_points.keys() & second_points.keys()):
			a, b = first_points[offset], second_points[offset]
			horizontal = haversine_nm(a["latitude"], a["longitude"], b["latitude"], b["longitude"])
			vertical = abs(a["altitude"] - b["altitude"]) * METERS_TO_FEET
			if horizontal < horizontal_nm and vertical < vertical_ft:
				found.add((first["icao24"], second["icao24"], offset))
				break
	return found


class DetectConflictsRealDataTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.states = load_states(DATASET_PATH)
		cls.trajectories = build_trajectories(cls.states)
		cls.trajectories_by_icao = {t["icao24"]: t for t in cls.trajectories}
		cls.base = cls.trajectories[0]

	def test_dataset_loads_as_aircraft_states(self):
		self.assertGreater(len(self.states), 0)
		self.assertTrue(all(isinstance(state, AircraftState) for state in self.states))

	def test_trajectories_match_predictable_latest_states(self):
		latest = {state.icao24: state for state in self.states}
		expected = {icao24 for icao24, state in latest.items() if is_predictable(state)}
		self.assertEqual({t["icao24"] for t in self.trajectories}, expected)

	def test_every_trajectory_predicts_the_full_horizon(self):
		for trajectory in self.trajectories:
			with self.subTest(icao24=trajectory["icao24"]):
				offsets = [point["t_offset_s"] for point in trajectory["predicted_points"]]
				self.assertEqual(offsets, PREDICTION_OFFSETS)

	def test_fewer_than_two_trajectories_return_no_conflicts(self):
		self.assertEqual(detect_conflicts([]), [])
		self.assertEqual(detect_conflicts([self.base]), [])

	def test_empty_predicted_points_return_no_conflicts(self):
		empty = make_twin(self.base)
		empty["predicted_points"] = []
		self.assertEqual(detect_conflicts([self.base, empty]), [])

	def test_conflict_contains_aircraft_details_distances_and_utc_timestamp(self):
		twin = make_twin(self.base)
		before = datetime.now(timezone.utc)
		conflicts = detect_conflicts([self.base, twin])
		after = datetime.now(timezone.utc)

		self.assertEqual(len(conflicts), 1)
		conflict = conflicts[0]
		self.assertEqual(conflict["icao24_1"], self.base["icao24"])
		self.assertEqual(conflict["icao24_2"], "twin01")
		self.assertEqual(conflict["callsign_1"], self.base["callsign"])
		self.assertEqual(conflict["callsign_2"], "TWIN")
		self.assertEqual(conflict["time_to_conflict_s"], 0)
		self.assertAlmostEqual(conflict["horizontal_dist_nm"], 0.0)
		self.assertAlmostEqual(conflict["vertical_dist_ft"], 0.0)
		self.assertEqual(conflict["severity"], "critical")
		self.assertEqual(conflict["detected_at"].tzinfo, timezone.utc)
		self.assertLessEqual(before, conflict["detected_at"])
		self.assertLessEqual(conflict["detected_at"], after)

	def test_horizontal_separation_prevents_conflict(self):
		twin = make_twin(self.base)
		for point in twin["predicted_points"]:
			point["longitude"] += 1.0
		self.assertEqual(detect_conflicts([self.base, twin]), [])

	def test_vertical_separation_prevents_conflict_in_either_direction(self):
		for altitude_shift_ft in (-1200.0, 1200.0):
			with self.subTest(altitude_shift_ft=altitude_shift_ft):
				twin = make_twin(self.base, altitude_shift_ft=altitude_shift_ft)
				self.assertEqual(detect_conflicts([self.base, twin]), [])

	def test_horizontal_threshold_is_exclusive(self):
		twin = make_twin(self.base)
		for distance, expected_count in ((4.999, 1), (5.0, 0), (5.001, 0)):
			with self.subTest(distance=distance):
				with patch("app.conflict.haversine_nm", return_value=distance):
					self.assertEqual(len(detect_conflicts([self.base, twin])), expected_count)

	def test_vertical_threshold_separates_999_ft_from_1001_ft(self):
		for separation_ft, expected_count in ((999.0, 1), (1001.0, 0)):
			with self.subTest(separation_ft=separation_ft):
				twin = make_twin(self.base, altitude_shift_ft=separation_ft)
				self.assertEqual(len(detect_conflicts([self.base, twin])), expected_count)

	def test_severity_requires_both_critical_thresholds_to_be_strictly_met(self):
		cases = (
			(2.999, 499.0, "critical"),
			(3.0, 499.0, "warning"),
			(2.999, 500.5, "warning"),
			(4.0, 750.0, "warning"),
		)
		for horizontal_nm, vertical_ft, expected in cases:
			with self.subTest(horizontal_nm=horizontal_nm, vertical_ft=vertical_ft):
				twin = make_twin(self.base, altitude_shift_ft=vertical_ft)
				with patch("app.conflict.haversine_nm", return_value=horizontal_nm):
					conflicts = detect_conflicts([self.base, twin])
				self.assertEqual(len(conflicts), 1)
				self.assertEqual(conflicts[0]["severity"], expected)

	def test_custom_thresholds_override_defaults(self):
		twin = make_twin(self.base, altitude_shift_ft=1200.0)
		trajectories = [self.base, twin]
		with patch("app.conflict.haversine_nm", return_value=6.0):
			self.assertEqual(detect_conflicts(trajectories), [])
			self.assertEqual(detect_conflicts(trajectories, horizontal_threshold_nm=7.0), [])
			conflicts = detect_conflicts(
				trajectories, horizontal_threshold_nm=7.0, vertical_threshold_ft=1500.0,
			)
		self.assertEqual(len(conflicts), 1)
		self.assertEqual(conflicts[0]["severity"], "warning")

	def test_smaller_custom_thresholds_reject_default_conflicts(self):
		twin = make_twin(self.base, altitude_shift_ft=100.0)
		trajectories = [self.base, twin]
		with patch("app.conflict.haversine_nm", return_value=2.0):
			self.assertEqual(len(detect_conflicts(trajectories)), 1)
			self.assertEqual(detect_conflicts(trajectories, horizontal_threshold_nm=1.0), [])
			self.assertEqual(detect_conflicts(trajectories, vertical_threshold_ft=50.0), [])

	def test_earliest_conflict_is_returned_for_unordered_points(self):
		twin = make_twin(self.base)
		for point in twin["predicted_points"]:
			if point["t_offset_s"] < 60:
				point["longitude"] += 1.0
		twin["predicted_points"].reverse()

		conflicts = detect_conflicts([self.base, twin])
		self.assertEqual(len(conflicts), 1)
		self.assertEqual(conflicts[0]["time_to_conflict_s"], 60)

	def test_each_unordered_aircraft_pair_is_checked_once(self):
		twins = [make_twin(self.base, icao24=f"twin{i:02d}") for i in range(3)]
		conflicts = detect_conflicts([self.base] + twins)
		pairs = {(conflict["icao24_1"], conflict["icao24_2"]) for conflict in conflicts}
		self.assertEqual(len(conflicts), 6)
		self.assertEqual(len(pairs), 6)

	def test_dataset_conflicts_are_well_formed(self):
		for conflict in detect_conflicts(self.trajectories):
			pair = (conflict["icao24_1"], conflict["icao24_2"])
			with self.subTest(pair=pair):
				self.assertNotEqual(conflict["icao24_1"], conflict["icao24_2"])
				self.assertIn(conflict["time_to_conflict_s"], PREDICTION_OFFSETS)
				self.assertLess(conflict["horizontal_dist_nm"], 5.0)
				self.assertLess(conflict["vertical_dist_ft"], 1000.0)
				expected = (
					"critical"
					if conflict["horizontal_dist_nm"] < 3 and conflict["vertical_dist_ft"] < 500
					else "warning"
				)
				self.assertEqual(conflict["severity"], expected)
				self.assertEqual(conflict["detected_at"].tzinfo, timezone.utc)
				for callsign in (conflict["callsign_1"], conflict["callsign_2"]):
					self.assertTrue(callsign is None or callsign == callsign.strip())

	def test_reported_distances_match_recomputed_separation(self):
		for conflict in detect_conflicts(self.trajectories):
			offset = conflict["time_to_conflict_s"]
			first = point_at(self.trajectories_by_icao[conflict["icao24_1"]], offset)
			second = point_at(self.trajectories_by_icao[conflict["icao24_2"]], offset)
			with self.subTest(offset=offset):
				self.assertAlmostEqual(
					conflict["horizontal_dist_nm"],
					haversine_nm(first["latitude"], first["longitude"],
						second["latitude"], second["longitude"]),
				)
				self.assertAlmostEqual(
					conflict["vertical_dist_ft"],
					abs(first["altitude"] - second["altitude"]) * METERS_TO_FEET,
				)

	def test_dataset_conflicts_match_reference_implementation(self):
		actual = {
			(conflict["icao24_1"], conflict["icao24_2"], conflict["time_to_conflict_s"])
			for conflict in detect_conflicts(self.trajectories)
		}
		self.assertEqual(actual, reference_conflicts(self.trajectories))


if __name__ == "__main__":
	unittest.main()
