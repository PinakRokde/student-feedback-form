"""
test_form.py — Selenium Test Suite
Student Feedback Registration Form
======================================
Covers 12 test cases:
  TC01  Page loads correctly (title, all fields, gender options, submit button)
  TC02  Blank form submission shows required-field error messages
  TC03  Invalid name (digits/special chars) is rejected
  TC04  Invalid email format is rejected
  TC05  Invalid mobile number is rejected
  TC06  Department dropdown contains expected options
  TC07  Feedback comments validation works
  TC08  Name field: too short (< 2 chars) raises an error
  TC09  Gender radio buttons are selectable
  TC10  Department dropdown contains all expected options
  TC11  Fully-valid form submission shows success screen
  TC12  Reset button returns the form to its initial state

Run:
  pip3 install selenium webdriver-manager pytest
  pytest test_form.py -v        # via pytest
  python3 test_form.py          # direct execution
"""

import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# ── Paths ────────────────────────────────────────────────────────────────────
_DIR = os.path.dirname(os.path.abspath(__file__))

# Local chromedriver binary (same folder as this file)
CHROMEDRIVER_PATH = os.path.join(_DIR, "chromedriver")

# Absolute URL to the form HTML
FORM_PATH = os.path.join(_DIR, "index.html")
FORM_URL = f"file:///{FORM_PATH}"


# ── Chrome options factory ────────────────────────────────────────────────────
def _chrome_options() -> Options:
    opts = Options()
    # opts.add_argument("--headless=new")            # uncomment to hide Chrome
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--allow-file-access-from-files")  # needed for file:// URLs
    opts.add_argument("--disable-web-security")
    return opts


# ── Fixture: Chrome WebDriver ─────────────────────────────────────────────────
# Tries the local chromedriver first; falls back to webdriver_manager if the
# binary is missing or its version is incompatible with the installed Chrome.
@pytest.fixture(scope="module")
def driver():
    opts = _chrome_options()
    drv = None

    # 1️⃣  Attempt: local chromedriver
    if os.path.isfile(CHROMEDRIVER_PATH):
        try:
            drv = webdriver.Chrome(
                service=Service(executable_path=CHROMEDRIVER_PATH),
                options=opts,
            )
        except Exception as local_err:
            print(f"[warn] Local chromedriver failed ({local_err}); falling back to webdriver_manager.")
            drv = None

    # 2️⃣  Fallback: webdriver_manager auto-downloads the matching driver
    if drv is None:
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            drv = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=opts,
            )
        except Exception as wdm_err:
            raise RuntimeError(
                f"Could not start Chrome with either local chromedriver or webdriver_manager.\n"
                f"webdriver_manager error: {wdm_err}"
            ) from wdm_err

    drv.implicitly_wait(5)
    yield drv
    drv.quit()


# ── Helpers ──────────────────────────────────────────────────────────────────
def load_form(driver):
    """Navigate to the form and wait until #registrationForm is ready."""
    driver.get(FORM_URL)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "registrationForm"))
    )
    # Small buffer to allow DOMContentLoaded JS listeners to attach
    time.sleep(0.4)


def js_click(driver, element):
    """Click an element via JavaScript to avoid click-interception issues."""
    driver.execute_script("arguments[0].click();", element)


def js_submit(driver):
    """Trigger form submit via JavaScript."""
    driver.execute_script("document.getElementById('submitBtn').click();")
    time.sleep(0.5)


def fill_field(driver, field_id: str, value: str):
    """Clear a field, type a value, then blur it to trigger validators."""
    el = driver.find_element(By.ID, field_id)
    el.clear()
    el.send_keys(value)
    # Dispatch blur so inline validators fire
    driver.execute_script(
        "arguments[0].dispatchEvent(new Event('blur', {bubbles:true}));", el
    )
    time.sleep(0.15)


def error_text(driver, error_id: str) -> str:
    """Return trimmed text of an error <span>."""
    return driver.find_element(By.ID, error_id).text.strip()


def select_gender(driver, value: str):
    """Select a gender radio button via JS (inputs are visually hidden)."""
    radio = driver.find_element(
        By.CSS_SELECTOR, f'input[name="gender"][value="{value}"]'
    )
    driver.execute_script("arguments[0].click();", radio)
    time.sleep(0.15)


def select_department(driver, value: str):
    """Select a department option from the dropdown."""
    sel = Select(driver.find_element(By.ID, "department"))
    sel.select_by_value(value)
    driver.execute_script(
        "document.getElementById('department').dispatchEvent(new Event('change', {bubbles:true}));"
    )
    time.sleep(0.15)


def check_terms(driver):
    """Tick the terms checkbox if not already checked."""
    cb = driver.find_element(By.ID, "terms")
    if not cb.is_selected():
        js_click(driver, cb)
    time.sleep(0.1)


