🏠 Zillow Property Scraper

A robust web scraping tool designed to extract real estate listings from Zillow.com. Built with Python and Selenium, this scraper automates property data collection while handling modern web challenges like dynamic content loading and anti-bot measures.

✨ Key Features

**Automated Scrolling**: Simulates human-like browsing behavior to load all listings
  
**Comprehensive Data Extraction**:

  - Property Prices
  - Addresses & Zip Codes
  - Bed/Bath Counts
  - Square Footage
  - Direct Listing URLs
  - 
**Anti-Detection Techniques**:
  
  - Randomized delays between actions
  - Chrome browser fingerprint masking
  - Headless browsing support
    
**CSV Export**: Cleanly formatted output ready for analysis
  
**Streamlit Interface**: User-friendly web UI for non-technical users

🛠️ Technical Stack

- **Python 3.9+**
- **Selenium WebDriver**
- **Streamlit** (Web Interface)
- **Pandas** (Data Processing)
- **WebDriver Manager** (Automatic driver setup)


## 🚀 Usage
1. Start Streamlit interface:
  
2. Input Zillow search URL (e.g., `https://www.zillow.com/homes/for_rent/`)
   
3. Click "Start Scraping"
   
4. Download CSV when complete

⚠️ Important Notes

- Add random delays between requests to avoid IP blocking
  
- Zillow frequently updates their DOM structure - monitor selector changes
  
- Recommended to use residential proxies for large-scale scraping
  
- Respect `robots.txt` and website terms of service

This description emphasizes the tool's capabilities while being transparent about its limitations. 
