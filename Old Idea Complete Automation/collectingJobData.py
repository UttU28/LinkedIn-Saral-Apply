import subprocess
from time import sleep
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pyautogui as py
from addToJSON import checkAndAdd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


chrome_driver_path = "C:/chromeDriver/chromedriver.exe"
subprocess.Popen(['C:/Program Files/Google/Chrome/Application/chrome.exe', '--remote-debugging-port=8989', '--user-data-dir=C:/chromeDriver/tempData/'])
sleep(2)

options = Options()
options.add_experimental_option("debuggerAddress", "localhost:8989")
options.add_argument(f"webdriver.chrome.driver={chrome_driver_path}")
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(options=options)

driver.get("https://www.linkedin.com/jobs/search/?currentJobId=3778956671&distance=25.0&geoId=103644278&keywords=python%20developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&sortBy=R")

def pageLoadHoneDe(driver1):
    WebDriverWait(driver1, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "job-card-container--clickable"))
    )

def buttonLoadHoneDe(driver1):
    try:
        button = WebDriverWait(driver1, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@id='your-button-id']"))
        )
        print("Button is loaded.")
        return button
    except Exception as e:
        print("Error waiting for button:", e)
        return None

def readingBhawishyawaniPage(driver1):
    currentPageData = driver1.find_element(By.CSS_SELECTOR, "#main > div.scaffold-layout__list-detail-inner > div.scaffold-layout__list > div > ul")
    jobPostings = currentPageData.find_elements(By.CLASS_NAME, "job-card-container--clickable")
    print(len(jobPostings))

    for posting in jobPostings:
        timeStamp = time.time()
        try:
            posting.click()
            id = posting.get_attribute("data-job-id")

            state = posting.find_element(By.CLASS_NAME, "job-card-container__footer-item").text.strip().lower()

            if state == "applied":
                checkAndAdd(id, link, title, state, companyName, location, "EasyApply", timeStamp, timeStamp, "Applied", "No")
                pass
            else:
                data = posting.find_element(By.CLASS_NAME, "job-card-container__link")
                title = data.text.strip()
                link = data.get_attribute('href')
                companyName = posting.find_element(By.CLASS_NAME, "job-card-container__primary-description ").text.strip()
                location = posting.find_element(By.CLASS_NAME, "job-card-container__metadata-item ").text.strip()

                try:
                    easyApplyButton = buttonLoadHoneDe(driver)
                    if easyApplyButton:
                        easyApplyButton.click()
                    else:
                        print("No more job postings available.")
                        break
                    thisButton = posting.find_element(By.CLASS_NAME, "job-card-container__apply-method")
                    if thisButton:
                        checkAndAdd(id, link, title, state, companyName, location, "EasyApply", timeStamp, "NoTime", "NotApplied", "No")
                        sleep(5)
                        buttonLocation = thisButton.location
                        print(buttonLocation, "Sleeping Long")
                        sleep(100)
                        continue
                except NoSuchElementException:
                    checkAndAdd(id, link, title, state, companyName, location, "Manual", timeStamp, "NoTime", "NotApplied", "No")

        except Exception as e:
            print(f"Error in readingBhawishyawaniPage: {e}")

def scrollToSpecific(distance, sleepTime, rangeNo):
    print("Scrolled")
    py.moveTo(500, 500)
    for _ in range(rangeNo):
        py.scroll(distance)
        sleep(sleepTime)

if __name__ == "__main__":
    currentPage = 0
    scrollToSpecific(distance=-800, sleepTime=1, rangeNo=10)
    sleep(2)
    scrollToSpecific(distance=800, sleepTime=0.4, rangeNo=10)

    readingBhawishyawaniPage(driver)

    for i in range(3):
        try:
            scrollToSpecific(distance=-800, sleepTime=1, rangeNo=10)
            pageLoadHoneDe(driver)

            readingBhawishyawaniPage(driver)

            pageNumbers = driver.find_elements(By.CLASS_NAME, "artdeco-pagination__indicator--number")
            for pageNumber in pageNumbers:
                if pageNumber.get_attribute("data-test-pagination-page-btn") == str(currentPage + 1):
                    print(currentPage + 1, "this", pageNumber.get_attribute("data-test-pagination-page-btn"))
                    currentPage += 1
                    pageNumber.click()
                    print("Page is now clicked")
                    pageLoadHoneDe(driver)
                    scrollToSpecific(distance=200, sleepTime=0.3, rangeNo=1)
                    sleep(5)

            print(pageNumbers)
        except Exception as e:
            print(f"Error in main loop: {e}")
            print("Exiting loop")

driver.quit()
