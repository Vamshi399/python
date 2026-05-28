# go to this link "https://freecourse.io/courses" and store the course hyperlink in a text file and then click on each and every course hyperlink 
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

# Setup WebDriver
options = webdriver.ChromeOptions()
# Connect to your already open Chrome window
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # Load visited links into a list (using 'with' automatically closes the file after reading)
    visited_links = []
    try:
        with open(r"c:\code\udemy\links_visited.txt", "r") as file:
            visited_links = [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print("links_visited.txt not found. Proceeding with an empty list.")

    # Navigate to the URL
    driver.get("https://freecourse.io/courses")

    # Store the original window handle so we can switch back to it later
    original_window = driver.current_window_handle

    # Wait for course links to load
    wait = WebDriverWait(driver, 30)  # Increased timeout to 30 seconds
    css_selector = "a[href*='/courses/']"
    try:
        course_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector)))
    except TimeoutException:
        print(f"Error: Timed out waiting for links. Current page title: '{driver.title}'")
        print("This often happens if Cloudflare is blocking the page, or the site layout changed.")
        course_elements = [] # Safely fallback to an empty list so the script doesn't crash

    actions = ActionChains(driver)

    # Iterate through elements, hover, and check
    for elem in course_elements:
        href = elem.get_attribute("href")
        if not href:
            continue
            
        # Hover the link
        actions.move_to_element(elem).perform()
        time.sleep(0.5)  # Short pause to mimic natural hover behavior
        
        # Check in the links_visited list
        if href in visited_links:
            print(f"Already visited, moving to next: {href}")
            continue
        else:
            print(f"Opening link in the existing window: {href}")
            # Force link to open as a new tab within the existing window using JavaScript
            driver.execute_script("window.open(arguments[0], '_blank');", href)
            
            # Switch to the newly opened tab (usually the last one in window_handles)
            driver.switch_to.window(driver.window_handles[-1])
            
            # Search for the first Udemy link and click it
            try:
                udemy_selector = "a[href^='https://www.udemy.com/course/']"
                udemy_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, udemy_selector)))
                print(f"Found Udemy link, clicking: {udemy_link.get_attribute('href')}")
                # Use JavaScript click to bypass overlapping elements like ads or sticky headers
                driver.execute_script("arguments[0].click();", udemy_link)
            except TimeoutException:
                print(f"Udemy link not found or timed out on page: {href}")
                
            # Switch back to the original window to continue the loop
            driver.switch_to.window(original_window)
            time.sleep(2) # Small pause before moving to the next element

finally:
    pass # Prevent Selenium from closing your existing browser when done
