"""Payment-option section of the Review & Pay step. This page object deliberately
exposes no method that submits the 'Securely Pay' action - per the assignment's safety
rules, automation must never trigger a real financial transaction."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class PaymentPage(BasePage):
    # Headings render as "Pay Now" / "Pay Upon Arrival" in the DOM; CSS applies the
    # all-caps display style seen on screen.
    PAY_NOW_OPTION = (By.XPATH, "//*[normalize-space(text())='Pay Now']")
    PAY_UPON_ARRIVAL_OPTION = (By.XPATH, "//*[contains(text(),'Pay Upon') and contains(text(),'Arrival')]")
    PAYABLE_NOW_RESERVATION_FEE = (By.XPATH, "//*[contains(text(),'Payable Now')]/following::*[contains(text(),'₹')][1]")
    SECURELY_PAY_BUTTON = (By.XPATH, "//button[contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'SECURELY PAY')]")

    def is_pay_now_visible(self) -> bool:
        return self.is_visible(self.PAY_NOW_OPTION)

    def is_pay_upon_arrival_visible(self) -> bool:
        return self.is_visible(self.PAY_UPON_ARRIVAL_OPTION)

    def get_payable_now_reservation_fee(self) -> str:
        return self.get_text(self.PAYABLE_NOW_RESERVATION_FEE)

    def is_securely_pay_button_present(self) -> bool:
        """Confirms the final payment CTA is reached, without ever clicking it."""
        return self.is_visible(self.SECURELY_PAY_BUTTON)

    def get_securely_pay_button_text(self) -> str:
        return self.get_text(self.SECURELY_PAY_BUTTON)
