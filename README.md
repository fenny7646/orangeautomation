# Automation Hub & OrangeHRM Playwright Pipeline

A modern, full-stack automation dashboard powered by Flask 3, Playwright browser automation, and real-time live terminal monitoring. The application enables users to trigger and monitor employee registration workflows on OrangeHRM with live feedback and automatic CSV data persistence.

---

## Key Features

- **Interactive Web Portal**: Premium glassmorphism UI with real-time feedback, status banners, theme toggle (dark/light), and live console mirroring.
- **Playwright Automation Engine**: Automated end-to-end OrangeHRM workflow (Login &rarr; PIM Navigation &rarr; Employee Creation &rarr; Logout).
- **Template Error Handling**: Validates credentials directly from template inputs; displays descriptive authentication error alerts without hardcoded credentials.
- **CSV Data Persistence**: Automatically records and appends completed registrations to `data/extracted_employees.csv` and renders them in the live CSV records table.
- **RESTful API**: Clean API endpoints for automation triggers, health checks, CSV retrieval, and task management.
- **Automated Test Suite**: Pytest test suite covering full workflow execution, missing credential handling, and invalid credential scenarios.

---

## Project Structure

```text
Automation/
├── app/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api.py              # REST API endpoints (/api/*)
│   │   └── main.py             # UI page routes (/, /about)
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css       # Design system & dark/light theme
│   │   └── js/
│   │       └── main.js         # Frontend controllers, fetch handlers & terminal mirror
│   ├── templates/
│   │   ├── base.html           # Base layout template
│   │   ├── index.html          # Main dashboard & registration portal
│   │   └── about.html          # Architecture & documentation view
│   └── __init__.py             # Flask application factory
├── data/
│   └── extracted_employees.csv # Automatically generated CSV storage
├── test/
│   ├── __init__.py
│   ├── orangehrm_automation.py # Playwright automation engine
│   └── test_orangehrm.py       # Pytest test cases
├── .env                        # Local environment variables
├── .env.example                # Sample environment configuration
├── config.py                   # Flask environment configurations
├── Pipfile                     # Pipenv dependencies and scripts
├── requirements.txt            # PIP requirements
└── run.py                      # Application entry point
```

---

## Environment Variables (`.env`)

Create a `.env` file in the root directory (or copy from `.env.example`):

```bash
cp .env.example .env
```

### Environment Keys Reference

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `FLASK_APP` | `app:create_app` | Application factory entry point used by Flask CLI. |
| `FLASK_ENV` | `development` | Application mode (`development`, `production`, or `testing`). |
| `FLASK_DEBUG` | `1` | Enables debug mode and hot-reloading (`1` for enabled, `0` for disabled). |
| `SECRET_KEY` | `dev-secret-key-123456` | Cryptographic secret key used for session signing and security. |
| `PORT` | `5000` | Port number on which the Flask server will listen. |
| `HOST` | `127.0.0.1` | Host address to bind the web server (`127.0.0.1` or `0.0.0.0`). |
| `BASE_URL` | `https://opensource-demo.orangehrmlive.com` | Base URL of the target OrangeHRM instance. |
| `LOGIN_URL` | `https://opensource-demo.orangehrmlive.com/web/index.php/auth/login` | Login page URL for OrangeHRM authentication. |
| `HEADLESS` | `false` | Default browser mode for Playwright (`false` opens visible browser, `true` runs in background). |

---

## Installation & Setup

Choose **one** of the two package management methods below.

### Method A: Using Pipenv (Primary & Recommended)

> **Note**: `pipenv` automatically creates the virtual environment and installs all dependencies and pinned versions directly from [`Pipfile`](file:///c:/Users/fenny/Deployer/Automation/Pipfile) and `Pipfile.lock` (no `requirements.txt` needed).

1. **Install dependencies from `Pipfile`**:
   ```bash
   pipenv install --dev
   ```

2. **Install Playwright browser binaries**:
   ```bash
   pipenv run playwright install chromium
   ```

3. **Start the Flask server**:
   ```bash
   pipenv run start
   ```
   *(or `pipenv run dev`)*

---

### Method B: Using Standard `pip` + `venv` (Alternative Fallback)

> If you do not use Pipenv, you can use Python's built-in `venv` with [`requirements.txt`](file:///c:/Users/fenny/Deployer/Automation/requirements.txt).

1. **Create and activate a virtual environment**:
   - **Windows**:
     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - **macOS / Linux**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

2. **Install packages from `requirements.txt`**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browser binaries**:
   ```bash
   playwright install chromium
   ```

4. **Start the application**:
   ```bash
   python run.py
   ```

---

## Using the Application

1. Open your browser and navigate to:
   ```text
   http://127.0.0.1:5000
   ```
2. Enter the employee details:
   - **First Name**: e.g., `Jane`
   - **Last Name**: e.g., `Doe`
   - **Employee ID**: e.g., `10482`
   - **Enter Username**: OrangeHRM username (e.g., `Admin`)
   - **Enter Password**: OrangeHRM password (e.g., `admin123`)
   - **Show Browser Window**: Check to run in headed mode, or uncheck for headless.
3. Click **Run Automation**:
   - The backend runs Playwright against OrangeHRM.
   - Real-time steps are printed to the **Live Output Terminal**.
   - Upon completion, the result displays **Task is Success** and appends the record into `data/extracted_employees.csv` and the **CSV Stored Records** table.

---

## Running Automated Tests

Run the test suite to verify the automation pipeline and error handling:

### Using Pipenv:
```bash
pipenv run test
```

### Using Pytest directly:
```bash
pytest test/test_orangehrm.py -v
```

### Test Coverage:
- `test_orangehrm_full_employee_workflow`: Full end-to-end login, employee creation, and CSV file persistence test.
- `test_orangehrm_missing_credentials_error_handling`: Verifies rejection when credentials are not supplied.
- `test_orangehrm_invalid_credentials_error_handling`: Verifies rejection when invalid credentials are provided.

---

## REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Returns server health, uptime, and system status. |
| `POST` | `/api/run-automation` | Executes the Playwright automation workflow. Accepts `{ username, password, first_name, last_name, employee_id, headless }`. |
| `GET` | `/api/csv-records` | Returns all records stored in `data/extracted_employees.csv`. |
| `GET` | `/api/tasks` | Returns active tasks list. |
| `POST` | `/api/employee` | Standalone endpoint to log employee submission payloads. |
