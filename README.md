
# LinkedIn Auto Connect Bot

This project is a Python automation script that uses Selenium to automatically send personalized LinkedIn connection requests to people found in LinkedIn search results. It is designed to help you efficiently network by sending connection requests with a custom note.

## Features

- **Automated Login:** Logs into LinkedIn using credentials stored in environment variables.
- **Smart Card Filtering:** Only processes cards with a "Se connecter" (Connect) button.
- **Personalized Notes:** Extracts the recipient's first name and personalizes the connection note.
- **Robust Clicking:** Uses multiple strategies to safely click buttons, handling popups and UI quirks.
- **Pagination:** Automatically navigates through search result pages.
- **Visual Feedback:** Highlights cards in the browser to indicate success or failure.
- **Configurable Zoom:** Adjusts page zoom for better element visibility.

## Requirements

- Python 3.7+
- Google Chrome browser
- ChromeDriver (compatible with your Chrome version)
- LinkedIn account

### Python Packages

- selenium
- python-dotenv

Install dependencies with:

```bash
pip install selenium python-dotenv
```

## Setup

1. **Clone or Download the Script**

   Place `auto-messaging.py` in your working directory.

2. **Set Up Environment Variables**

   Create a `.env` file in the same directory as the script with the following content:

   ```
   LINKEDIN_EMAIL=your_email@example.com
   LINKEDIN_PASSWORD=your_linkedin_password
   ```

3. **Download ChromeDriver**

   - Download the ChromeDriver that matches your Chrome version from [here](https://sites.google.com/chromium.org/driver/).
   - Place the `chromedriver` executable in your PATH or in the same directory as the script.

4. **Edit the Script (Optional)**

   - You can change the `search_url` and `connection_note` in the `main()` function to suit your needs.

## Usage

Run the script from the command line:

```bash
python auto-messaging.py
```

The script will:

- Open Chrome and log in to LinkedIn.
- Visit the specified search results page.
- Send connection requests with your personalized note to each person found.
- Move to the next page and repeat until no more results are available.

## Notes

- **Language:** The script is tailored for French LinkedIn UI (e.g., "Se connecter", "Ajouter une note", "Envoyer"). If you use LinkedIn in another language, update the button texts accordingly.
- **LinkedIn Limits:** LinkedIn may restrict the number of connection requests you can send per day. Use responsibly to avoid account restrictions.
- **ChromeDriver:** Ensure your ChromeDriver version matches your installed Chrome browser.

## Troubleshooting

- If you encounter errors about elements not found, check that your LinkedIn UI language matches the script.
- If ChromeDriver is not found, ensure it is in your PATH or the script directory.
- For CAPTCHA or login issues, manual intervention may be required.

## Disclaimer

This project is for educational purposes only. Use at your own risk. Automating actions on LinkedIn may violate their terms of service.

---
