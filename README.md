# Martech Web Application

## Project Overview

This project is a simple web application designed for uploading and processing data through CSV/XLS files. It allows users to upload data and view aggregated results in a table format. The platform also supports user authentication with two roles: **User** and **Admin**.

### Key Features

1. **Data Upload**: Users can upload XLSX files, which are parsed and stored in the database. The upload functionality works even if the column order in the file is changed.
2. **Error Handling**: If the file structure doesn't match the expected format, the user will receive an error message explaining what went wrong.
3. **Aggregated Results**: The platform displays aggregated statistics (sums of numeric columns) grouped by year.
4. **User Authentication**: The platform is protected by login credentials. It includes two levels of access:
   - **User**: Can upload data and view processed statistics.
   - **Admin**: Has additional access to admin functionalities, including viewing the log of uploaded files, user access statuses, and full uploaded data.

## How to Run

To run the project locally, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone git@github.com:d1mmm/martech.git
    cd martech
    ```

2. **Set up a virtual environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install dependencies**:
    Ensure you have `pip` installed, then run:
    ```bash
    pip install -r requirements.txt
    python3.9 setup.py sdist bdist_wheel 
    pip install dist/martech-<version>-py3-none-any.whl
    ```
4. **Export environment variable/**
   ```bash
   export DATABASE_URL="postgresql://<user>:<password>@localhost:5432/martech"
   ```

5. **Set up the database**:
    ```bash
    psql -U <postgres> <password>
    CREATE DATABASE martech;
    ```

6. **Run the application**:
    Use the following command to start the application:
    ```bash
   python3.9 app/main.py
    ```

7. **Access the application**:
    Open your browser and go to `http://0.0.0.0:8000` to access the site.

### Running Tests:
   To verify that the application functions correctly, run the provided tests using `pytest`:
   ```bash
   pytest tests/
   ```
