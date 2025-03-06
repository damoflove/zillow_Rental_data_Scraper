import pandas as pd
import streamlit as st
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver.set_page_load_timeout(180)
    return driver

def scroll_and_scrape(driver):
    all_listings = []
    unique_ids = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(random.uniform(2, 4))
        listings_data = scrape_page(driver)
        for listing in listings_data:
            if listing["link"] not in unique_ids:
                unique_ids.add(listing["link"])
                all_listings.append(listing)
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return all_listings

def scrape_page(driver):
    listings_data = []
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '[id^="zpid_"] > div > div.StyledPropertyCardDataWrapper-c11n-8-109-3__sc-hfbvv9-0.gpfUSu.property-card-data')
            )
        )
        listings = driver.find_elements(
            By.CSS_SELECTOR, '[id^="zpid_"] > div > div.StyledPropertyCardDataWrapper-c11n-8-109-3__sc-hfbvv9-0.gpfUSu.property-card-data'
        )
        st.write(f"Found {len(listings)} listings on the current view.")
        
        for listing in listings:
            try:
                # Price extraction
                price = listing.find_element(
                    By.CSS_SELECTOR, 'div.StyledPropertyCardDataArea-c11n-8-109-3__sc-10i1r6-0.inpsgu > div > span'
                ).text
                price = re.sub(r"[^\d]", "", price) if price != "N/A" else "N/A"
            except NoSuchElementException:
                price = "N/A"

            # Address extraction
            try:
                address = listing.find_element(By.CSS_SELECTOR, 'a > address').text
                zipcode_match = re.search(r'\b\d{5}\b', address)
                zipcode = zipcode_match.group(0) if zipcode_match else "N/A"
            except NoSuchElementException:
                address = zipcode = "N/A"

            # Property details
            beds = baths = sqft = "N/A"
            try:
                # Bedrooms
                beds_elem = listing.find_element(By.CSS_SELECTOR, 'div.StyledPropertyCardDataArea-c11n-8-109-3__sc-10i1r6-0.fqJdKU > ul > li:nth-child(1)')
                beds_text = beds_elem.get_attribute("textContent").strip()
                beds = re.search(r'\d+', beds_text).group() if re.search(r'\d+', beds_text) else "N/A"

                # Bathrooms (Updated)
                try:
                    # Wait until the element is present
                    baths_elem = WebDriverWait(listing, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.StyledPropertyCardDataArea-c11n-8-109-3__sc-10i1r6-0.fqJdKU > ul > li:nth-child(2)'))
                    )
                    # Extract text using JavaScript
                    baths_text = driver.execute_script("return arguments[0].textContent;", baths_elem).strip()
    
                    # Extract numeric value
                    baths = re.search(r'\d+(\.\d+)?', baths_text).group() if re.search(r'\d+(\.\d+)?', baths_text) else "N/A"

                except (NoSuchElementException, TimeoutException):
                    baths = "N/A"

                # Square footage
                sqft_elem = listing.find_element(By.CSS_SELECTOR, 'div.StyledPropertyCardDataArea-c11n-8-109-3__sc-10i1r6-0.fqJdKU > ul > li:nth-child(3) > b')
                sqft_text = sqft_elem.text.strip()
                sqft = re.sub(r"[^\d]", "", sqft_text) if sqft_text else "N/A"

            except NoSuchElementException:
                st.warning("Some property details are missing.")

            # Property link
            try:
                link = listing.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            except NoSuchElementException:
                link = "N/A"

            listings_data.append({
                "price": price,
                "address": address,
                "zipcode": zipcode,
                "link": link,
                "beds": beds,
                "baths": baths,
                "sqft": sqft,
            })
    except TimeoutException:
        st.error("Timeout occurred while loading the page.")
    return listings_data

def fetch_all_listings(driver, url):
    driver.get(url)
    time.sleep(5)
    st.write("Starting to scrape all visible listings on the main page...")
    return scroll_and_scrape(driver)

# Streamlit Interface
st.title("Zillow Scraper for Main Page Listings")

url = st.text_input("Enter Zillow URL:", value="https://www.zillow.com/homes/for_sale/")
if st.button("Start Scraping"):
    driver = initialize_driver()
    with st.spinner("Scraping data... Please wait."):
        try:
            data = fetch_all_listings(driver, url)
        finally:
            driver.quit()

        if data:
            df = pd.DataFrame(data)
            # Convert numeric columns to appropriate types
            numeric_cols = ['price', 'beds', 'baths', 'sqft']
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
            st.write(df)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Data as CSV",
                data=csv,
                file_name="zillow_listings.csv",
                mime="text/csv",
            )
        else:
            st.warning("No data scraped. Please verify the URL or check the debug logs.")
