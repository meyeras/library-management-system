# Library Management System

This project is a library management system built with FastAPI and SQLAlchemy.

## Requirements

- Python 3.9.6
- Docker
- Docker Compose


## Setup and Installation using Docker Compose

1. Clone the repository:

   ```shell
   git clone <repository-url>

2. Change to project directory
    ```shell
    cd library-management-system

3. Build and run the project using Docker Compose:
    docker-compose up --build

4. Access the API documentation at http://localhost:8000/docs for detailed information about the available endpoints and request/response formats.


## Usage
The system supports users, books and borrows management.
It can be tested through the built-in FastAPI docs or through Postman (collection and environment files are part of the project)
A typical flow will include:
1. Register a user using the /register API
2. Set the user as admin. Use the pgAdmin tool to access the database and run:
    ```shell
    UPDATE USERS SET is_admin = True WHERE username = 'yourusername'
3. Call the /login API to create a token
4. Copy the access_token and select the "Authorize" button on the upper right, then paste Bearer your-token
5. Start using the APIs
6. Note that this project includes a books.json file that can be used to populate the database through the POST /books API

## Run the REST API locally
Alternatively, there is an option to run the api locally.
Here are the steps:
1. Create a virtual environment and activate it
2. Install the required packages
    ```shell
    pip install -r requirements.txt
3. Run the uvicorn server
    ```shell
    uvicorn app.main:app --host localhost --port 8000 --reload
4. Use docker compose to compose up only the postgres and pgadmin services


## PG ADMIN TOOL
PgAdmin is a web-based administration tool for managing PostgreSQL databases. It allows you to interact with the database and perform tasks such as creating tables, executing SQL queries, and managing database users.

1. To access PgAdmin, open http://localhost:8080 in your web browser. Use the following credentials to log in:

    Email: assayag.meir@gmail.com
    Password: mongodb?

2. After entering the portal, select "Add new server"
3. Give a name in the General tab then move to Connection
4. Use Host name: postgres-library, port: 5432, maintenance database: postgres, username: postgres, password: password123
5. Click on Save, you should be connected now.