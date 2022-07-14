import os
import uuid
import json
import boto3
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Headless mode

class PremierLeagueScraper:
    '''
    This class is used to scrape the match stats of a particular club from the Premier League season 2021/22.

    Attributes
    ----------
    driver (class): The webdriver to be used.
    club (str): The Premier League club to be inspected.
    URL (str): The URL of the 2021/22 results page from the official Premier League website.
    '''
    def __init__(self, driver, club):
        self.driver = driver
        self.club = club.capitalize()
        self.URL = 'https://www.premierleague.com/results?co=1&se=418&cl=-1'
        self.driver.implicitly_wait(5)

    def accept_cookies(self):
        '''Wait for window and accepts all cookies. Does nothing if no window.'''
        try:
            accept_cookies_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                '//*[@class="_2hTJ5th4dIYlveipSEMYHH BfdVlAo_cgSVjDUegen0F js-accept-all-close"]')))
            accept_cookies_button.click()
        except:
            pass # If there are no cookies.

    def close_ad(self):
        '''Closes ad if window appears. Does nothing if no ad.'''
        try:
            close_ad_button = self.driver.find_element(By. XPATH, '//*[@class="closeBtn"]')
            close_ad_button.click()
        except:
            pass # If there is no ad.

    def scroll_to_bottom(self): # C.presence_of_element_located
        '''Scrolls to 14/15ths of the way down the page, multiple times, to ensure all fixtures loaded.'''
        sleep(2)
        self.close_ad()
        i = 0
        while i < 5:
            self.driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight*14/15)")
            sleep(2)
            i += 1

    def get_fixture_link_list(self):
        '''
        Retrieves the href links to each match and stores them in a list.
        
        Returns:
            list: A list of all the URLs to each match the club has played over the course of the season.
        '''
        link_list = []
        while len(link_list) != 38:
            link_list = []
            fixture_list = self.driver.find_element(By.XPATH, '//section[@class="fixtures"]')
            home_games = fixture_list.find_elements(By.XPATH, f'//li[@data-home="{self.club}"]')
            away_games = fixture_list.find_elements(By.XPATH, f'//li[@data-away="{self.club}"]')
            game_list = home_games + away_games
            for game in game_list:
                link_class = game.find_element(By.XPATH, "./div")
                link = link_class.get_attribute('data-href')
                link_list.append(link)
            if len(link_list) != 38:
                print(f'ERROR: {len(link_list)} fixtures in list. There should be 38.')
                self.driver.refresh()
                sleep(5)
                self.close_ad()
                sleep(1)
                self.scroll_to_bottom()
            else:
                print('All 38 fixtures in list.')
                return link_list

    def home_or_away(self):
        '''
        Determines whether the game was played at home or away.
        
        Returns:
            str: 'Home' or 'Away'
        '''
        score_container = self.driver.find_element(By.XPATH, '//div[@class="scoreboxContainer"]')
        home_container = score_container.find_element(By.XPATH, '//div[contains(@class, "team home")]')
        home_team = home_container.find_element(By.CSS_SELECTOR, 'span.long').text
        if home_team == f'{self.club}':
            return 'Home'
        else:
            return 'Away'

    def get_result(self, home_or_away):
        '''
        Understands the result from the score of the match.

        Returns:
            str: 'Win', 'Loss' or 'Draw'.
        '''
        score = self.driver.find_element(By.XPATH, '//div[@class="score fullTime"]').text # 'home_score - away_score'
        home_score = int(score[0])
        away_score = int(score[2])
        if (home_or_away == 'Home' and home_score > away_score) or (home_or_away == 'Away' and away_score > home_score):
            return [home_score, away_score, 'Win']
        elif home_score == away_score:
            return [home_score, away_score, 'Draw']
        else:
            return [home_score, away_score, 'Loss']
    
    def get_match_info(self):
        '''
        Extracts the date, name and location of the stadium played at and statistics from the stats page.

        Returns:
            list: Date in datetime format (%a %d %b %Y) as a string, stadium as a string, stats_list as a list.
        '''
        date_str = self.driver.find_element(By.XPATH, '//div[@class="matchDate renderMatchDateContainer"]').text
        stadium = self.driver.find_element(By.XPATH, '//div[@class="stadium"]').text
        stats_table = self.driver.find_element(By.XPATH, '//tbody[@class="matchCentreStatsContainer"]')
        stats_list = stats_table.find_elements(By.TAG_NAME, 'tr')
        info = [date_str, stadium, stats_list]
        return info

    def split_stats_list(self, stats_list):
        '''
        Splits the stats list into the a list conatining only the stats of the club being inspects.
        
        Args:
            stats_list (list): The list of all match statistics of both teams.

        Returns:
            # list: [
            #     Possession,
            #     Shots on target,
            #     Shots,
            #     Touches,
            #     Passes,
            #     Tackles,
            #     Clearances,
            #     Corners,
            #     Offsides,
            #     Fouls conceded (if any),
            #     Yellow cards (if any),
            #     Red cards (if any)
            #     ]
        '''
        stats_reconstructed = []
        for i in range(len(stats_list)):
            stat_split = stats_list[i].text.split()
            stat_h = [stat_split[0]]
            stat_a = [stat_split[-1]]
            stat_name = [stat_split[1:-1]]
            stats_reconstructed.append(stat_h + stat_a + stat_name)
        return stats_reconstructed

    def get_match_id(self, URL):
        '''
        Gets the unique match ID for each fixture.

        Args:
            URL (str): The URL of the match being inspected.

        Returns:
            int: Match ID.
        '''
        name_short = {
            'Arsenal': 'ARS',
            'Aston Villa': 'AVL',
            'Brentford': 'BRE',
            'Brighton': 'BHA',
            'Burnley': 'BUR',
            'Chelsea': 'CHE',
            'Crystal Palace': 'CRY',
            'Everton': 'EVE',
            'Leeds': 'LEE',
            'Leicester': 'LEI',
            'Liverpool': 'LIV',
            'Man City': 'MCI',
            'Man Utd': 'MUN',
            'Newcastle': 'NEW',
            'Norwich': 'NOR',
            'Southampton': 'SOU',
            'Tottenham': 'TOT',
            'Watford': 'WAT',
            'West Ham': 'WHU',
            'Wolves': 'WOL'
        }
        match_id = F'{URL[-5:]}-{name_short[self.club]}'
        return match_id

    def create_dictionary(self, match_id, info, home_or_away, result, stats_list):
        '''
        Creates the unique dictionary with all the information needed for each game.
        
        Args:
            match_id (int): The unique ID of each match.
            date (str): The string of the date in datetime format (%a %d %b %Y).
            location (str): The location of the stadium played at.
            home_or_away (str): 'Home' or 'Away' depending on the club inspected.
            result (str): 'Win' 'Loss' or 'Draw' depending on the score and the club inspected.
            stat_list (list): The list of statistics of only the club being inspected.

        Returns:
            dict
        '''
        stats_dict = {
                'Match ID': match_id,
                'V4 UUID': str(uuid.uuid4()),
                'Date': info[0],
                'Location': info[1],
                'Home or Away': home_or_away,
                'Result': result[2]
        }
        if home_or_away == 'Home':
            stats_dict['Goals scored']: result[0]
            stats_dict['Goals against']: result[1]
            for i in range(len(stats_list)):
                stat_name = ' '.join(stats_list[i][2])
                stats_dict[stat_name] = stats_list[i][0]
        else:
            stats_dict['Goals scored']: result[1]
            stats_dict['Goals against']: result[0]
            for i in range(len(stats_list)):
                stat_name = ' '.join(stats_list[i][2])
                stats_dict[stat_name] = stats_list[i][1]         
        return stats_dict

    def save_data_locally(self, match_id, raw_stats):
        '''
        Saves the dictionary of information locally  into a new directory named after the club and a sub-directory after the match ID.

        Args:
            match_id (int): The unique ID of each match.
            raw_stats (dict): The unique dictionary with all the information needed from the match.
        '''
        path = f'/Users/asadiceccarelli/Documents/AiCore/Data-Collection-Pipeline/raw_data/{self.club}/{match_id}'
        if not os.path.exists(path):
            os.makedirs(path)
        json_str = json.dumps(raw_stats)
        with open(f'{path}/data.json', 'w') as outfile:
            outfile.write(json_str)

    def save_data_aws(self, match_id):
        '''
        Saves the dictionary of information in an AWS S3 bucket in the cloud, named after the match ID.

        Args:
            match_id (int): The unique ID of each match.
        '''
        s3_client = boto3.client('s3')
        s3_client.upload_file(f'raw_data/{self.club}/{match_id}/data.json', 'premier-league-bucket', match_id)

    def scrape_links(self):
        '''Gets the list of links of all 38 fixtures of the club being inspected.'''
        self.driver.get(self.URL)
        self.accept_cookies()
        self.scroll_to_bottom()
        self.get_fixture_link_list()
          
    def scrape_stats(self, link):
        '''Scrapes the statistics from each match and stores in a .json file
        
        Args:
            link (str): The URL of the fixture to be inspected.
        '''
        self.driver.get(link)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//li[@data-tab-index="2"]'))).click()
        dict = self.create_dictionary(self.get_match_id(link),
                               self.get_match_info(),
                               self.home_or_away(),
                               self.get_result(self.home_or_away()),
                               self.split_stats_list(self.get_match_info()[2]))
        self.save_data_locally(self.get_match_id(link), dict)
        self.save_data_aws(self.get_match_id(link))
    
    def iterate_links(self, link_list):
        '''
        Goes through the links one by one and extracts the information needed.

        Args:
            link_list (list): A list of all 38 URLs corresponding to each fixture.
        '''
        for link in link_list:
            self.scrape_stats(f'https:{link}')
       
    def run_crawler(self):
        '''Gets the list of 38 links to each fixture, goes through them one by one and extracts all the data required.'''
        self.scrape_links()
        self.iterate_links(self.get_fixture_link_list())
        self.driver.quit()
        

if __name__ == '__main__':
    premierleague = PremierLeagueScraper(
        driver=webdriver.Chrome(),
        club = 'Chelsea'
        )
    premierleague.run_crawler()

