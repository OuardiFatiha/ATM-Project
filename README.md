# ATM-Project

## Backend
Pour lancer l'api backend:

`cd backend`

`docker build --no-cache -t atm-app .`

`docker run -p 8000:8000 atm-app`
 
go to *http://localhost:8000/api/aircraft/all?min_latitude=48.8&max_latitude=49.0&min_longitude=2.2&max_longitude=2.5*

## Frontend
Pour lancer le front:

`cd frontend`

`npm install`

`npm run dev`

go to *http://localhost:5173/*