VALID = {
    "name":        "Pinak Rokde",
    "email":       "pinak.rokde@symbiosis.in",
    "mobile":      "9876543210",
    "department":  "Computer Science",
    "gender":      "Female",
    "comments":    "This is a great educational institution with excellent faculty and facilities. The campus environment is very conducive to learning."
}


# ════════════════════════════════════════════════════════════════════════════
# Test Cases
# ════════════════════════════════════════════════════════════════════════════

class TestPageLoad:
    """TC01 — Page loads with required elements."""

    def test_tc01_page_title(self, driver):
        load_form(driver)
        assert "Feedback" in driver.title, \
            f"Page title should contain 'Feedback', got: {driver.title}"

    def test_tc01_form_fields_present(self, driver):
        for fid in ("name", "email", "mobile", "department", "comments"):
            el = driver.find_element(By.ID, fid)
            assert el.is_displayed(), f"Field #{fid} should be visible"

    def test_tc01_gender_options_present(self, driver):
        radios = driver.find_elements(By.CSS_SELECTOR, 'input[name="gender"]')
        assert len(radios) == 4, \
            f"Expected 4 gender radio options, found {len(radios)}"

    def test_tc01_submit_button_present(self, driver):
        btn = driver.find_element(By.ID, "submitBtn")
        assert btn.is_displayed() and btn.is_enabled(), \
            "Submit button should be visible and enabled"


class TestBlankFormSubmission:
    """TC02 — All fields blank → error messages appear."""

    def test_tc02_blank_submit_shows_errors(self, driver):
        load_form(driver)
        js_submit(driver)

        for err_id, field in [
            ("name-error",       "Name"),
            ("email-error",      "Email"),
            ("mobile-error",     "Mobile"),
            ("department-error", "Department"),
            ("gender-error",     "Gender"),
            ("comments-error",   "Comments"),
        ]:
            assert error_text(driver, err_id) != "", \
                f"{field} error should appear on blank submit"

    def test_tc02_success_message_hidden(self, driver):
        msg = driver.find_element(By.ID, "successMsg")
        assert not msg.is_displayed(), \
            "Success message must remain hidden on blank submit"


class TestNameValidation:
    """TC03 + TC08 — Name field validation."""

    def test_tc03_name_with_digits_rejected(self, driver):
        load_form(driver)
        fill_field(driver, "name", "Raj123")
        js_submit(driver)
        err = error_text(driver, "name-error")
        assert err != "", \
            f"Name with digits should produce an error, got none"

    def test_tc08_name_too_short(self, driver):
        load_form(driver)
        fill_field(driver, "name", "A")
        js_submit(driver)
        err = error_text(driver, "name-error")
        assert "2" in err or "characters" in err.lower(), \
            f"Expected min-length error, got: '{err}'"

    def test_tc03_valid_name_accepted(self, driver):
        load_form(driver)
        fill_field(driver, "name", "Pinak Rokde")
        js_submit(driver)
        err = error_text(driver, "name-error")
        assert err == "", \
            f"Valid name should produce no error, got: '{err}'"


class TestEmailValidation:
    """TC04 — Email format must be valid."""

    @pytest.mark.parametrize("bad_email", [
        "notanemail",
        "missing@",
        "@nodomain.com",
        "double@@domain.com",
    ])
    def test_tc04_invalid_email_rejected(self, driver, bad_email):
        load_form(driver)
        fill_field(driver, "email", bad_email)
        js_submit(driver)
        err = error_text(driver, "email-error")
        assert err != "", \
            f"Email '{bad_email}' should be rejected, got no error"

    def test_tc04_valid_email_accepted(self, driver):
        load_form(driver)
        fill_field(driver, "email", "pinak.rokde@symbiosis.ac.in")
        js_submit(driver)
        err = error_text(driver, "email-error")
        assert err == "", \
            f"Valid email should produce no error, got: '{err}'"


class TestMobileValidation:
    """TC05 — Mobile number validation."""

    def test_tc05_invalid_mobile_rejected(self, driver):
        load_form(driver)
        fill_field(driver, "mobile", "12345")
        js_submit(driver)
        err = error_text(driver, "mobile-error")
        assert err != "" and ("10" in err or "digit" in err.lower()), \
            f"Invalid mobile error expected, got: '{err}'"

    def test_tc05_mobile_with_letters_rejected(self, driver):
        load_form(driver)
        fill_field(driver, "mobile", "987654321a")
        js_submit(driver)
        err = error_text(driver, "mobile-error")
        assert err != "", \
            f"Mobile with letters should produce an error, got none"

    def test_tc05_valid_mobile_accepted(self, driver):
        load_form(driver)
        fill_field(driver, "mobile", "9876543210")
        js_submit(driver)
        err = error_text(driver, "mobile-error")
        assert err == "", \
            f"Valid mobile should produce no error, got: '{err}'"


