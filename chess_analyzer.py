import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# In your setup_driver() function:
def setup_driver():
    """Configure and return a Chrome WebDriver instance."""
    chrome_binary = os.getenv("CHROME_BINARY", "/tmp/chrome/chrome-linux64/chrome")
    chromedriver_binary = os.getenv("CHROMEDRIVER_BINARY", "/tmp/chromedriver/chromedriver-linux64/chromedriver")

    options = Options()
    options.binary_location = chrome_binary
    options.add_argument("--headless=new")  # New headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Anti-detection settings
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(
        executable_path=chromedriver_binary,
        service_args=['--verbose'],  # Optional logging
    )

    driver = webdriver.Chrome(service=service, options=options)

    # Mask selenium detection
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """
    })

    return driver

def analyze_game(game_url):
    """Analyze a Chess.com game and return the review URL."""
    logger.info(f"Starting analysis for game URL: {game_url}")
    driver = None
    try:
        # Set up the driver
        driver = setup_driver()

        # Log in to Chess.com
        username = os.getenv("CHESS_USERNAME")
        password = os.getenv("CHESS_PASSWORD")
        if not username or not password:
            logger.error("CHESS_USERNAME or CHESS_PASSWORD not set in environment variables")
            raise ValueError("Chess.com credentials not set")

        logger.info("Navigating to Chess.com login page")
        driver.get("https://www.chess.com/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

        logger.info("Entering username")
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "login").click()

        logger.info("Waiting for login to complete")
        WebDriverWait(driver, 10).until(EC.url_contains("chess.com/home"))

        # Navigate to the game URL
        logger.info(f"Navigating to game URL: {game_url}")
        driver.get(game_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "board")))

        # Request a review (adjust based on actual Chess.com UI)
        logger.info("Requesting game review")
        review_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Review')]"))
        )
        review_button.click()

        # Get the review URL (adjust based on actual behavior)
        logger.info("Waiting for review URL")
        WebDriverWait(driver, 10).until(EC.url_contains("analysis"))
        review_url = driver.current_url
        logger.info(f"Review URL obtained: {review_url}")

        return review_url

    except Exception as e:
        logger.error(f"Error analyzing game: {str(e)}", exc_info=True)
        raise
    finally:
        if driver:
            logger.info("Closing WebDriver")
            driver.quit()