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

def process_course_elements(driver, course_elements, visited_links, original_window):
    actions = ActionChains(driver)
    wait = WebDriverWait(driver, 40)
    # Iterate through elements, hover, and check
    for elem in course_elements:
        href = elem.get_attribute("href")
        if not href:
            continue
            
        # Hover the link
        actions.move_to_element(elem).perform()
        time.sleep(1)  # Short pause to mimic natural hover behavior
        
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
                udemy_href = udemy_link.get_attribute('href')
                
                if udemy_href in visited_links:
                    print(f"Udemy link already visited, skipping: {udemy_href}")
                    driver.close() # Close the freecourse detail tab
                    driver.switch_to.window(original_window)
                    continue
                
                print(f"Found Udemy link, clicking: {udemy_href}")
                # Use JavaScript click to bypass overlapping elements like ads or sticky headers
                driver.execute_script("arguments[0].click();", udemy_link)
                
                # Wait for the page to load (and switch if Udemy opened in a new tab)
                time.sleep(2)
                driver.switch_to.window(driver.window_handles[-1])
                
                free_span = None
                try:
                    # Search for the parent element containing both 'Current price' and 'Free' spans and click it
                    free_span = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.XPATH, "//*[span[text()='Current price'] and span[text()='Free']]")))
                    print("Found 'Free' pricing element, clicking...")
                    driver.execute_script("arguments[0].click();", free_span)
                except TimeoutException:
                    print("'Free' span not present (course might not be free anymore). Closing tabs twice.")
                    with open(r"c:\code\udemy\links_visited.txt", "a") as f:
                        f.write(href + "\n")
                    driver.close()
                    driver.switch_to.window(driver.window_handles[-1])
                    driver.close()
                    
                if free_span:
                    try:
                        # Search for span tag of 'Enroll now' within a button tag and click it
                        enroll_span = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.XPATH, "//button//span[text()='Enroll now']")))
                        print("Found 'Enroll now' span, clicking...")
                        driver.execute_script("arguments[0].click();", enroll_span)
                        
                        # Search for the second 'Enroll now' button on the redirect page and click it
                        second_enroll_btn = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Enroll now')]")))
                        print("Found second 'Enroll now' button on checkout page, clicking...")
                        driver.execute_script("arguments[0].click();", second_enroll_btn)
                        
                        # Wait for the success page URL
                        print("Waiting for success page redirection...")
                        WebDriverWait(driver, 6).until(EC.url_contains("https://www.udemy.com/cart/success/"))
                        print("Successfully enrolled!")
                        
                        # Close the current tab 2 times (Udemy tab, then freecourse detail tab)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.close()
                    except TimeoutException:
                        print("Enrollment process timed out or 'Enroll now' button not found.")
                        print("Closing tabs twice.")
                        with open(r"c:\code\udemy\links_visited.txt", "a") as f:
                            f.write(href + "\n")
                        driver.close()
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.close()
            except TimeoutException:
                print(f"Udemy link not found or timed out on page: {href}")
                
            # Switch back to the original window to continue the loop
            driver.switch_to.window(original_window)
            time.sleep(2) # Small pause before moving to the next element

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
    wait = WebDriverWait(driver, 40)  # Increased timeout to 30 seconds
    css_selector = "a[href*='/courses/']"
    
    while True:
        try:
            course_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector)))
        except TimeoutException:
            print(f"Error: Timed out waiting for links. Current page title: '{driver.title}'")
            print("This often happens if Cloudflare is blocking the page, or the site layout changed.")
            course_elements = [] # Safely fallback to an empty list so the script doesn't crash

        process_course_elements(driver, course_elements, visited_links, original_window)
        
        try:
            print("Clicking on 'Next' button...")
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Next') or contains(text(), 'NEXT')]")))
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3) # Wait for the next page to load
        except TimeoutException:
            print("'Next' button not found. Reached the last page.")
            break

finally:
    pass # Prevent Selenium from closing your existing browser when done
