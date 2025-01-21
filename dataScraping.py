import subprocess
from time import sleep
import time, os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import urlencode
from config import (
    CHROME_DRIVER_PATH,
    CHROME_APP_PATH,
    CHROME_USER_DATA_DIR,
    DEBUGGING_PORT,
)
from database import addTheJob, checkTheJob, getSearchKeywords
from app import app

chromeDriverPath = CHROME_DRIVER_PATH
chromeAppPath = CHROME_APP_PATH
chromeUserDataDir = CHROME_USER_DATA_DIR
debuggingPort = DEBUGGING_PORT


def waitForPageLoad(driver):
    """Wait for the job listings page to load."""
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "job-card-container--clickable"))
    )

def readJobListingsPage(driver, excludedCompanies):
    """Scrape job postings from the current page."""
    currentPageData = driver.find_element(By.CLASS_NAME, "scaffold-layout__list")
    jobPostings = currentPageData.find_elements(By.CLASS_NAME, "job-card-container--clickable")

    for posting in jobPostings:
        try:
            jobId = posting.get_attribute("data-job-id")
            jobData = posting.find_element(By.CLASS_NAME, "job-card-container__link")
            jobTitle = jobData.text.strip()
            jobLink = jobData.get_attribute('href')
            companyName = posting.find_element(By.CLASS_NAME, "artdeco-entity-lockup__subtitle ").text.strip()
            jobLocation = posting.find_element(By.CLASS_NAME, "artdeco-entity-lockup__caption ").text.strip()
            applyMethod = None
            print(f"Here:{jobId} & {checkTheJob(jobId)}")
            if not checkTheJob(jobId) and companyName not in excludedCompanies:
                print("Not here")
                posting.click()
                sleep(1)
                try:
                    applyButton = driver.find_element(By.CLASS_NAME, "jobs-apply-button")
                    buttonText = applyButton.find_element(By.CLASS_NAME, "artdeco-button__text").text
                    applyMethod = 'EasyApply' if 'easy' in buttonText.lower() else 'Manual'
                except NoSuchElementException:
                    applyMethod = 'CHECK'

                jobDescription = driver.find_element(By.CLASS_NAME, "jobs-description__container").text
                addTheJob(jobId, jobLink, jobTitle, companyName, jobLocation, applyMethod, time.time(), 'FullTime', jobDescription, "NO")

        except Exception as e:
            print(f"Error in readJobListingsPage: {e}")


params = {
    "distance": "25.0",
    "f_JT": "F",
    "f_TPR": "r86400",
    "geoId": "103644278",
    "keywords": "{searchText}",
    "origin": "JOB_SEARCH_PAGE_JOB_FILTER",
    "refresh": "true",
    "sortBy": "DD",
    "spellCorrectionEnabled": "true",
    "f_E": "2,3,4",
}


def buildLinkedinUrl(searchText):
    """Construct a LinkedIn job search URL."""
    params["keywords"] = searchText
    baseUrl = "https://www.linkedin.com/jobs/search/"
    queryString = urlencode(params)
    return f"{baseUrl}?{queryString}"


if __name__ == "__main__":
    with app.app_context():
        keywordsData = getSearchKeywords()
        excludedCompanies = keywordsData["noCompany"]
        jobKeywords = keywordsData["searchList"]
        for kk in excludedCompanies:
            print(kk)    
        chromeDataDir = os.path.join(os.getcwd(), 'chromeData')
        if not os.path.exists(chromeDataDir):
            os.makedirs(chromeDataDir)
            print(f"'{chromeDataDir}' directory was created.")
        else:
            print(f"'{chromeDataDir}' directory already exists.")

        print(chromeAppPath, debuggingPort, chromeUserDataDir)
        chromeApp = subprocess.Popen([
            chromeAppPath,
            f'--remote-debugging-port={debuggingPort}',
            f'--user-data-dir={chromeUserDataDir}'
        ])
        sleep(2)

        options = Options()
        options.add_experimental_option("debuggerAddress", f"localhost:{debuggingPort}")
        options.add_argument(f"webdriver.chrome.driver={chromeDriverPath}")
        options.add_argument("--disable-notifications")
        driver = webdriver.Chrome(options=options)

        for keyword in jobKeywords:
            searchUrl = buildLinkedinUrl(keyword.strip())
            print(searchUrl)
            driver.get(searchUrl)
            while True:
                sleep(4)
                try:
                    driver.find_element(By.CLASS_NAME, "jobs-search-no-results-banner")
                    print("All Jobs have been scraped")
                    break
                except NoSuchElementException:
                    readJobListingsPage(driver, excludedCompanies)
                except Exception as error:
                    print(f"Error: {error}")

                try:
                    nextButton = driver.find_element(By.CLASS_NAME, "jobs-search-pagination__button--next")
                    nextButton.click()
                except:
                    print("No more pages to scrape")
                    break

        chromeApp.terminate()
        driver.quit()
