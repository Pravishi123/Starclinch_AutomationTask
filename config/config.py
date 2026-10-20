"""Central configuration for the Express Booking automation framework."""
import os

BASE_URL = "https://sv2.starclinch.com/express-booking/"
ON_DEMAND_URL = "https://sv2.starclinch.com/express-booking/on-demand"

DEFAULT_BROWSER = os.environ.get("EB_BROWSER", "chrome")
HEADLESS = os.environ.get("EB_HEADLESS", "false").lower() == "true"

EXPLICIT_WAIT_SECONDS = 15
SHORT_WAIT_SECONDS = 5

SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screenshots")
REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
