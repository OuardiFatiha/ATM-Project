import { Panel } from 'primereact/panel';
import { useAircraftStates } from '../hooks/useAircraftStates';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import type { AircraftState } from '../types/AircraftState';

export const LeftPanel = () => {
    const { aircraftStates } = useAircraftStates();
    const verticalRateBody = (aircraft: AircraftState) => {
        const rate = aircraft.vertical_rate;

        if (rate == null) {
            return null;
        }

        const icon =
            rate > 0 ? 'pi-caret-up' :
                rate < 0 ? 'pi-caret-down' :
                    'pi-caret-right';

        const color =
            rate > 0 ? '#16a34a' :
                rate < 0 ? '#dc2626' :
                    '#6b7280';

        return (
            <i
                className={`pi ${icon}`}
                style={{ color }}
                title={`${rate} m/s`}
                aria-label={`${rate} meters per second`}
            />
        );
    };

    return (
        <Panel header="Aircraft States" style={{ height: '100%', width: '500px' }}>
            <div className="card">
                <DataTable value={aircraftStates} paginator rows={10} size="small">
                    <Column field="vertical_rate" header="Vertical Rate (m/s)" body={verticalRateBody} sortable></Column>
                    <Column field="callsign" header="Callsign" sortable></Column>
                    <Column field="barometric_altitude" header="Altitude (m)" sortable></Column>
                </DataTable>
            </div>
        </Panel>
    )
}