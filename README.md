# Amazon Search Scraper

This Python script uses `undetected_chromedriver` and Selenium to scrape Amazon search results for product names and prices, with support for setting a custom country code to view region-specific results.

## Prerequisites
- **Python**: Version 3.6 or higher.
- **Chrome/Chromium**: Installed on your system.
- **Dependencies**:
  - `undetected-chromedriver`
  - `selenium`
- **Operating System**: Tested on Linux and Windows.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/amazon-search-scraper.git
   cd amazon-search-scraper
   ```
2. Install dependencies:
   ```bash
   pip install undetected-chromedriver selenium
   ```
3. Ensure Chrome or Chromium is installed:
   - **Linux**: `sudo apt install chromium-browser`
   - **macOS**: `brew install chromium`
   - **Windows**: Install Google Chrome from [chrome.google.com](https://www.google.com/chrome/).

## Usage
Run the script with the following command-line arguments:
- `country_code`: Required. The country code for the Amazon region (e.g., `FR` for France, `US` for USA).
- `--search-url`: Optional. A full Amazon search URL (e.g., `https://www.amazon.com/s?k=rtx+5070`).
- `--search-text`: Optional. A search query (e.g., `rtx 5070`) that is converted to a URL.
- `-o/--output`: Optional. Output file for results (e.g., `results.csv` or `results.txt`).

**Note**: Either `--search-url` or `--search-text` must be provided. If both are provided, `--search-url` takes priority.

### Example Commands
1. **Search with Text and Save to CSV**:
   ```bash
   python scraper.py FR --search-text "rtx 5070" -o results.csv
   ```
   - Searches for "rtx 5070" on Amazon with France as the delivery country.
   - Saves results to `results.csv` (e.g., `name,price`).

2. **Search with URL and Save to TXT**:
   ```bash
   python scraper.py ID --search-url "https://www.amazon.com/s?k=wireless+mouse" -o results.txt
   ```
   - Searches using the provided URL with Indonesia as the delivery country.
   - Saves results to `results.txt` (e.g., `name: price` per line).

3. **Search with Text, Console Output Only**:
   ```bash
   python scraper.py JP --search-text "gaming keyboard"
   ```
   - Searches for "gaming keyboard" with Japan as the delivery country.
   - Prints results to the console.

4. **Search with Both URL and Text (URL Takes Priority)**:
   ```bash
   python scraper.py DE --search-url "https://www.amazon.com/s?k=rtx+5070" --search-text "gaming laptop" -o output.csv
   ```
   - Uses the provided URL, ignores `--search-text`, and saves to `output.csv`.

### Example Output
**Console**:
```
Search URL: https://www.amazon.com/s?k=rtx+5070
Setting up stealth Chrome driver...
Driver initialized successfully.
Setting country to FR...
Waiting for data-toaster-csrftoken element...
Found data-toaster-csrftoken: hPxs4yjyeN6Ek9fjRrP4wYE6QWO+X9NOiR8zaLQB6nWHAAAAAGhhKowAAAAB
Sent POST request to set country to FR
POST response: <server response>
Page loaded successfully.
Scraping goods: names and prices...

Goods Names and Prices:
NVIDIA RTX 5070 Graphics Card: $599.99
ASUS RTX 5070 ROG Strix: $649.99
Results saved to results.csv
Driver cleaned up.
```

**results.csv**:
```csv
name,price
"NVIDIA RTX 5070 Graphics Card","$599.99"
"ASUS RTX 5070 ROG Strix","$649.99"
```

**results.txt**:
```
NVIDIA RTX 5070 Graphics Card: $599.99
ASUS RTX 5070 ROG Strix: $649.99
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue on GitHub to report bugs or suggest improvements.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Built with [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) for bypassing anti-bot protections.
- Uses [Selenium](https://www.selenium.dev/) for browser automation.
