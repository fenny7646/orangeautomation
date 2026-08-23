import os
import time
import pytest
from test.orangehrm_automation import OrangeHRMAutomation

@pytest.fixture
def automation_runner():
    return OrangeHRMAutomation(headless=True, slow_mo=50)


def test_orangehrm_full_employee_workflow(automation_runner):
    test_first_name = "Automation"
    test_last_name = "Tester"
    test_emp_id = f"EMP{int(time.time()) % 100000}"

    result = automation_runner.run_full_flow(
        username="Admin",
        password="admin123",
        first_name=test_first_name,
        last_name=test_last_name,
        employee_id=test_emp_id
    )

    assert result["success"] is True, f"Automation flow failed with error: {result.get('error')}"
    assert result["created_employee"] is not None
    assert result["created_employee"]["first_name"] == test_first_name
    assert result["created_employee"]["last_name"] == test_last_name
    assert len(result["logs"]) > 0
    assert result.get("csv_file") is not None
    assert os.path.exists(result["csv_file"])
    assert os.path.getsize(result["csv_file"]) > 0


def test_orangehrm_missing_credentials_error_handling(automation_runner):
    result = automation_runner.run_full_flow(
        username="",
        password="",
        first_name="Fail",
        last_name="Tester"
    )

    assert result["success"] is False
    assert result["error"] is not None
    assert "Username and password not received" in result["error"]


def test_orangehrm_invalid_credentials_error_handling(automation_runner):
    result = automation_runner.run_full_flow(
        username="InvalidUser_XYZ",
        password="WrongPassword_123",
        first_name="Fail",
        last_name="Tester"
    )

    assert result["success"] is False
    assert result["error"] is not None
    assert "Username or password is wrong" in result["error"] or "not received" in result["error"]
