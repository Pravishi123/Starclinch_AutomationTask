"""Contact Information fields. In the real app these live at the bottom of the same
'Event Details' wizard step (event_details_page.py), not a separate URL/step - kept as
its own page object because it is a distinct business concern."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class ContactPage(BasePage):
    FULL_NAME_INPUT = (By.XPATH, "//label[contains(text(), 'Full Name')]/following::input[1]")
    EMAIL_INPUT = (By.XPATH, "//label[contains(text(), 'Email Address')]/following::input[1]")
    PHONE_INPUT = (By.XPATH, "//label[contains(text(), 'Phone Number')]/following::input[1]")
    PROCEED_TO_CHECKOUT_BUTTON = (By.XPATH, "//button[.//text()[contains(., 'Proceed to Checkout')]]")
    FIELD_ERROR = (By.XPATH, "//p[contains(@class,'text-red') and not(contains(text(),'*'))]")

    def enter_full_name(self, name: str):
        self.type_text(self.FULL_NAME_INPUT, name)

    def enter_email(self, email: str):
        self.type_text(self.EMAIL_INPUT, email)

    def enter_phone(self, phone: str):
        self.type_text(self.PHONE_INPUT, phone)

    def enter_contact_details(self, name: str, email: str, phone: str):
        self.enter_full_name(name)
        self.enter_email(email)
        self.enter_phone(phone)

    def proceed_to_checkout(self):
        self.click(self.PROCEED_TO_CHECKOUT_BUTTON)

    def get_field_errors(self) -> list:
        return [e.text.strip() for e in self.find_all(self.FIELD_ERROR) if e.text.strip()]
