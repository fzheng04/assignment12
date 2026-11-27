
# IS601 Module 12 — User and Calculation Routes

This project builds on my Module 11 FastAPI calculator application by implementing user registration, login, and calculation BREAD operations. The application integrates FastAPI endpoints with existing SQLAlchemy models, Pydantic schemas, and a PostgreSQL database.

The project also includes integration testing, Docker containerization, automated security scanning, and continuous deployment to Docker Hub through GitHub Actions.

## Features

- Secure user registration and login using Argon2 password hashing.
- Calculation BREAD operations (Browse, Read, Edit, Add, Delete).
- Support for addition, subtraction, multiplication, and division.
- PostgreSQL database for persistent storage.
- Pydantic request and response validation.
- Factory pattern for arithmetic operations.
- Interactive API documentation through Swagger UI.
- Automated unit, integration, and end-to-end testing.
- Docker Compose for managing FastAPI, PostgreSQL, and pgAdmin.
- GitHub Actions for CI/CD.
- Trivy security scanning.

## Technologies

- Python 3.12
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL 17
- pytest
- Playwright
- Docker and Docker Compose
- GitHub Actions
- Trivy
- Argon2

## Project Structure

```text
assignment12/
├── .github/
│   └── workflows/
├── app/
│   ├── calculation_factory.py
│   ├── database.py
│   ├── init_db.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   └── operations/
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   │   ├── test_user_routes.py
│   │   └── test_calculation_routes.py
│   └── e2e/
├── templates/
│   └── index.html
├── screenshots/
├── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── reflection.txt
└── README.md
```

## Running the Application

### Prerequisites

- Git
- Docker
- Docker Compose

### Installation

Clone the repository:

```bash
git clone https://github.com/fzheng04/assignment12.git
cd assignment12
```

Build and start the containers:

```bash
docker compose up -d --build
```

Check container status:

```bash
docker compose ps
```

The application initializes the database tables automatically during startup.

### Application URLs

| Service | URL |
|---|---|
| FastAPI Calculator | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |
| pgAdmin | http://localhost:5050 |

Stop the containers:

```bash
docker compose down
```

## API Endpoints

### User Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/users/register` | Register a new user |
| POST | `/users/login` | Verify user credentials |

### Calculation Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/calculations` | Browse all calculations |
| GET | `/calculations/{id}` | Retrieve a calculation |
| PUT | `/calculations/{id}` | Update a calculation |
| POST | `/calculations` | Create a calculation |
| DELETE | `/calculations/{id}` | Delete a calculation |

The existing calculator endpoints from previous modules are also maintained.

## Manual API Testing

Open Swagger UI at:

http://localhost:8000/docs

Expand an endpoint, select **Try it out**, enter the request data, and click **Execute**.

### Register a User

POST `/users/register`

```json
{
  "username": "testuser",
  "email": "testuser@example.com",
  "password": "SecurePassword123!"
}
```

Expected status code: `201 Created`

The password is hashed before being stored in PostgreSQL. Passwords and password hashes are excluded from API responses.

### Login

POST `/users/login`

```json
{
  "username": "testuser",
  "password": "SecurePassword123!"
}
```

Expected status code: `200 OK`

Incorrect credentials return `401 Unauthorized`.

Login verifies credentials but does not issue authentication tokens or establish a persistent session.

### Create a Calculation

POST `/calculations`

```json
{
  "a": 10,
  "b": 5,
  "type": "add"
}
```

Expected status code: `201 Created`

Example response:

```json
{
  "id": 1,
  "a": 10,
  "b": 5,
  "type": "add",
  "result": 15
}
```

Use the actual ID returned by the API for subsequent operations.

### Browse Calculations

GET `/calculations`

Expected status code: `200 OK`

Returns a list of stored calculations.

### Read a Calculation

GET `/calculations/1`

Expected status code: `200 OK`

Returns the calculation associated with the specified ID.

### Update a Calculation

PUT `/calculations/1`

```json
{
  "a": 20,
  "b": 5,
  "type": "multiply"
}
```

Expected status code: `200 OK`

The calculation result is automatically recalculated to 100.

### Delete a Calculation

DELETE `/calculations/1`

Expected status code: `204 No Content`

Requesting the deleted calculation again returns `404 Not Found`.

### Invalid Input

POST `/calculations`

```json
{
  "a": 10,
  "b": 0,
  "type": "divide"
}
```

Expected status code: `400 Bad Request`

The application uses Pydantic validation to prevent division by zero, unsupported operations, missing fields, and invalid numeric inputs.

## Database Models

### User Model

| Field | Description |
|---|---|
| id | Unique user identifier |
| username | Unique username |
| email | Unique email address |
| password_hash | Securely hashed password |
| created_at | Account creation timestamp |

### Calculation Model

| Field | Description |
|---|---|
| id | Unique calculation identifier |
| a | First operand |
| b | Second operand |
| type | Arithmetic operation |
| result | Calculated result |

The supported operations are `add`, `subtract`, `multiply`, and `divide`.

## Pydantic Schemas

- `UserCreate`: Validates user registration data.
- `UserRead`: Defines the user response structure without exposing passwords.
- `UserLogin`: Validates login credentials.
- `CalculationCreate`: Validates calculation inputs.
- `CalculationRead`: Defines the calculation response structure.
- `CalculationType`: Restricts supported arithmetic operations.

## Calculation Factory

The `CalculationFactory` selects the appropriate arithmetic operation and creates a Calculation object.

