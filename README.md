# Salary Tracker - Backend

## ⚠️️ App is still under development, not ready to use yet ⚠️

## Description
This is the backend for the Salary Tracker application. It is used for tracking salary of employee, who works with many groups with different hourly rates.

Frontend repository can be found [here](https://github.com/xividi/salary-tracker).

## Technologies
- Python
- Pydantic
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker

## How to run
1. Clone the repository
2. Copy `.env.example` to `.env` and fill it with your data
3. Run `docker compose -f docker/docker-compose.yml build` to build the image
4. Run `./bin/run-migration.sh` to run the migrations
5. Run `docker compose -f docker/docker-compose.yml up -d` to run the container
6. Open `http://localhost:51112/docs` in your browser to see the API documentation