class TestCommentsValidation:
    """TC07 — Feedback comments validation."""

    def test_tc07_comments_too_short(self, driver):
        load_form(driver)
        fill_field(driver, "comments", "Hi")
        js_submit(driver)
        err = error_text(driver, "comments-error")
        assert err != "" and ("10" in err or "characters" in err.lower()), \
            f"Short comments error expected, got: '{err}'"

    def test_tc07_comments_too_long(self, driver):
        load_form(driver)
        long_comment = "A" * 1001
        fill_field(driver, "comments", long_comment)
        js_submit(driver)
        err = error_text(driver, "comments-error")
        assert err != "" and ("1000" in err or "exceed" in err.lower()), \
            f"Long comments error expected, got: '{err}'"

    def test_tc07_valid_comments_accepted(self, driver):
        load_form(driver)
        fill_field(driver, "comments", "This is excellent feedback with proper length.")
        js_submit(driver)
        err = error_text(driver, "comments-error")
        assert err == "", \
            f"Valid comments should produce no error, got: '{err}'"


class TestDepartmentDropdown:
    """TC06 — Department dropdown validation."""

    def test_tc06_department_selection_required(self, driver):
        load_form(driver)
        js_submit(driver)
        err = error_text(driver, "department-error")
        assert err != "", "Department selection should be required"

    def test_tc06_department_selection_clears_error(self, driver):
        load_form(driver)
        js_submit(driver)
        assert error_text(driver, "department-error") != "", \
            "Department error should appear on blank submit"
        select_department(driver, "Computer Science")
        js_submit(driver)
        err = error_text(driver, "department-error")
        assert err == "", \
            f"Selecting a department should clear its error, got: '{err}'"


class TestGenderSelection:
    """TC10 — Gender radio buttons work."""

    @pytest.mark.parametrize("gender_val", [
        "Male", "Female", "Other", "Prefer not to say"
    ])
    def test_tc10_gender_radio_selectable(self, driver, gender_val):
        load_form(driver)
        select_gender(driver, gender_val)
        radio = driver.find_element(
            By.CSS_SELECTOR, f'input[name="gender"][value="{gender_val}"]'
        )
        assert radio.is_selected(), \
            f"Gender radio '{gender_val}' should be selected after click"

    def test_tc10_no_gender_shows_error(self, driver):
        load_form(driver)
        js_submit(driver)
        err = error_text(driver, "gender-error")
        assert err != "", "Missing gender should produce an error"


class TestDepartmentOptions:
    """TC10 — Department dropdown contains correct options."""

    EXPECTED_VALUES = [
        "Computer Science", "Information Technology", "Mechanical Engineering",
        "Electrical Engineering", "Civil Engineering", "Business Administration",
        "Commerce", "Arts", "Science", "Other",
    ]

    def test_tc10_all_departments_present(self, driver):
        load_form(driver)
        sel = Select(driver.find_element(By.ID, "department"))
        actual = [o.get_attribute("value") for o in sel.options if o.get_attribute("value")]
        for d in self.EXPECTED_VALUES:
            assert d in actual, f"Department '{d}' not found in dropdown"


class TestFullValidSubmission:
    """TC11 — All valid inputs → success screen shown."""

    def test_tc11_valid_form_submission(self, driver):
        load_form(driver)

        fill_field(driver, "name",       VALID["name"])
        fill_field(driver, "email",      VALID["email"])
        fill_field(driver, "mobile",     VALID["mobile"])
        select_department(driver, VALID["department"])
        select_gender(driver, VALID["gender"])
        fill_field(driver, "comments",   VALID["comments"])

        js_submit(driver)

        # Wait up to 3 s for the success message to appear
        WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.ID, "successMsg"))
        )
        success_el = driver.find_element(By.ID, "successMsg")
        assert success_el.is_displayed(), \
            "Success message should be visible after valid submission"

    def test_tc07_form_hidden_after_success(self, driver):
        # Continuing from the previous test — form should now be hidden
        form = driver.find_element(By.ID, "registrationForm")
        assert not form.is_displayed(), \
            "Registration form should be hidden on the success screen"


class TestResetBehavior:
    """TC12 — Reset button returns to the form screen."""

    def test_tc12_reset_shows_form(self, driver):
        # Success screen should still be visible from TC07
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "successMsg"))
        )
        driver.execute_script("resetForm();")
        time.sleep(0.4)

        form = driver.find_element(By.ID, "registrationForm")
        assert form.is_displayed(), "Form should reappear after reset"

        success = driver.find_element(By.ID, "successMsg")
        assert not success.is_displayed(), \
            "Success message should be hidden after reset"

    def test_tc12_fields_cleared_after_reset(self, driver):
        assert driver.find_element(By.ID, "name").get_attribute("value") == "", \
            "Name field should be empty after reset"
        assert driver.find_element(By.ID, "email").get_attribute("value") == "", \
            "Email field should be empty after reset"


# ── Direct execution entry point ──────────────────────────────────────────────
if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