```python
data = CalculationCreate(a=10, b=5, type="multiply")
calculation = CalculationFactory.create(data)

print(calculation.result)  # 50.0
```

The factory handles the calculation logic, while SQLAlchemy handles database persistence. The factory is reused when creating and updating calculations.

## Running Tests

Tests are organized into unit, integration, and end-to-end test directories.

Start the Docker containers before running tests:

```bash
docker compose up -d --build
```

Running tests inside Docker ensures that the application can access PostgreSQL through the Docker network.

### Unit Tests

```bash
docker compose exec web python -m pytest tests/unit/ -v --no-cov
```

Unit tests cover arithmetic operations, password security, Pydantic validation, and the calculation factory.

### User Integration Tests

```bash
docker compose exec web python -m pytest tests/integration/test_user_routes.py -v --no-cov
```

The seven user route integration tests cover:

- Successful registration
- Duplicate registration
- Invalid registration data
- Successful login
- Incorrect passwords
- Nonexistent users
- Invalid login data

The registration test also verifies that passwords are securely hashed in the database.

### Calculation Integration Tests

```bash
docker compose exec web python -m pytest tests/integration/test_calculation_routes.py -v --no-cov
```

The calculation integration tests cover:

- Creating calculations
- Browsing calculations
- Retrieving calculations
- Updating calculations
- Deleting calculations
- Nonexistent calculation IDs
- Invalid operation types
- Division by zero
- Invalid and missing inputs
- Invalid updates

### All Integration Tests

```bash
docker compose exec web python -m pytest tests/integration/ -v --no-cov
```

The integration tests use a shared database fixture with transaction rollback to prevent test data from permanently modifying the database.

### Unit and Integration Tests Together

```bash
docker compose exec web python -m pytest tests/unit/ tests/integration/ -v --no-cov
```

### Code Coverage

To avoid permission conflicts with the mounted project directory, the coverage file can be stored in a writable temporary directory.

```bash
docker compose exec -e COVERAGE_FILE=/tmp/.coverage web python -m pytest tests/unit/ tests/integration/ -v -o addopts="" --cov=app --cov=main --cov-report=term-missing
```

### End-to-End Tests

The project includes Playwright end-to-end tests that validate the existing calculator interface.

GitHub Actions automatically installs Chromium and the required browser dependencies before running these tests.

## CI/CD Pipeline

GitHub Actions automatically runs on pushes and pull requests to the main branch.

The pipeline consists of three jobs:

### 1. Test

- Configures Python 3.12.
- Starts a PostgreSQL service.
- Installs project dependencies.
- Initializes database tables.
- Runs unit tests.
- Runs integration tests.
- Runs Playwright end-to-end tests.

### 2. Security

- Builds the Docker image.
- Scans the image using Trivy.
- Checks for fixable HIGH and CRITICAL vulnerabilities.

### 3. Deploy

- Authenticates with Docker Hub using GitHub Actions secrets.
- Builds the Docker image.
- Publishes the image with the latest tag and commit SHA.

Deployment only occurs after successful testing and security scanning on pushes to the main branch.

All three CI/CD jobs passed successfully for Module 12.

GitHub Actions:

https://github.com/fzheng04/assignment12/actions

## Docker Hub

Docker Hub Repository:

https://hub.docker.com/r/fzheng04/601_module12

Pull the latest published image:

```bash
docker pull fzheng04/601_module12:latest
```

To run the published image using the existing PostgreSQL container, first start the database:

```bash
docker compose up -d db
```

Then run:

```bash
docker run --rm --name module12-check \
  --network assignment12_app-network \
  -e DATABASE_URL="postgresql+psycopg://postgres:postgres@db:5432/fastapi_db" \
  -p 8001:8000 \
  fzheng04/601_module12:latest
```

The published application can then be accessed at:

http://localhost:8001/docs

Port 8001 avoids conflicts with the local development application running on port 8000.

## Security

- Passwords are hashed using Argon2 before database storage.
- Password hashes are excluded from API responses.
- Invalid login credentials return an unauthorized response.
- Pydantic validates incoming user and calculation data.
- SQLAlchemy handles database interactions.
- Database uniqueness constraints prevent duplicate usernames and emails.
- GitHub Actions secrets protect Docker Hub credentials.
- Trivy scans Docker images for known vulnerabilities.
- The Docker application runs as a non-root user.

Authentication tokens and authorization restrictions are not implemented in this module. Calculation endpoints are accessible without authentication.

## Troubleshooting

### PostgreSQL Connection Errors

PostgreSQL is accessible through the internal Docker network. Tests should be executed inside the web container rather than directly from the host machine unless a host database port is configured.

### Coverage Permission Errors

If pytest cannot access the `.coverage` file, use `--no-cov` or set the `COVERAGE_FILE` environment variable to a writable temporary location.

### Docker DNS Errors

If the web container cannot resolve the database hostname, restart Docker Desktop and recreate the containers.

```bash
docker compose down
docker compose up -d --build
```

The Module 12 Docker Compose project uses a separate project name to avoid conflicts with previous assignments.

## Screenshots

Screenshots demonstrating the working application, API endpoints, GitHub Actions workflow, and Docker Hub deployment are included in the `screenshots/` directory.

## Reflection

My reflection on the development process, integration testing, Docker troubleshooting, and CI/CD deployment is included in [reflection.txt](reflection.txt).

## Future Development

Module 12 completes the required backend functionality of the calculator application.

Module 13 will focus on developing a frontend that interacts with the user and calculation API endpoints.

## Author

Feiyang Zheng  
NJIT — IS601  
Module 12 Assignment
