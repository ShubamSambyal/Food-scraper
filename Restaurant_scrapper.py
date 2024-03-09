import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

class GrabFoodScraper:
    def __init__(self, url):
        self.url = url
        self.driver = webdriver.Chrome()
    #This function is responsible for searching the restaurant name, and then scraping the necessary data and then append the scraped data in .csv file
    def scrape_restaurants(self):
        self.driver.get(self.url)
        
        
        location = "PT Singapore - Choa Chu Kang North 6, Singapore, 689577"
        self.enter_location(location)
        
        
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-col-24.RestaurantListCol___1FZ8V")))
        
        
        self.scroll_to_bottom()

        
        restaurants = []
        try:
            restaurant_cards = self.driver.find_elements(By.CSS_SELECTOR, ".ant-col-24.RestaurantListCol___1FZ8V")
            for card in restaurant_cards:
                restaurant_info = {}
                
                
                restaurant_info['name'] = self.get_text(card, ".name___2epcT")
                
                
                restaurant_info['cuisine'] = self.get_text(card, ".cuisine___T2tCh")
                
                
                restaurant_info['rating'] = self.get_text(card, ".ant-rate-text")
                
                
                delivery_info = self.get_delivery_info(card)
                restaurant_info['delivery_time'] = delivery_info[0]
                restaurant_info['distance'] = delivery_info[1]

                
                lat_lng = self.get_lat_lng(card)
                restaurant_info['latitude'] = lat_lng[0]
                restaurant_info['longitude'] = lat_lng[1]

                
                restaurant_info['id'] = self.get_restaurant_id(card)
                
                
                restaurants.append(restaurant_info)
        except Exception as e:
            print(f"An error occurred while scraping: {str(e)}")
        
        return restaurants

    def get_text(self, element, selector):
        try:
            return element.find_element(By.CSS_SELECTOR, selector).text.strip()
        except NoSuchElementException:
            return "N/A"

    def get_delivery_info(self, element):
        try:
            delivery_info = element.find_elements(By.CSS_SELECTOR, ".numbers___2xZGn .numbersChild___2qKMV")
            return delivery_info[1].text.strip().split(' • ')
        except (NoSuchElementException, IndexError):
            return "N/A", "N/A"

    def get_lat_lng(self, element):
           try:
                latitude = element.find_element(By.CSS_SELECTOR, ".merchant-latlng")
                latitude = latitude.get_attribute("data-lat")
                longitude = element.find_element(By.CSS_SELECTOR, ".merchant-latlng")
                longitude = longitude.get_attribute("data-lng")
                return latitude, longitude
           except NoSuchElementException:
                return "N/A" , "N/A"

    def get_restaurant_id(self, element):
        try:
            url = element.find_element(By.XPATH, ".//a[contains(@href, '/sg/en/restaurant')]").get_attribute('href')
            return url.split("/")[-1]
        except NoSuchElementException:
            return "N/A"

    def enter_location(self, location):
        location_input = self.driver.find_element(By.ID, 'location-input')
        location_input.click()
        time.sleep(5)
        location_input.clear()
        location_input.send_keys(location)
        submit_button = self.driver.find_element(By.CSS_SELECTOR, '.ant-btn.submitBtn___2roqB.ant-btn-primary')
        submit_button.click()

    def scroll_to_bottom(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def save_to_csv(self, data, filename):
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

    def close_driver(self):
        self.driver.quit()


if __name__ == "__main__":
    url = "https://food.grab.com/sg/en"
    scraper = GrabFoodScraper(url)
    restaurant_data = scraper.scrape_restaurants()
    scraper.save_to_csv(restaurant_data, "restaurant_data_with_id1.csv")
    scraper.close_driver()
