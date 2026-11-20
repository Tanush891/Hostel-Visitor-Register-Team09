# Hostel Visitor Register

## Problem statement

Hostel staff need a simple way to record visitors who enter the hostel. Staff should be able to register and log in, add visitor details, and view the visitor records they have created. Each staff member must only see their own records. The app uses FastAPI, SQLite, and React, with password hashing and JWT access and refresh tokens.

## API contract

Protected requests use the header `Authorization: Bearer <access_token>`.

| ID | What it does | Method | Path | Request body | Success code |
| --- | --- | --- | --- | --- | ---: |
| A1 | Register a hostel staff user | `POST` | `/auth/register` | `{ "username": "Asha", "email": "asha@example.com", "password": "password123" }` | 201 |
| A2 | Log in and create JWT access and refresh tokens | `POST` | `/auth/login` | `{ "email": "asha@example.com", "password": "password123" }` | 200 |
| A3 | Create new tokens using a refresh token | `POST` | `/auth/refresh` | `{ "refresh_token": "<refresh_token>" }` | 200 |
| E1 | Get records created by the logged-in staff member | `GET` | `/visitors` | None | 200 |
| E2 | Register a visitor for the logged-in staff member | `POST` | `/visitors` | `{ "visitor_name": "Ravi Kumar", "student_name": "Sam Lee", "room_no": "204", "purpose": "Family visit", "visit_date": "2026-11-20" }` | 201 |

## Database tables

The app creates one SQLite database file named `visitors.db` with these tables:

| Table | Columns |
| --- | --- |
| `users` | `id`, `username`, `email`, `hashed_password`, `created_at` |
| `visitors` | `id`, `user_id`, `visitor_name`, `student_name`, `room_no`, `purpose`, `visit_date`, `created_at` |

Each visitor row is connected to its staff user through `user_id`. Email addresses are unique. Passwords are stored as hashes.

## Docker and deployment

- Create a Dockerfile for the FastAPI backend, build the Docker image, and run the app in a container.
- Check that the app works through the container. Docker Compose is not required.
- Use GitHub Actions to build the image when code is pushed, push the latest image to Docker Hub, connect to the team's EC2 instance, and replace the running container with the updated image.
- Store Docker Hub and EC2 credentials in GitHub Actions Secrets. Do not put credentials in the repository.
- Install Docker on one EC2 instance and make the app available through its public IP.
- Keep `visitors.db` in a persistent folder on EC2 and mount that folder into the container so records remain after a restart or deployment.


`backend/main.py` sets up the FastAPI application. `backend/functions.py` contains its Python functions and API routes. The React files provide registration, login, and the visitor dashboard. `Dockerfile` builds the app container, and `.github/workflows/deploy.yml` describes the GitHub Actions deployment workflow.
