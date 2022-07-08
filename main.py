from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import uuid
import os
import json


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
    pause_time: int
        the amount of time in seconds between each action

    Methods
    -------
    # says(sound=None)
    #     Prints the animals name and what sound it makes
    """
    '''
    def __init__(self, driver, URL, pause_time):
        self.driver = driver
        self.URL = URL
        self.pause_time = pause_time


    def open_page(self, link):
        '''Opens URL'''
        self.driver.get(link)


    def accept_cookies(self):
        '''Accepts all cookies if cookie window appears. Does nothing if no window.'''
        sleep(self.pause_time+2)
        try:
            accept_cookies_button = self.driver.find_element(By. XPATH, '//*[@class="_2hTJ5th4dIYlveipSEMYHH BfdVlAo_cgSVjDUegen0F js-accept-all-close"]')
            accept_cookies_button.click()
        except:
            pass # If there is no cookies button, pass


    def scroll_to_bottom(self):
        '''Scrolls to bottom of any page.'''
        last_height = self.driver.execute_script('return document.body.scrollHeight')
        new_height = None
        while last_height != new_height:
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(self.pause_time)
            new_height = self.driver.execute_script('return document.body.scrollHeight')
            last_height = new_height

    
    def get_fixture_link_list(self):
        '''Retrieves the href links to each match and stores them in a list.'''
        sleep(self.pause_time)
        fixture_list = self.driver.find_element(By.XPATH, '//section[@class="fixtures"]')
        home_games = fixture_list.find_elements(By.XPATH, '//li[@data-home="Chelsea"]')
        away_games = fixture_list.find_elements(By.XPATH, '//li[@data-away="Chelsea"]')
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
        print(link_list)
        return link_list

    
    def home_or_away(self):
        '''Returns 'Home' or 'Away' depending on location of game.'''
        score_container = self.driver.find_element(By.XPATH, '//div[@class="scoreboxContainer"]')
        home_container = score_container.find_element(By.XPATH, '//div[contains(@class, "team home")]')
        home_team = home_container.find_element(By.CSS_SELECTOR, 'span.long').text
        if home_team == 'Chelsea':
            return 'Home'
        else:
            return 'Away'


    def get_result(self):
        '''Returns Win, Loss or Draw depending on the score.'''
        sleep(self.pause_time)
        home_or_away = self.home_or_away()
        score = self.driver.find_element(By.XPATH, '//div[@class="score fullTime"]').text # 'home_score - away_score'
        home_score = int(score[0])
        away_score = int(score[2])
        if home_or_away == 'Home' and home_score > away_score:
            return [home_score, away_score, 'Win']
        elif home_or_away == 'Away' and away_score > home_score:
            return [home_score, away_score, 'Win']
        elif home_score == away_score:
            return [home_score, away_score, 'Draw']
        else:
            return [home_score, away_score, 'Loss']


    def click_stats(self):
        '''Clicks on the stas tab to reveal the page from which the data is scraped.'''
        stats_tab = self.driver.find_element(By.XPATH, '//li[@data-tab-index="2"]')
        stats_tab.click()

    
    def get_match_location(self):
        '''Return the name and location of the stadium played at.'''
        stadium = self.driver.find_element(By.XPATH, '//div[@class="stadium"]')
        return stadium.text

    
    def get_match_date(self):
        'Returns the date of the fixture in datetime.'
        date_str = self.driver.find_element(By.XPATH, '//div[@class="matchDate renderMatchDateContainer"]').text
        return(date_str)


    def get_stats(self):
        '''Returns Chelsea's match statistics in a list.'''
        sleep(self.pause_time)
        stats_table = self.driver.find_element(By.XPATH, '//tbody[@class="matchCentreStatsContainer"]')
        return stats_table.find_elements(By.TAG_NAME, 'tr')

    
    def split_stats_list(self, stats_list):
        '''Splits the stats list into individual stats.'''
        possession = stats_list[0].text.split()         # ['home_posession', 'Possession', '%', 'away_possession']
        shots_ontarget = stats_list[1].text.split()     # ['home_shots_ontarger', 'Shots', 'on', 'target', 'away_shots_ontarget']
        shots = stats_list[2].text.split()              # ['home_shots', 'Shots', 'away_shots']
        touches = stats_list[3].text.split()            # ['home_touches', 'Shots', 'away_touches'] 
        passes = stats_list[4].text.split()             # ['home_passes', 'Passes', 'away_passes']
        tackles = stats_list[5].text.split()            # ['home_tackles', 'Tackles', 'away_tackles']
        clearances = stats_list[6].text.split()         # ['home_clearances', 'Clearances', 'away_clearances']
        corners = stats_list[7].text.split()            # ['home_corners', 'Corners', 'away_corners']
        fouls_conceeded = stats_list[-1].text.split()   # ['home_fouls_conceeded', 'Fouls', 'conceeded', 'away_fouls_conceeded']
        if len(stats_list) == 9:
            stats_reconstructed = [possession, shots_ontarget, shots, touches, passes, tackles,
                                   clearances, corners, fouls_conceeded]
        elif len(stats_list) == 10:
            offsides = stats_list[-2].text.split()      # ['home_offsides', 'Offsides', 'away_offsides']
            stats_reconstructed = [possession, shots_ontarget, shots, touches, passes, tackles,
                                   clearances, corners, offsides, fouls_conceeded]
        elif len(stats_list) == 11: # offsides/yellow/red cards not included in stats_list if 0 for each team
            offsides = stats_list[-3].text.split()      # ['home_offsides', 'Offsides', 'away_offsides']
            yellow_cards = stats_list[-2].text.split()  # ['home_yellow_cards', 'Yellow', 'cards', 'away_yellow_cards']
            stats_reconstructed = [possession, shots_ontarget, shots,  touches, passes, tackles,
                                   clearances, corners, offsides, fouls_conceeded, yellow_cards]
        elif len(stats_list) == 12:
            offsides = stats_list[-4].text.split()  
            yellow_cards = stats_list[-3].text.split()
            red_cards = stats_list[-2].text.split()     # ['home_red_cards', 'Red', 'cards', 'away_red_cards']
            stats_reconstructed = [possession, shots_ontarget, shots,  touches, passes, tackles,
                                   clearances, corners, offsides, fouls_conceeded, yellow_cards, red_cards]
        print(stats_reconstructed)
        return stats_reconstructed

    
    def get_match_id(self, URL):
        match_id = int(URL[-5:])
        return match_id


    def generate_uuid(self):
        '''Generates a random UUID.'''
        return uuid.uuid4()


    def create_dictionary(self, match_id, date, location, home_or_away, result, stat_list):
        '''Creates the unique dictionary with all the information needed for each game.'''
        if home_or_away == 'Home':
            stats_dictionary = {'Match ID': match_id,
                                'V4 UUID': str(self.generate_uuid()),
                                'Date': date,
                                'Location': location,
                                'Home or Away': home_or_away,
                                'Result': result[2],
                                'Goals scored': result[0],
                                'Goals against': result[1],
                                'Possession': float(stat_list[0][0]),
                                'Shots on target': int(stat_list[1][0]),
                                'Shots': int(stat_list[2][0]),
                                'Touches': int(stat_list[3][0]),
                                'Passes': int(stat_list[4][0]),
                                'Tackles': int(stat_list[5][0]),
                                'Clearances': int(stat_list[6][0]),
                                'Corners': int(stat_list[7][0]),
                                'Offsides': int(stat_list[8][0]),
                                'Fouls conceeded': int(stat_list[-1][0])}
        else:
            stats_dictionary = {'Match ID': match_id,
                                'V4 UUID': str(self.generate_uuid()),
                                'Date': date,
                                'Location': location,
                                'Home or Away': home_or_away,
                                'Result': result[2],
                                'Goals scored': result[1],
                                'Goals against': result[0],
                                'Possession': float(stat_list[0][3]),
                                'Shots on target': int(stat_list[1][4]),
                                'Shots': int(stat_list[2][2]),
                                'Touches': int(stat_list[3][2]),
                                'Passes': int(stat_list[4][2]),
                                'Tackles': int(stat_list[5][2]),
                                'Clearances': int(stat_list[6][2]),
                                'Corners': int(stat_list[7][2]),
                                'Offsides': int(stat_list[8][2]),
                                'Fouls conceeded': int(stat_list[-1][3])}
        return stats_dictionary

    
    def save_data(self, match_id, raw_stats):
        path = f'/Users/asadiceccarelli/Documents/AiCore/Data-Collection-Pipeline/raw_data/{match_id}'
        if not os.path.exists(path):
            os.makedirs(path)
        json_str = json.dumps(raw_stats)
        with open(f'{path}/data.json', 'w') as outfile:
            outfile.write(json_str)

    
    def scrape_links(self):
        self.open_page(self.URL)
        self.accept_cookies()
        self.scroll_to_bottom()
        self.get_fixture_link_list()
        
        

    def scrape_stats(self, link):
        self.open_page(link)
        self.accept_cookies()
        self.click_stats()
        dict = self.create_dictionary(self.get_match_id(link),
                               self.get_match_date(),
                               self.get_match_location(),
                               self.home_or_away(),
                               self.get_result(),
                               self.split_stats_list(self.get_stats()))
        self.save_data(self.get_match_id(link), dict)

    
    def iterate_links(self, link_list):
        for link in link_list:
            self.scrape_stats(f'https:{link}')

    def close_browser(self):
        '''Closes brower after all tasks are completed.'''
        sleep(self.pause_time)
        self.driver.quit()
       

    def run_crawler(self):
        self.scrape_links()
        self.iterate_links(self.get_fixture_link_list())
        self.close_browser()
        


if __name__ == '__main__':
    premierleague = Scraper(driver=webdriver.Chrome(),
                            URL='https://www.premierleague.com/results?co=1&se=418&cl=-1',
                            pause_time=1)
    premierleague.run_crawler()


