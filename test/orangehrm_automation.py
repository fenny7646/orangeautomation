import csv
import os
import sys
import time
import traceback
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Page, Browser, Playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError

try:
    load_dotenv()
except Exception as env_err:
    print(f"[WARNING] Could not load .env file: {env_err}", file=sys.stderr)


class OrangeHRMAutomation:
    BASE_URL = os.getenv("BASE_URL", "https://opensource-demo.orangehrmlive.com")
    LOGIN_URL = os.getenv("LOGIN_URL", f"{BASE_URL}/web/index.php/auth/login")

    def __init__(
        self,
        headless: Optional[bool] = None,
        slow_mo: int = 150,
        base_url: Optional[str] = None,
        login_url: Optional[str] = None
    ):
        try:
            if headless is None:
                env_headless = os.getenv("HEADLESS", "false").strip().lower()
                self.headless = env_headless in ("true", "1", "yes")
            else:
                self.headless = bool(headless)

            self.slow_mo = max(0, int(slow_mo)) if isinstance(slow_mo, (int, float)) else 150
            self.base_url = str(base_url or os.getenv("BASE_URL", self.BASE_URL)).strip()
            self.login_url = str(login_url or os.getenv("LOGIN_URL", self.LOGIN_URL)).strip()
            self.logs: List[str] = []
        except Exception as init_err:
            print(f"[ERROR] Error in OrangeHRMAutomation initialization: {init_err}", file=sys.stderr)
            raise

    def log(self, message: str) -> None:
        try:
            entry = f"[{time.strftime('%H:%M:%S')}] {message}"
            self.logs.append(entry)
            print(entry)
        except Exception:
            pass

    def login(self, page: Page, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        if not username or not str(username).strip() or not password or not str(password).strip():
            self.log("Login failed: Username and password not received.")
            raise ValueError("Username and password not received")

        username = str(username).strip()
        password = str(password).strip()

        if page is None or page.is_closed():
            raise RuntimeError("Browser page is closed or not available.")

        self.log(f"Opening login page: {self.login_url}")
        try:
            page.goto(self.login_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("input[name='username']", timeout=25000)
        except PlaywrightTimeoutError as te:
            self.log(f"Navigation timeout while opening login page: {te}")
            raise TimeoutError(f"Login page unreachable or timed out ({self.login_url})")
        except Exception as ge:
            self.log(f"Page load error: {ge}")
            raise RuntimeError(f"Could not load login page: {ge}")

        self.log(f"Entering credentials for username: '{username}'")
        try:
            user_input = page.locator("input[name='username']").first
            pass_input = page.locator("input[name='password']").first

            if user_input.count() == 0 or pass_input.count() == 0:
                raise RuntimeError("Credential input fields could not be found on the page.")

            user_input.fill(username)
            pass_input.fill(password)
            
            self.log("Clicking Login button...")
            submit_btn = page.locator("button[type='submit']").first
            if submit_btn.count() == 0:
                raise RuntimeError("Login submit button not found.")
            submit_btn.click()
        except Exception as fill_err:
            self.log(f"Failed entering credentials: {fill_err}")
            raise RuntimeError(f"Error submitting login form: {fill_err}")

        try:
            page.wait_for_selector(
                ".oxd-topbar-header-userarea, .oxd-sidepanel, .oxd-alert-content, .oxd-alert--error",
                timeout=20000
            )
            
            alert_locator = page.locator(".oxd-alert-content, .oxd-alert--error")
            if alert_locator.count() > 0 and alert_locator.first.is_visible():
                alert_text = alert_locator.first.inner_text().strip()
                self.log(f"Login alert detected: '{alert_text}'")
                raise ValueError("Username or password is wrong")

            page.wait_for_url("**/web/index.php/**", timeout=15000)
        except PlaywrightTimeoutError:
            self.log("Timeout waiting for dashboard navigation. Login may have failed.")
            raise ValueError("Username or password is wrong")
        except ValueError:
            raise
        except Exception as nav_err:
            self.log(f"Dashboard verification error: {nav_err}")
            raise RuntimeError(f"Login failed: Username or password is wrong ({str(nav_err)})")

        self.log("Login successful! Dashboard loaded.")
        return True

    def navigate_to_pim(self, page: Page) -> bool:
        if page is None or page.is_closed():
            raise RuntimeError("Browser page is closed or not available.")

        self.log("Navigating to PIM (Personnel Information Management) section...")
        try:
            pim_link = page.locator(
                "a[href*='/pim/viewPimModule'], a:has-text('PIM'), .oxd-main-menu-item:has-text('PIM')"
            ).first
            
            if pim_link.count() == 0:
                raise RuntimeError("PIM navigation menu item not found in dashboard.")

            pim_link.click()
            page.wait_for_url("**/pim/**", timeout=30000)
            page.wait_for_selector(".oxd-topbar-header-breadcrumb, .oxd-table-filter, .oxd-topbar-body-nav, .oxd-table", timeout=30000)
            self.log("Successfully navigated to PIM section.")
            return True
        except PlaywrightTimeoutError as te:
            self.log(f"Timeout navigating to PIM module: {te}")
            raise TimeoutError(f"PIM module failed to load within timeout: {te}")
        except Exception as e:
            self.log(f"PIM navigation error: {e}")
            raise RuntimeError(f"Error navigating to PIM module: {e}")

    def add_employee(
        self,
        page: Page,
        first_name: str,
        last_name: str,
        employee_id: Optional[str] = None
    ) -> Dict[str, Any]:
        if page is None or page.is_closed():
            raise RuntimeError("Browser page is closed or not available.")

        first_name = (first_name or "Automation").strip()
        last_name = (last_name or "Tester").strip()
        self.log(f"Adding new employee: {first_name} {last_name} (ID: {employee_id or 'Auto'})")
        
        try:
            add_btn = page.locator(
                "a:has-text('Add Employee'), button:has-text('Add'), button.oxd-button--secondary"
            ).first
            
            if add_btn.count() == 0:
                raise RuntimeError("Add Employee button could not be located.")

            add_btn.click()
            page.wait_for_url("**/pim/addEmployee**", timeout=20000)
            page.wait_for_selector("input[name='firstName']", timeout=15000)
        except Exception as btn_err:
            self.log(f"Failed opening Add Employee form: {btn_err}")
            raise RuntimeError(f"Could not open Add Employee page: {btn_err}")

        try:
            self.log("Filling employee name details...")
            fn_input = page.locator("input[name='firstName']").first
            ln_input = page.locator("input[name='lastName']").first
            
            fn_input.fill(first_name)
            ln_input.fill(last_name)

            if employee_id:
                self.log(f"Setting custom Employee ID: {employee_id}")
                emp_id_input = page.locator(
                    "div.oxd-input-group:has(label:has-text('Employee Id')) input, div:has(> label:has-text('Employee Id')) input"
                ).last
                if emp_id_input.count() > 0:
                    emp_id_input.click()
                    emp_id_input.fill("")
                    emp_id_input.fill(str(employee_id).strip())

            self.log("Submitting employee registration form...")
            submit_btn = page.locator("button[type='submit']").first
            if submit_btn.count() == 0:
                raise RuntimeError("Employee submission button not found.")
            submit_btn.click()

            page.wait_for_url("**/pim/viewPersonalDetails/**", timeout=30000)
            self.log("Employee record saved successfully! Personal details page loaded.")

            return {
                "first_name": first_name,
                "last_name": last_name,
                "employee_id": employee_id,
                "status": "Created"
            }
        except PlaywrightTimeoutError as te:
            self.log(f"Timeout saving employee record: {te}")
            raise TimeoutError("Timed out while saving employee record. Form validation or server lag occurred.")
        except Exception as save_err:
            self.log(f"Error during employee registration: {save_err}")
            raise RuntimeError(f"Failed to create employee record: {save_err}")

    def save_to_csv(self, employee_data: Dict[str, Any], filepath: Optional[str] = None) -> str:
        try:
            if not filepath:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                data_dir = os.path.join(base_dir, "data")
                os.makedirs(data_dir, exist_ok=True)
                filepath = os.path.join(data_dir, "extracted_employees.csv")
            else:
                parent_dir = os.path.dirname(os.path.abspath(filepath))
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)

            file_exists = os.path.exists(filepath) and os.path.getsize(filepath) > 0
            fieldnames = ["employee_id", "first_name", "last_name", "timestamp", "status"]
            now_str = time.strftime("%Y-%m-%d %H:%M:%S")

            emp_id = str(employee_data.get("employee_id") or employee_data.get("id") or "").strip()
            fn = str(employee_data.get("first_name") or "").strip()
            ln = str(employee_data.get("last_name") or "").strip()
            status = str(employee_data.get("status") or "Success").strip()

            with open(filepath, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow({
                    "employee_id": emp_id,
                    "first_name": fn,
                    "last_name": ln,
                    "timestamp": now_str,
                    "status": status
                })

            self.log(f"Appended form data to CSV file: {filepath} ({emp_id} - {fn} {ln})")
            return filepath
        except Exception as csv_err:
            self.log(f"Warning: Error appending employee data to CSV ({csv_err})")
            return ""

    def logout(self, page: Page) -> bool:
        if page is None or page.is_closed():
            self.log("Browser page already closed; logout step marked complete.")
            return True

        self.log("Logging out of OrangeHRM securely...")
        try:
            user_dropdown = page.locator(".oxd-userdropdown-tab, p.oxd-userdropdown-name").first
            if user_dropdown.count() > 0:
                user_dropdown.click()
                page.wait_for_selector(".oxd-dropdown-menu", timeout=10000)
                logout_link = page.locator("a:has-text('Logout'), a[href*='/auth/logout']").first
                if logout_link.count() > 0:
                    logout_link.click()
                    page.wait_for_url("**/auth/login**", timeout=20000)
                    self.log("Successfully and securely logged out!")
                    return True
            self.log("User dropdown not found, continuing cleanup.")
            return True
        except Exception as logout_err:
            self.log(f"Warning: Non-fatal error during logout: {logout_err}")
            return True

    def run_full_flow(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        first_name: str = "Jane",
        last_name: str = "Doe",
        employee_id: Optional[str] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        self.logs = []
        result: Dict[str, Any] = {
            "success": False,
            "created_employee": None,
            "csv_file": None,
            "logs": self.logs,
            "duration_seconds": 0,
            "error": None
        }

        playwright_obj = None
        browser = None
        context = None
        page = None

        try:
            if not username or not str(username).strip() or not password or not str(password).strip():
                raise ValueError("Username and password not received")

            playwright_mgr = sync_playwright()
            playwright_obj = playwright_mgr.__enter__()

            try:
                browser = playwright_obj.chromium.launch(
                    headless=self.headless,
                    slow_mo=self.slow_mo
                )
            except Exception as launch_err:
                raise RuntimeError(
                    f"Failed to launch Chromium browser. Ensure playwright browsers are installed (`playwright install chromium`). Details: {launch_err}"
                )

            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            self.login(page, username, password)
            self.navigate_to_pim(page)
            created = self.add_employee(page, first_name, last_name, employee_id)
            result["created_employee"] = created
            self.logout(page)

            result["success"] = True
            self.log("All automation sequence steps completed successfully!")

            form_payload = {
                "first_name": first_name,
                "last_name": last_name,
                "employee_id": employee_id,
                "status": "Success"
            }
            csv_file_path = self.save_to_csv(form_payload)
            result["csv_file"] = csv_file_path

        except Exception as e:
            error_msg = str(e)
            self.log(f"Automation Error: {error_msg}")
            result["error"] = error_msg
        finally:
            try:
                if context:
                    context.close()
            except Exception:
                pass

            try:
                if browser:
                    browser.close()
            except Exception:
                pass

            try:
                if playwright_obj:
                    playwright_mgr.__exit__(None, None, None)
            except Exception:
                pass

            result["duration_seconds"] = round(time.time() - start_time, 2)
            result["logs"] = self.logs

        return result


if __name__ == "__main__":
    runner = OrangeHRMAutomation(headless=False)
    cli_user = sys.argv[1] if len(sys.argv) > 1 else os.getenv("ORANGE_USERNAME", "")
    cli_pass = sys.argv[2] if len(sys.argv) > 2 else os.getenv("ORANGE_PASSWORD", "")
    res = runner.run_full_flow(
        username=cli_user,
        password=cli_pass,
        first_name="Alice",
        last_name="Automator",
        employee_id=f"EMP-{int(time.time()) % 10000}"
    )
    print("\n" + "="*50)
    print(f"AUTOMATION RESULT: {'SUCCESS' if res['success'] else 'FAILED'}")
    print(f"Duration: {res['duration_seconds']}s")
    if res.get("csv_file"):
        print(f"CSV Stored at: {res['csv_file']}")
    if res["error"]:
        print(f"Error: {res['error']}")
    print("="*50)
