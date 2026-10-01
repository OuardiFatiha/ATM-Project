# Flgiht Viewer
The aim is this project is to visualize flight information on map.

The backend API connects to [OpenSky API](https://opensky-network.org/data/api) to get ADS-B flight information.

The frontend displays flight information in a 2D Leaflet map.

![Application](/doc/img/app_snapshot.png)
## Backend
### Configure OpenSky API credentials
- Go to https://opensky-network.org/, create an accound and download credentials.
- Create a .env file in the backend repository.
- Copy your credentials to the .env file as follows:

`OPENSKY_CLIENT_ID=<your client id>`
<br>
`OPENSKY_CLIENT_SECRET=<your secret>`
### Luanch backend API
The backend is a FastAPI api.
To launch the backend api:

`cd backend`

`docker build --no-cache -t atm-app .` : you can delete the no-cache option for faster build (with cache)

`docker run --env-file .env -p 8000:8000 atm-app`
 
go to *http://localhost:8000/*
to test sending a request you can type: *http://localhost:8000/api/aircraft/all*

## Frontend
The frontend is a React app.
To launch the front:

`cd frontend`

`npm install`

`npm run dev`

go to *http://localhost:5173/*