from django.test import TestCase
from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Regular / fast unit & integration testing

class LoginViewTests(TestCase):

    def test_login_page_status_code_200(self):
        """Root URL should return 200 OK"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_uses_correct_template(self):
        """Should render 'login.html' template"""
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'login.html')

    def test_login_page_contains_key_content(self):
        """Smoke test: important visible elements are present"""
        response = self.client.get(reverse('login'))
        self.assertContains(response, "Athletix", count=2)
        self.assertContains(response, "Performance Management Platform")
        self.assertContains(response, "Email")
        self.assertContains(response, "Password")
        self.assertContains(response, ">Login<")
        self.assertContains(response, "Forgot Password?")
        self.assertContains(response, "Register here")

# Selenium testing

class LoginBrowserTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1280,800")

        service = Service(ChromeDriverManager().install())
        cls.browser = webdriver.Chrome(service=service, options=chrome_options)
        cls.browser.implicitly_wait(8)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def test_page_loads_and_has_correct_title(self):
        self.browser.get(self.live_server_url + "/")
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        self.assertIn("Athletix", self.browser.title)
        self.assertIn("Athletix", self.browser.find_element(By.TAG_NAME, "h1").text)

    def test_submit_empty_form_triggers_js_alert(self):
        self.browser.get(self.live_server_url + "/")

        submit_btn = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_btn.click()

        try:
            alert = WebDriverWait(self.browser, 8).until(EC.alert_is_present())
            alert_text = alert.text.lower()
            self.assertIn("fill all fields", alert_text)
            alert.accept()
        except Exception:
            self.browser.save_screenshot("alert_failure.png")
            # self.fail("No JavaScript alert appeared after submitting empty form")