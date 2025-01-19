import subprocess
from time import sleep
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pyautogui as py
from database import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Environment Variables
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH')
CHROME_APP_PATH = os.getenv('CHROME_APP_PATH')
CHROME_USER_DATA_DIR = os.getenv('CHROME_USER_DATA_DIR')
DEBUGGING_PORT = os.getenv('DEBUGGING_PORT')

def pageLoadHoneDe(driver1):
    WebDriverWait(driver1, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "job-card-container--clickable"))
    )

def readingBhawishyawaniPage(driver1):
    notMyCompany = ["Dice", "Epic", "Jobot", "ClickJobs.io"]

    currentPageData = driver1.find_element(By.CLASS_NAME, "scaffold-layout__list")
    jobPostings = currentPageData.find_elements(By.CLASS_NAME, "job-card-container--clickable")

    for posting in jobPostings:
        try:
            id = posting.get_attribute("data-job-id")
            data = posting.find_element(By.CLASS_NAME, "job-card-container__link")
            title = data.text.strip()
            link = data.get_attribute('href')
            companyName = posting.find_element(By.CLASS_NAME, "artdeco-entity-lockup__subtitle ").text.strip()
            location = posting.find_element(By.CLASS_NAME, "artdeco-entity-lockup__caption ").text.strip()
            applyMethod = None

            if check_the_job(id) and companyName not in notMyCompany:
                posting.click()
                sleep(1)
                try:
                    thisButton = driver.find_element(By.CLASS_NAME, "jobs-apply-button")
                    clickThis = thisButton.find_element(By.CLASS_NAME, "artdeco-button__text").text
                    if 'easy' in clickThis.lower():
                        applyMethod = 'EasyApply'
                    else:
                        applyMethod = 'Manual'
                except NoSuchElementException:
                    applyMethod = 'CHECK'
                # jobType = driver.find_element(By.CSS_SELECTOR, 'li.job-details-jobs-unified-top-card__job-insight').text
                jobDescription = driver.find_element(By.CLASS_NAME, "jobs-description__container").text
                add_the_job(id, link, title, companyName, location, applyMethod, time.time(), 'FullTime', jobDescription, "no")

        except Exception as e:
            print(f"Error in readingBhawishyawaniPage: {e}")


from urllib.parse import urlencode

params = {
    "distance": "25.0",                   
    "f_JT": "F",                            # Fulltime 
    # "f_JT": "F,C",                        # Fulltime + Contract
    "f_TPR": "r86400",                      
    "geoId": "103644278",                 
    "keywords": "{searchText}",           
    "origin": "JOB_SEARCH_PAGE_JOB_FILTER", 
    "refresh": "true",                    
    "sortBy": "DD",                       
    "spellCorrectionEnabled": "true",    
}


def build_linkedin_url(search_text):
    """
    Dynamically constructs a LinkedIn job search URL with pagination support.

    :param search_text: The job keywords to search for.
    :param start: The pagination index (default: 0).
    :param current_job_id: The ID of the current job (default: "4129302155").
    :return: The complete LinkedIn job search URL.
    """
    params["keywords"] = search_text
    base_url = "https://www.linkedin.com/jobs/search/"
    query_string = urlencode(params)
    return f"{base_url}?{query_string}"

if __name__ == "__main__":
    chrome_data_dir = os.path.join(os.getcwd(), 'chromeData')
    if not os.path.exists(chrome_data_dir):
        os.makedirs(chrome_data_dir)
        print(f"'{chrome_data_dir}' directory was created.")
    else:
        print(f"'{chrome_data_dir}' directory already exists.")

    chromeApp = subprocess.Popen([
        CHROME_APP_PATH,
        f'--remote-debugging-port={DEBUGGING_PORT}',
        f'--user-data-dir={CHROME_USER_DATA_DIR}'
    ])
    sleep(2)

    # Configure WebDriver
    options = Options()
    options.add_experimental_option("debuggerAddress", f"localhost:{DEBUGGING_PORT}")
    options.add_argument(f"webdriver.chrome.driver={CHROME_DRIVER_PATH}")
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=options)

    # Job Keywords List
    myList = ["flask", "python automation", "python developer"]
    for eachElement in myList:
        currentPage = 0
        searchText = build_linkedin_url(eachElement.strip())
        print(searchText)
        # pageURL = f"https://www.linkedin.com/jobs/search/?&distance=25.0&f_JT=F%2CC&f_T=25764%2C30006%2C6483%2C22848%2C25165&f_TPR=r86400&geoId=103644278&keywords={searchText}&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true&sortBy=DD&spellCorrectionEnabled=true&start="
        driver.get(searchText)
        while True:
            sleep(4)
            try:
                driver.find_element(By.CLASS_NAME, "jobs-search-no-results-banner")
                print("All Jobs have been scraped")
                break
            except NoSuchElementException:
                readingBhawishyawaniPage(driver)
            except Exception as error:
                print(f"Error: {error}")

            try:
                currentPage += 1
                nextButton = driver.find_element(By.CLASS_NAME, "jobs-search-pagination__button--next")
                nextButton.click()
            except:
                print("No more pages to scrape")
                break
    chromeApp.terminate()
    driver.quit()
