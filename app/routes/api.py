import csv
import logging
import os
import platform
import time
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request

api_bp = Blueprint("api", __name__)
logger = logging.getLogger("automation_hub.api")
START_TIME = time.time()


def get_json_data_safely():
    if not request.is_json and request.content_length and request.content_length > 0:
        return None, "Content-Type must be 'application/json'"
    try:
        data = request.get_json(silent=True)
        if data is None and request.content_length and request.content_length > 0:
            return None, "Malformed or invalid JSON payload"
        return data or {}, None
    except Exception as e:
        logger.warning(f"Error parsing request JSON: {e}")
        return None, f"JSON parse error: {str(e)}"


@api_bp.route("/health", methods=["GET"])
def health_check():
    try:
        uptime_seconds = int(time.time() - START_TIME)
        return jsonify({
            "status": "online",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": max(0, uptime_seconds),
            "environment": os.getenv("FLASK_ENV", "development"),
            "python_version": platform.python_version()
        }), 200
    except Exception as e:
        logger.exception(f"Health check encountered error: {e}")
        return jsonify({
            "status": "error",
            "error": "Health check failed",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500


@api_bp.route("/tasks", methods=["GET", "POST"])
def tasks_handler():
    try:
        if request.method == "POST":
            data, json_error = get_json_data_safely()
            if json_error:
                return jsonify({
                    "success": False,
                    "status": "Failed",
                    "error": "Invalid Payload",
                    "message": json_error
                }), 400

            raw_name = data.get("name")
            task_name = str(raw_name).strip() if raw_name is not None else ""
            if not task_name:
                return jsonify({
                    "success": False,
                    "status": "Failed",
                    "error": "Validation Error",
                    "message": "Task 'name' is required"
                }), 400

            created_task = {
                "id": int(time.time() * 1000) % 100000,
                "name": task_name[:100],
                "status": "created",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            logger.info(f"Task created: {created_task['name']} (ID: {created_task['id']})")
            return jsonify({
                "success": True,
                "status": "Success",
                "task": created_task,
                "message": f"Task '{created_task['name']}' registered successfully."
            }), 201

        return jsonify({
            "success": True,
            "tasks": [
                {"id": 1, "name": "System Health Monitor", "status": "active"},
                {"id": 2, "name": "Background Job Queue", "status": "idle"},
                {"id": 3, "name": "Automation Pipeline", "status": "ready"}
            ]
        }), 200

    except Exception as e:
        logger.exception(f"Tasks handler encountered error: {e}")
        return jsonify({
            "success": False,
            "status": "Failed",
            "error": "Internal Server Error",
            "message": str(e)
        }), 500


@api_bp.route("/csv-records", methods=["GET"])
def get_csv_records():
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csv_file = os.path.join(base_dir, "data", "extracted_employees.csv")

        if not os.path.exists(csv_file):
            return jsonify({
                "success": True,
                "records": [],
                "count": 0,
                "csv_file": csv_file,
                "message": "No CSV file generated yet."
            }), 200

        records = []
        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                records.append({
                    "row_index": idx + 1,
                    "id": row.get("employee_id") or row.get("id") or "",
                    "first_name": row.get("first_name", ""),
                    "last_name": row.get("last_name", ""),
                    "status": row.get("status", "Success"),
                    "timestamp": row.get("timestamp") or row.get("saved_at") or ""
                })

        return jsonify({
            "success": True,
            "records": records,
            "count": len(records),
            "csv_file": csv_file
        }), 200
    except Exception as e:
        logger.exception(f"Error reading CSV records: {e}")
        return jsonify({
            "success": False,
            "status": "Failed",
            "error": "CSV Read Error",
            "message": str(e)
        }), 500


@api_bp.route("/employee", methods=["POST"])
def submit_employee():
    try:
        data, json_error = get_json_data_safely()
        if json_error:
            return jsonify({
                "success": False,
                "status": "Failed",
                 "error": "Invalid Payload",
                "message": json_error
            }), 400

        first_name = str(data.get("first_name", "")).strip()
        last_name = str(data.get("last_name", "")).strip()
        employee_id = str(data.get("employee_id", "")).strip()

        if not first_name or not last_name or not employee_id:
            missing_fields = []
            if not first_name: missing_fields.append("first_name")
            if not last_name: missing_fields.append("last_name")
            if not employee_id: missing_fields.append("employee_id")
            
            return jsonify({
                "success": False,
                "status": "Failed",
                "error": "Validation Error",
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        first_name = first_name[:60]
        last_name = last_name[:60]
        employee_id = employee_id[:30]

        logger.info(f"New employee submitted: {first_name} {last_name} ({employee_id})")
        print("\n" + "="*50)
        print("[NEW EMPLOYEE SUBMISSION RECEIVED]")
        print(f"   First Name  : {first_name}")
        print(f"   Last Name   : {last_name}")
        print(f"   Employee ID : {employee_id}")
        print(f"   Timestamp   : {datetime.now(timezone.utc).isoformat()}")
        print("="*50 + "\n")

        return jsonify({
            "success": True,
            "status": "Success",
            "message": "Employee details received and logged to console.",
            "data": {
                "first_name": first_name,
                "last_name": last_name,
                "employee_id": employee_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }), 200

    except Exception as e:
        logger.exception(f"Error processing employee submission: {e}")
        return jsonify({
            "success": False,
            "status": "Failed",
            "error": "Submission Processing Error",
            "message": str(e)
        }), 500


@api_bp.route("/run-automation", methods=["POST"])
def run_automation():
    try:
        from test.orangehrm_automation import OrangeHRMAutomation
    except ImportError as import_err:
        logger.critical(f"Failed to import OrangeHRMAutomation module: {import_err}")
        return jsonify({
            "success": False,
            "status": "Failed",
            "task_status": "Failed",
            "error": "Automation Module Missing",
            "message": "The OrangeHRMAutomation module could not be loaded on the server.",
            "logs": [f"[ERROR] Import failure: {str(import_err)}"]
        }), 500

    try:
        data, json_error = get_json_data_safely()
        if json_error:
            return jsonify({
                "success": False,
                "status": "Failed",
                "task_status": "Failed",
                "error": "Invalid Payload",
                "message": f"Task is Failed: {json_error}.",
                "logs": [f"[ERROR] {json_error}"]
            }), 400

        raw_username = data.get("username")
        raw_password = data.get("password")

        username = str(raw_username).strip() if raw_username is not None else ""
        password = str(raw_password).strip() if raw_password is not None else ""

        if not username or not password:
            error_msg = "Username and password not received"
            logger.warning("Automation trigger rejected: username and password not received.")
            return jsonify({
                "success": False,
                "status": "Failed",
                "task_status": "Failed",
                "error": error_msg,
                "message": f"Task is Failed: {error_msg}.",
                "logs": [f"[ERROR] {error_msg}. Both username and password must be entered on the template."]
            }), 400

        raw_first = data.get("first_name")
        raw_last = data.get("last_name")
        raw_id = data.get("employee_id")

        first_name = str(raw_first).strip() if raw_first is not None else ""
        last_name = str(raw_last).strip() if raw_last is not None else ""
        employee_id = str(raw_id).strip() if raw_id is not None else ""

        first_name = (first_name or "Automation")[:50]
        last_name = (last_name or "Tester")[:50]
        employee_id = employee_id[:30] if employee_id else None

        raw_headless = data.get("headless")
        if isinstance(raw_headless, bool):
            headless = raw_headless
        elif isinstance(raw_headless, str):
            headless = raw_headless.strip().lower() in ("true", "1", "yes")
        else:
            headless = False

        logger.info(f"Triggering OrangeHRM automation for user='{username}', employee='{first_name} {last_name}', headless={headless}")
        print("\n" + "="*50)
        print("[TRIGGERING ORANGEHRM PLAYWRIGHT AUTOMATION]")
        print(f"   Target User : {username}")
        print(f"   Employee    : {first_name} {last_name}")
        print(f"   Employee ID : {employee_id or 'Auto'}")
        print(f"   Headless    : {headless}")
        print("="*50 + "\n")

        try:
            runner = OrangeHRMAutomation(headless=headless)
        except Exception as runner_init_err:
            logger.exception(f"Failed to initialize OrangeHRMAutomation: {runner_init_err}")
            return jsonify({
                "success": False,
                "status": "Failed",
                "task_status": "Failed",
                "error": "Runner Initialization Error",
                "message": f"Task is Failed: Could not initialize Playwright runner ({str(runner_init_err)}).",
                "logs": [f"[ERROR] Runner initialization failed: {str(runner_init_err)}"]
            }), 500

        result = runner.run_full_flow(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            employee_id=employee_id
        )

        if result.get("success", False):
            result["status"] = "Success"
            result["task_status"] = "Success"
            csv_path = result.get("csv_file") or ""
            result["message"] = f"Task is Success: OrangeHRM automation completed successfully. Data stored in CSV: {csv_path}" if csv_path else "Task is Success: OrangeHRM automation completed successfully."
            status_code = 200
        else:
            result["status"] = "Failed"
            result["task_status"] = "Failed"
            result["message"] = f"Task is Failed: {result.get('error', 'Automation encountered an error')}"
            status_code = 400

        return jsonify(result), status_code

    except Exception as e:
        logger.exception(f"Unexpected error during automation route execution: {e}")
        return jsonify({
            "success": False,
            "status": "Failed",
            "task_status": "Failed",
            "error": "Unexpected Server Error",
            "message": f"Task is Failed: Unexpected error ({str(e)})",
            "logs": [f"[ERROR] Unexpected server exception: {str(e)}"]
        }), 500
