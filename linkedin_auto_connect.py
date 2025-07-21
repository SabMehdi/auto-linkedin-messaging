from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import os
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options


# Load environment variables
load_dotenv()

class LinkedInAutoConnect:
    def __init__(self):
        options = Options()
        options.add_argument(r"user-data-dir=C:\Users\saber\AppData\Local\Google\Chrome\User Data")
        options.add_argument("profile-directory=Default")
        self.driver = webdriver.Chrome(options=options)  # Make sure you have ChromeDriver installed
        
        self.wait = WebDriverWait(self.driver, 5)  # Reduced from 10 to 5 seconds
        
    def login(self):
        options = Options()
        options.add_argument(r"user-data-dir=C:\Users\saber\AppData\Local\Google\Chrome\User Data")
        options.add_argument("profile-directory=Default")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 5)
        """Login to LinkedIn"""
        self.driver.get("https://www.linkedin.com/login")
        
        # Get credentials from environment variables
        email = os.getenv("LINKEDIN_EMAIL")
        password = os.getenv("LINKEDIN_PASSWORD")
        
        # Enter email
        email_field = self.wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        email_field.send_keys(email)
        
        # Enter password
        password_field = self.driver.find_element(By.ID, "password")
        password_field.send_keys(password)
        
        # Click login button
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Wait for potential 2FA authentication
        print("\nChecking for two-factor authentication...")
        try:
            # Check for app authentication page
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "header__content__heading__inapp"))
            )
            print("\n2FA Required: Please check your LinkedIn mobile app and approve the login request.")
            print("Waiting for you to complete authentication...")
            
            # Wait for the user to complete authentication by checking for navigation to home page
            WebDriverWait(self.driver, 300).until(  # 5 minute timeout
                lambda driver: "feed" in driver.current_url or 
                             "checkpoint/challenge" not in driver.current_url
            )
            print("Authentication completed successfully!")
            
        except TimeoutException:
            # If we don't find the 2FA page, we might be already logged in
            print("No 2FA detected or already completed.")
        except Exception as e:
            print(f"Unexpected error during login: {str(e)}")
            
        # Additional wait to ensure page is loaded
        time.sleep(3)

    def scroll_to_element(self, element):
        """Scroll element into view and wait a bit"""
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(.5)

    def highlight_element(self, element, color="yellow"):
        """Highlight an element with a colored background"""
        original_style = element.get_attribute('style')
        style = f"background-color: {color} !important; border: 2px solid {color} !important;"
        self.driver.execute_script(f"arguments[0].setAttribute('style', '{style}');", element)
        return original_style

    def restore_style(self, element, original_style):
        """Restore element's original style"""
        self.driver.execute_script(f"arguments[0].setAttribute('style', '{original_style}');", element)

    def check_connect_buttons(self):
        """Check if there are any 'Se connecter' buttons on the page"""
        connect_buttons = self.driver.find_elements(
            By.XPATH,
            "//button[contains(@class, 'artdeco-button') and .//span[text()='Se connecter']]"
        )
        count = len(connect_buttons)
        print(f"\nFound {count} cards with 'Se connecter' button")
        return count

    def remove_non_connect_cards(self):
        """Remove cards that don't have 'Se connecter' button"""
        try:
            # Find all li elements (cards)
            all_cards = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'YqPvchDpIQAtSkXEsugKtLYEYIOEbePc')]")
            print(f"Total cards on page: {len(all_cards)}")
            
            # Check each card for 'Se connecter' button
            for card in all_cards:
                try:
                    # Try to find 'Se connecter' button in this card
                    connect_button = card.find_elements(By.XPATH, ".//button[contains(@class, 'artdeco-button') and .//span[text()='Se connecter']]")
                    if not connect_button:
                        # If no connect button, hide the card
                        self.driver.execute_script("arguments[0].style.display = 'none';", card)
                except:
                    # If any error occurs, hide the card
                    self.driver.execute_script("arguments[0].style.display = 'none';", card)
        except Exception as e:
            print(f"Error while filtering cards: {str(e)}")

    def set_page_zoom(self, zoom_percentage):
        """Set page zoom level"""
        zoom_decimal = zoom_percentage / 100
        self.driver.execute_script(f"document.body.style.zoom = '{zoom_decimal}'")
        time.sleep(0.5)  # Reduced from 1 to 0.5 seconds

    def click_button_safely(self, button, button_text):
        """Try multiple methods to click a button safely"""
        max_retries = 3
        for retry in range(max_retries):
            try:
                # Method 1: Direct click
                try:
                    button.click()
                    return True
                except:
                    pass

                # Method 2: JavaScript click
                try:
                    self.driver.execute_script("arguments[0].click();", button)
                    return True
                except:
                    pass

                # Method 3: Action chains
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(self.driver)
                    actions.move_to_element(button).click().perform()
                    return True
                except:
                    pass

                # Method 4: Find and click by XPath relative to current element
                try:
                    relative_button = button.find_element(By.XPATH, f".//span[text()='{button_text}']/parent::button")
                    relative_button.click()
                    return True
                except:
                    pass

                print(f"Click attempt {retry + 1} failed, trying different method...")
                time.sleep(1)
            except Exception as e:
                print(f"Click attempt {retry + 1} failed: {str(e)}")
                if retry == max_retries - 1:
                    return False
                time.sleep(1)
        return False

    def save_request_count(self, count):
        """Save the number of successful requests to a file"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open("connection_requests_log.txt", "a") as f:
            f.write(f"{timestamp}: Sent {count} connection requests\n")

    def send_connection_requests(self, search_url, connection_note, max_requests=None):
        """Send connection requests to people from search results
        
        Args:
            search_url (str): URL of the LinkedIn search results page
            connection_note (str): Template for the connection request message
            max_requests (int, optional): Maximum number of requests to send. If None, no limit.
        """
        self.driver.get(search_url)
        time.sleep(1)
        
        page_number = 1
        successful_requests = 0  # Track successful requests
        
        try:
            while True:
                print(f"\nProcessing page {page_number}")
                if max_requests is not None and successful_requests >= max_requests:
                    print(f"\nReached maximum number of requests ({max_requests}). Stopping...")
                    break
                
                # Set zoom to 75%
                self.set_page_zoom(75)
                time.sleep(.5)
                
                try:
                    # Check for connect buttons first
                    connect_buttons_count = self.check_connect_buttons()
                    
                    if connect_buttons_count == 0:
                        print("No connect buttons found on this page, moving to next page...")
                        try:
                            next_button = self.wait.until(
                                EC.element_to_be_clickable(
                                    (By.XPATH, "//button[contains(@class, 'artdeco-pagination__button--next')]")
                                )
                            )
                            if not self.click_button_safely(next_button, "Suivant"):
                                print("Failed to click next button")
                                break
                            time.sleep(.5)
                            page_number += 1
                            continue
                        except:
                            print("No more pages available")
                            break
                    
                    # If we have connect buttons, remove non-connect cards
                    self.remove_non_connect_cards()
                    
                    # Find all connect buttons in visible cards
                    connect_buttons = self.wait.until(
                        EC.presence_of_all_elements_located(
                            (By.XPATH, "//li[not(@style='display: none;')]//button[contains(@class, 'artdeco-button') and .//span[text()='Se connecter']]")
                        )
                    )
                    
                    print(f"Processing {len(connect_buttons)} connection requests")
                    
                    for i, connect_button in enumerate(connect_buttons, 1):
                        try:
                            print(f"\nProcessing connection {i} of {len(connect_buttons)}")
                            
                            # Find the parent li element using a more robust selector
                            try:
                                # First try to get the closest parent li
                                li_element = connect_button.find_element(By.XPATH, "./ancestor::li[1]")
                                
                                # Verify this is a connection card by checking for name
                                try:
                                    profile_span = li_element.find_element(By.XPATH, ".//span[contains(text(), 'Voir le profil de')]")
                                except:
                                    # If name not found in immediate li, try going up one more level
                                    li_element = connect_button.find_element(By.XPATH, "./ancestor::li[2]")
                                    profile_span = li_element.find_element(By.XPATH, ".//span[contains(text(), 'Voir le profil de')]")
                                
                                print("Successfully found profile card")
                            except Exception as e:
                                print(f"Error finding profile card: {str(e)}")
                                continue
                            
                            # Extract user name from the profile link
                            try:
                                profile_text = profile_span.text
                                # Extract only the first name (first word after "de")
                                full_name = profile_text.replace("Voir le profil de", "").strip()
                                first_name = full_name.split()[0]  # Get only the first word
                                personalized_note = connection_note.replace("Bonjour,", f"Bonjour {first_name},")
                                print(f"Extracted name: {first_name}")
                            except Exception as e:
                                print(f"Could not extract name, using default message: {str(e)}")
                                personalized_note = connection_note
                            
                            # Highlight the current profile card in yellow
                            original_style = self.highlight_element(li_element, "yellow")
                            
                            # Try to click the connect button with our safe click method
                            if not self.click_button_safely(connect_button, "Se connecter"):
                                print(f"Failed to click connect button for connection {i}")
                                self.highlight_element(li_element, "lightcoral")
                                continue
                            
                            time.sleep(.5)
                            
                            # Click "Add note" button
                            try:
                                print("Waiting for 'Add note' button...")
                                add_note_button = self.wait.until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH, "//button[.//span[text()='Ajouter une note']]")
                                    )
                                )
                                print("Found 'Add note' button, attempting to click...")
                                time.sleep(.5)  # Add small delay before clicking
                                if not self.click_button_safely(add_note_button, "Ajouter une note"):
                                    raise Exception("Failed to click add note button")
                                print("Successfully clicked 'Add note' button")
                                time.sleep(.5)  # Add delay after clicking
                            except Exception as e:
                                print(f"Error clicking add note button: {str(e)}")
                                # Try an alternative XPath if the first one fails
                                try:
                                    print("Trying alternative method to find 'Add note' button...")
                                    add_note_button = self.wait.until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH, "//button[contains(@aria-label, 'Ajouter une note')]")
                                        )
                                    )
                                    if not self.click_button_safely(add_note_button, "Ajouter une note"):
                                        raise Exception("Failed to click add note button (alternative method)")
                                except Exception as e2:
                                    print(f"Error with alternative method: {str(e2)}")
                                    self.highlight_element(li_element, "lightcoral")
                                    continue
                            
                            # Find and fill the note textarea
                            try:
                                print("Waiting for note textarea...")
                                note_textarea = self.wait.until(
                                    EC.presence_of_element_located(
                                        (By.ID, "custom-message")
                                    )
                                )
                                print("Found textarea, clearing existing text...")
                                note_textarea.clear()
                                time.sleep(.5)  # Add delay after clearing
                                
                                print(f"Sending personalized note: {personalized_note[:50]}...")  # Print first 50 chars
                                note_textarea.send_keys(personalized_note)
                                time.sleep(.5)  # Add delay after typing
                                print("Successfully entered message")
                            except Exception as e:
                                print(f"Error filling note: {str(e)}")
                                try:
                                    print("Trying alternative method to find textarea...")
                                    note_textarea = self.driver.find_element(By.CSS_SELECTOR, "textarea#custom-message")
                                    note_textarea.clear()
                                    time.sleep(.5)
                                    note_textarea.send_keys(personalized_note)
                                except Exception as e2:
                                    print(f"Error with alternative textarea method: {str(e2)}")
                                    self.highlight_element(li_element, "lightcoral")
                                    continue
                            
                            # Click send button
                            try:
                                print("Waiting for 'Send' button...")
                                send_button = self.wait.until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH, "//button[.//span[text()='Envoyer']]")
                                    )
                                )
                                print("Found 'Send' button, attempting to click...")
                                time.sleep(.5)  # Add delay before clicking
                                if not self.click_button_safely(send_button, "Envoyer"):
                                    raise Exception("Failed to click send button")
                                print("Successfully clicked 'Send' button")
                                time.sleep(.5)  # Add delay after sending
                            except Exception as e:
                                print(f"Error clicking send button: {str(e)}")
                                try:
                                    print("Trying alternative method to find 'Send' button...")
                                    send_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Envoyer maintenant']")
                                    if not self.click_button_safely(send_button, "Envoyer"):
                                        raise Exception("Failed to click send button (alternative method)")
                                except Exception as e2:
                                    print(f"Error with alternative send method: {str(e2)}")
                                    self.highlight_element(li_element, "lightcoral")
                                    continue
                            
                            print(f"Connection request {i} sent successfully")
                            self.highlight_element(li_element, "lightgreen")
                            successful_requests += 1  # Increment counter for successful requests
                            print(f"Successfully sent {successful_requests} requests total")
                            if max_requests is not None:
                                print(f"Remaining requests: {max_requests - successful_requests}")
                            time.sleep(.5)
                            
                        except Exception as e:
                            print(f"Error sending connection request {i}: {str(e)}")
                            if 'li_element' in locals():
                                self.highlight_element(li_element, "lightcoral")
                            continue
                    
                    # Try to click next page button
                    try:
                        next_button = self.wait.until(
                            EC.element_to_be_clickable(
                                (By.XPATH, "//button[contains(@class, 'artdeco-pagination__button--next')]")
                            )
                        )
                        if not self.click_button_safely(next_button, "Suivant"):
                            print("Failed to click next button")
                            break
                        time.sleep(.5)
                        page_number += 1
                        
                    except TimeoutException:
                        print("No more pages to process")
                        break
                    except Exception as e:
                        print(f"Error navigating to next page: {str(e)}")
                        break
                        
                except TimeoutException:
                    print(f"No connect buttons found on page {page_number}, trying next page...")
                    try:
                        next_button = self.wait.until(
                            EC.element_to_be_clickable(
                                (By.XPATH, "//button[contains(@class, 'artdeco-pagination__button--next')]")
                            )
                        )
                        if not self.click_button_safely(next_button, "Suivant"):
                            print("Failed to click next button")
                            break
                        time.sleep(.5)
                        page_number += 1
                    except:
                        print("No more pages available")
                        break
        finally:
            # Save the count of successful requests before exiting
            print(f"\nTotal successful requests in this session: {successful_requests}")
            self.save_request_count(successful_requests)

    def close(self):
        """Close the browser"""
        self.driver.quit()

def main():
    # Your LinkedIn search URL (the page with search results)
   #search_url = "https://www.linkedin.com/search/results/people/?activelyHiringForJobTitles=%5B%22-100%22%5D&geoUrn=%5B%22105015875%22%5D&keywords=recruteur&origin=FACETED_SEARCH&sid=!!e"
    search_url = "https://www.linkedin.com/search/results/people/?activelyHiringForJobTitles=25201&sid=agt"
    #search_url = "https://www.linkedin.com/search/results/people/?activelyHiringForJobTitles=9&sid=7SI"
    # Your personalized connection note
    connection_note = """Bonjour,
Je suis un développeur fullstack certifié Spring et AEM, Je me permets de vous contacter pour savoir si vous avez des opportunités pour un poste de développeur backend.
Je vous invite à visiter mon CV: https://saber-almehdi.netlify.app
Merci et bonne journée !
"""

    # Maximum number of connection requests to send
    """ max_requests = None """  # You can adjust this number as needed
    max_requests = 100
    bot = LinkedInAutoConnect()
    try:
        """ bot.login() """
        bot.send_connection_requests(search_url, connection_note, max_requests=max_requests)
    finally:
        bot.close()

if __name__ == "__main__":
    main() 