from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

class Scraper:
    '''
    """
    A class used to scrape the web.

    Attributes
    ----------
    driver : class
        the webdriver to be used
    URL : str
        the URL of the website to be scraped

    Methods
    -------
    says(sound=None)
        Prints the animals name and what sound it makes
    """
    '''
    def __init__(self, driver, URL, pause_time):
        self.driver = driver
        self.URL = URL
        self.pause_time = pause_time


    def count_occurences_items(list_of_items):
        """Given a list of items, count the occurences of each item in key-value pairs in a defaultdict.

        :param list_of_item: list of items
        :type list_of_item: list
        
        :return count_item_occurences: keys of item names and values being count of occurences in input list
        :type count_item_occurences: defaultdict
        """
    pass


    def open_page(self):
        '''Opens URL'''
        self.driver.get(self.URL)


    def accept_cookies(self):
        '''Accepts all cookies if cookie window appears. Does nothing if no window.'''
        try:
            sleep(self.pause_time)
            accept_cookies_button = self.driver.find_element(By. XPATH, '//*[@class="_2hTJ5th4dIYlveipSEMYHH BfdVlAo_cgSVjDUegen0F js-accept-all-close"]')
            accept_cookies_button.click()
        except:
            pass # If there is no cookies button, pass


    def scroll_to_bottom(self):
        '''Scrolls to bottom of any page.'''
        last_height = self.driver.execute_script('return document.body.scrollHeight')
        print(f'LH: {last_height}')
        new_height = None
        while last_height != new_height:
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(self.pause_time)
            new_height = self.driver.execute_script('return document.body.scrollHeight')
            print(f'NH: {new_height}')
            last_height = new_height

    
    def get_fixture_link_list(self):
        '''Retrieves the href links to each match and stores them in a list.'''
        sleep(self.pause_time)
        fixture_list = self.driver.find_element(By.XPATH, '//*[@class="fixtures"]')
        home_games = fixture_list.find_elements(By.XPATH, '//*[@data-home="Chelsea"]')
        away_games = fixture_list.find_elements(By.XPATH, '//*[@data-away="Chelsea"]')
        link_list = []
        for game in home_games:
            link_class = game.find_element(By.XPATH, "./div")
            link = link_class.get_attribute('data-href')
            link_list.append(link)
        for game in away_games:
            link_class = game.find_element(By.XPATH, "./div")
            link = link_class.get_attribute('data-href')
            link_list.append(link)
        if len(link_list) != 38:
            print(f'ERROR: Only {len(link_list)} fixtures in list.')
        else:
            print('All 38 fixtures in list.')


    def get_link_list():
        pass
    

    def click_statistics(self):
        pass


    def get_winner(self):
        pass


    def get_stats(self):
        pass

    
    def close_browser(self):
        self.driver.quit()

    
    def scrape_links(self):
        self.open_page()
        self.accept_cookies()
        self.scroll_to_bottom()
        self.get_fixture_link_list()
        #self.close_browser()


if __name__ == '__main__':
    premierleague = Scraper(driver=webdriver.Chrome(),
                            URL='https://www.premierleague.com/results?co=1&se=418&cl=-1',
                            pause_time=2)
    premierleague.scrape_links()
