"""Step 3 of the real /on-demand wizard: 'Review & Pay' - booking summary and the
collapsible venue/contact details card. Payment-option reading lives in
payment_page.py; this page intentionally exposes no method that submits payment."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class ReviewPage(BasePage):
    VENUE_CONTACT_TOGGLE = (By.XPATH, "//p[normalize-space(text())='Venue & Contact Details']")
    VENUE_CONTACT_CARD = (By.XPATH, "//p[normalize-space(text())='Venue & Contact Details']/ancestor::div[3]")
    EDIT_CONTACT_LINK = (By.XPATH, "//a[normalize-space(text())='Edit'] | //button[normalize-space(text())='Edit']")
    BOOKING_SLOT_TIMER = (By.XPATH, "//*[contains(text(), 'Your booking slot is reserved for')]")

    @staticmethod
    def _summary_value(label: str):
        return (By.XPATH, f"//p[contains(normalize-space(.), '{label}')]/following-sibling::p[1]")

    def expand_venue_and_contact(self):
        self.click(self.VENUE_CONTACT_TOGGLE)

    def get_summary_value(self, label: str) -> str:
        return self.get_text(self._summary_value(label))

    def get_artist_type(self) -> str:
        return self.get_summary_value("Artist Type")

    def get_event_type(self) -> str:
        return self.get_summary_value("Event")

    def get_date_and_time(self) -> str:
        return self.get_summary_value("Date & Time")

    def get_gender(self) -> str:
        return self.get_summary_value("Gender")

    def get_event_duration(self) -> str:
        return self.get_summary_value("Event Duration")

    def get_offers_applied(self) -> str:
        return self.get_summary_value("Offers Applied")

    def get_venue_and_contact_text(self) -> str:
        return self.find(self.VENUE_CONTACT_CARD).text
