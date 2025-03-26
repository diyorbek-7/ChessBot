# chess_analyzer.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException
import config
import psutil
import logging
from time import sleep

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def setup_driver():
    """Configure and return a Chrome WebDriver instance."""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver


def close_driver(driver):
    """Safely close the WebDriver and associated processes."""
    try:
        driver.quit()
    except Exception as e:
        logger.error(f"Error closing driver: {e}")
        for proc in psutil.process_iter(['pid', 'name']):
            if 'chrome' in proc.info['name'].lower():
                proc.kill()


def click_element(driver, xpath, description="element"):
    """Attempt to click an element with fallback methods."""
    try:
        element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        ActionChains(driver).move_to_element(element).click().perform()
        return True
    except Exception as e:
        logger.warning(f"Failed to click {description}: {e}")
        return False


def login(driver):
    """Log into Chess.com with provided credentials."""
    driver.get("https://www.chess.com/login")
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "login-username"))).send_keys(
        config.CHESS_USERNAME)
    driver.find_element(By.ID, "login-password").send_keys(config.CHESS_PASSWORD)
    click_element(driver, "//button[@type='submit' and contains(text(), 'Log In')]", "login button")

    # Handle potential verification
    try:
        WebDriverWait(driver, 3).until(lambda d: "login" not in d.current_url)
    except TimeoutException:
        logger.warning("Login verification timeout")


def get_review_url(game_url):
    """Generate a review URL from a Chess.com game URL."""
    if "live/game" in game_url:
        game_url = game_url.replace("live/game", "game/live")

    driver = setup_driver()
    try:
        login(driver)
        driver.get(game_url)

        if "error" in driver.current_url or "not-found" in driver.current_url:
            raise ValueError("Invalid game URL")

        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        if "analysis" not in driver.current_url:
            review_xpaths = [
                "//button[.//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'game review')]]",
                "//button[contains(@class, 'cc-button-primary') and .//span[contains(text(), 'Game Review')]]"
            ]
            for xpath in review_xpaths:
                if click_element(driver, xpath, "game review button"):
                    break
            else:
                raise Exception("Game Review button not found")

            analysis_url = game_url.replace("game/live", "analysis/game/live") + "?tab=review"
            driver.get(analysis_url)
            WebDriverWait(driver, 3).until(lambda d: "analysis" in d.current_url)

        WebDriverWait(driver, 3).until(EC.element_to_be_clickable((
            By.XPATH, "//button[contains(text(), 'Start Review')]")))

        start_review_xpaths = [
            "//button[contains(@class, 'tab-review-start-review-button') and contains(text(), 'Start Review')]",
            "//button[contains(@class,ogns.cc-button-primary') and contains(text(), 'Start Review')]"
        ]
        for xpath in start_review_xpaths:
            if click_element(driver, xpath, "start review button"):
                break
        else:
            raise Exception("Start Review button not found")

        review_url = driver.current_url
        if "review" not in review_url.lower() or "analysis" not in review_url.lower():
            raise Exception("Invalid review URL generated")

        return review_url

    except Exception as e:
        logger.error(f"Error processing game URL: {e}")
        return None
    finally:
        close_driver(driver)


if __name__ == "__main__":
    test_url = "https://www.chess.com/game/live/123456789"
    print(get_review_url(test_url))