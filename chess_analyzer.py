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

def setup_driver():
    """Configure and return a Chrome WebDriver instance."""
    logger.info("Setting up Chrome WebDriver")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    try:
        driver = webdriver.Chrome(service=Service(), options=options)
        logger.info("Chrome WebDriver initialized successfully")
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}", exc_info=True)
        raise

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