from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LinkedInAutoConnect:
    def __init__(self):
        self.driver = webdriver.Chrome()  # Make sure you have ChromeDriver installed
        self.wait = WebDriverWait(self.driver, 5)  # Reduced from 10 to 5 seconds
        
    def login(self):
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
        
        # Wait for login to complete
        time.sleep(3)  # Reduced from 5 to 3 seconds

    def scroll_to_element(self, element):
        """Scroll element into view and wait a bit"""
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)

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

    def send_connection_requests(self, search_url, connection_note):
        """Send connection requests to people from search results"""
        self.driver.get(search_url)
        time.sleep(3)
        
        page_number = 1
        while True:
            print(f"\nProcessing page {page_number}")
            
            # Set zoom to 75%
            self.set_page_zoom(75)
            time.sleep(1)
            
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
                        time.sleep(2)
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
                        
                        # Find the parent li element
                        li_element = connect_button.find_element(By.XPATH, "./ancestor::li[contains(@class, 'YqPvchDpIQAtSkXEsugKtLYEYIOEbePc')]")
                        
                        # Highlight the current profile card in yellow
                        original_style = self.highlight_element(li_element, "yellow")
                        
                        # Try to click the connect button with our safe click method
                        if not self.click_button_safely(connect_button, "Se connecter"):
                            print(f"Failed to click connect button for connection {i}")
                            self.highlight_element(li_element, "lightcoral")
                            continue
                        
                        time.sleep(1)
                        
                        # Click "Add note" button
                        try:
                            add_note_button = self.wait.until(
                                EC.element_to_be_clickable(
                                    (By.XPATH, "//button[.//span[text()='Ajouter une note']]")
                                )
                            )
                            if not self.click_button_safely(add_note_button, "Ajouter une note"):
                                raise Exception("Failed to click add note button")
                        except Exception as e:
                            print(f"Error clicking add note button: {str(e)}")
                            self.highlight_element(li_element, "lightcoral")
                            continue
                        
                        # Find and fill the note textarea
                        try:
                            note_textarea = self.wait.until(
                                EC.presence_of_element_located(
                                    (By.ID, "custom-message")
                                )
                            )
                            note_textarea.clear()
                            time.sleep(0.5)
                            note_textarea.send_keys(connection_note)
                            time.sleep(0.5)
                        except Exception as e:
                            print(f"Error filling note: {str(e)}")
                            self.highlight_element(li_element, "lightcoral")
                            continue
                        
                        # Click send button
                        try:
                            send_button = self.wait.until(
                                EC.element_to_be_clickable(
                                    (By.XPATH, "//button[.//span[text()='Envoyer']]")
                                )
                            )
                            if not self.click_button_safely(send_button, "Envoyer"):
                                raise Exception("Failed to click send button")
                        except Exception as e:
                            print(f"Error clicking send button: {str(e)}")
                            self.highlight_element(li_element, "lightcoral")
                            continue
                        
                        print(f"Connection request {i} sent successfully")
                        self.highlight_element(li_element, "lightgreen")
                        time.sleep(1)
                        
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
                    time.sleep(2)
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
                    time.sleep(2)
                    page_number += 1
                except:
                    print("No more pages available")
                    break
    
    def close(self):
        """Close the browser"""
        self.driver.quit()

def main():
    # Your LinkedIn search URL (the page with search results)
    search_url = "https://www.linkedin.com/search/results/people/?keywords=recruteur&network=%5B%22S%22%2C%22O%22%5D&origin=GLOBAL_SEARCH_HEADER&sid=*6v"
    
    # Your personalized connection note
    connection_note = """Bonjour
Je me permets de vous contacter pour savoir si vous avez actuellement des opportunités pour un poste de développeur junior fullstack frontend ou backend. Je suis motivé, curieux, et prêt à apprendre au sein d'une équipe dynamique.
Merci d'avance pour votre retour,
Cordialement
Al Mehdi SABER"""
    
    bot = LinkedInAutoConnect()
    try:
        bot.login()
        bot.send_connection_requests(search_url, connection_note)
    finally:
        bot.close()

if __name__ == "__main__":
    main() 