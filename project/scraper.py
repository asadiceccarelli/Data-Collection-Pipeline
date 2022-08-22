from multiprocessing.sharedctypes import Value
import os
import sys
import logging
import uuid
import json
import boto3
import RDS
import valid_inputs
from graphs import CreateGraph
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

logging.basicConfig(level = logging.INFO)


class PremierLeagueScraper:
    '''
    This class is used to scrape the match stats of a particular club from the Premier League season 2021/22.

    Attributes
    ----------
    driver (class): The webdriver to be used.
    club (str): The Premier League club to be inspected.
    URL (str): The URL of the 2021/22 results page from the official Premier League website.
    '''

    def __init__(self, driver):
        self.driver = driver
        self.URL = 'https://www.premierleague.com/results'

    def _user_inputs(self):
        '''Sets user inputs as environment variables.'''
        self.club = os.environ['club']
        self.year = os.environ['season']
    
    def _accept_cookies(self):
        '''Wait for window and accepts all cookies. Does nothing if no window.'''
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                'button[class^="_2hTJ5th4dIYlveipSEMYHH BfdVlAo_cgSVjDUegen0F"]'))).click()
            logging.info('Cookies accepted.')
        except TimeoutException:
            logging.info('No cookies to be accepted.')
            pass

    def _close_ad(self):
        '''Closes ad if ad window appears. Does nothing if no ad.'''
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[class="closeBtn"]'))).click()
            logging.info('Ad closed.')
        except TimeoutException:
            pass

    def _select_season(self):
        '''Selects the correct season to be inspected'''
        logging.info('Selecting season...')
        self._accept_cookies()
        self._close_ad()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
            '[aria-labelledby="dd-compSeasons"][role="button"]'))).click()
        desired_season = self.driver.find_element(By. XPATH,
            f'//*[@id="mainContent"]/div[3]/div[1]/section/div[3]/ul/li[contains(text(),"{self.year}")]')
        actions = ActionChains(self.driver)
        actions.move_to_element(desired_season).perform()
        desired_season.click()

    def _scroll_to_bottom(self):
        '''Selects the correct season and scrolls down the page slowly to ensure all fixtures loaded.'''
        logging.info('Scrolling to bottom of the page...')
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="mainContent"]/div[3]/div[1]/div[2]/section')))
        self._close_ad()
        for i in range(1, 37000, 5):  # 37000 length of page, scrolls 5 at a time
                self.driver.execute_script("window.scrollTo(0, {});".format(i))
    
    def _get_fixture_link_list(self, correct_no_fixtures):
        '''
        Retrieves the href links to each match and stores them in a list.
        
        Returns:
            list: A list of all the URLs to each match the club has played over the course of the season.
        '''
        logging.info('Getting fixture links...')
        link_list = []
        while len(link_list) != correct_no_fixtures:
            link_list = []
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@class="fixtures__matches-list"]')))
            fixture_list = self.driver.find_element(By.CSS_SELECTOR, 'section[class="fixtures"]')
            home_games = fixture_list.find_elements(By.CSS_SELECTOR, f'li[data-home="{self.club}"]')
            away_games = fixture_list.find_elements(By.CSS_SELECTOR, f'li[data-away="{self.club}"]')
            game_list = home_games + away_games
            for game in game_list:
                link_class = game.find_element(By.XPATH, "./div")
                link = link_class.get_attribute('data-href')
                link_list.append(link)
            if len(link_list) == correct_no_fixtures:
                logging.info(f'All {correct_no_fixtures} fixtures in list.')
                return link_list
            elif len(link_list) == 0:
                logging.error(f'This club was not in the premier league during the {self.year} season.')
                self.driver.quit()
                sys.exit()
            logging.error(f'{len(link_list)} fixtures in list. There should be {correct_no_fixtures}.')
            self.driver.refresh()
            self._close_ad()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[class="fixtures__matches-list"]')))
            self._scroll_to_bottom()
            return link_list
    
    def _get_match_info(self, link):
        '''
        Extracts the date, name and location of the stadium played at, statistics, result and match ID from the stats page.

        Returns:
            list: Date in datetime format (%a %d %b %Y) as a string, stadium as a string, stats_list as a list.
        '''
        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[class^="matchDate renderMatchDateContainer"]')))
        date_str = self.driver.find_element(By.CSS_SELECTOR, 'div[class^="matchDate renderMatchDateContainer"]').text
        stadium = self.driver.find_element(By.CSS_SELECTOR, 'div[class="stadium"]').text

        stats_table = self.driver.find_element(By.CSS_SELECTOR, 'tbody[class="matchCentreStatsContainer"]')
        stats_list = stats_table.find_elements(By.TAG_NAME, 'tr')
        info = [date_str, stadium, stats_list]

        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[class="scoreboxContainer"]')))
        score_container = self.driver.find_element(By.CSS_SELECTOR, 'div[class="scoreboxContainer"]')
        home_container = score_container.find_element(By.CSS_SELECTOR, 'div[class="team home"]')
        home_team_short = home_container.find_element(By.CSS_SELECTOR, 'span[class="short"]').get_attribute('textContent')  # get_attribute as element is not visible
        
        score = self.driver.find_element(By.XPATH, '//div[@class="score fullTime"]').text # 'home_score - away_score'
        home_score = int(score[0])
        away_score = int(score[2])
        
        if home_team_short == f'{valid_inputs.valid_clubs()[self.club]}':
            home_or_away = 'Home'
        else:
            home_or_away = 'Away'
        info.append(home_or_away)

        if (home_or_away == 'Home' and home_score > away_score) or (home_or_away == 'Away' and away_score > home_score):
            info.append([home_score, away_score, 'Win'])
        elif home_score == away_score:
            info.append([home_score, away_score, 'Draw'])
        else:
            info.append([home_score, away_score, 'Loss'])

        match_id = f'{link[-5:]}-{valid_inputs.valid_clubs()[self.club]}'
        info.append(match_id)

        return info

    def _split_stats_list(self, stats_list):
        '''
        Splits the stats list into the a list conatining only the stats of the club being inspects.
        
        Args:
            stats_list (list): The list of all match statistics of both teams.

        Returns:
            list: In format [home_stat, away_stat, 'stat name']
        '''
        stats_reconstructed = []
        for stat in stats_list:
            stat_split = stat.text.split()
            stat_h = [stat_split[0]]
            stat_a = [stat_split[-1]]
            stat_name = [stat_split[1:-1]]
            stats_reconstructed.append(stat_h + stat_a + stat_name)
        return stats_reconstructed        

    def _create_dictionary(self, info, stats_list):
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
                'Match id': info[5],
                'V4 uuid': str(uuid.uuid4()),
                'Date': info[0],
                'Location': info[1],
                'Home or away': info[3],
                'Result': info[4][2]
        }
        if info[3] == 'Home':
            stats_dict['Goals scored'] = info[4][0]
            stats_dict['Goals against'] = info[4][1]
            for i in range(len(stats_list)):
                stat_name = ' '.join(stats_list[i][2])
                stats_dict[stat_name] = stats_list[i][0]
        else:
            stats_dict['Goals scored'] = info[4][1]
            stats_dict['Goals against'] = info[4][0]
            for i in range(len(stats_list)):
                stat_name = ' '.join(stats_list[i][2])
                stats_dict[stat_name] = stats_list[i][1]       
        return stats_dict

    def save_data_aws(self, match_id, raw_stats):
        '''
        Saves the dictionary of information in an AWS S3 bucket in the cloud, named after the match ID.
        Args:
            match_id (int): The unique ID of each match.
        '''
        s3_client = boto3.client(
            's3',
            region_name = 'eu-west-2',
            aws_access_key_id = os.environ['aws_access_key_id'],
            aws_secret_access_key = os.environ['aws_secret_access_key']          
            )
        json_str = json.dumps(raw_stats)
        s3_client.put_object(Bucket='premier-league-bucket', Key=match_id, Body=(bytes(json_str, encoding='utf-8')))
        logging.info(f'{match_id} saved to AWS S3 bucket.')

    def _scrape_links(self):
        '''Gets the list of links of all 38 fixtures of the club being inspected.'''
        self._accept_cookies()
        self._close_ad()
        self._select_season()
        self._scroll_to_bottom()
        seasons_with_22_teams = ['1992/93', '1993/94', '1994/95']
        if self.year in seasons_with_22_teams:
            correct_no_fixtures = 42
        else:
            correct_no_fixtures = 38
        return self._get_fixture_link_list(correct_no_fixtures)
          
    def _scrape_stats(self, link):
        '''Scrapes the statistics from each match and stores in a .json file
        
        Args:
            link (str): The URL of the fixture to be inspected.
        '''
        self.driver.get(link)
        logging.info(f'Scraping stats from {self._get_match_info(link)[5]}...')
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//li[@data-tab-index="2"]'))).click()
        dict = self._create_dictionary(
            self._get_match_info(link),
            self._split_stats_list(self._get_match_info(link)[2])
            )
        match_id = self._get_match_info(link)[5]
        self.save_data_aws(match_id, dict)

    def _display_graphs(self):
        '''Displays the graphs created in the CreateGraph class in the graph.py file.'''
        logging.info('Displaying graphs...')
        try:
            CreateGraph(self.club, self.year).show_graphs()
        except ValueError:
            logging.error('ValueError: This is probably because full match data is not available for seasons prior to 2006/07.')
            sys.exit()

    def run_crawler(self):
        '''Gets the list of 38 links to each fixture, goes through them one by one and extracts all the data required.'''
        self._user_inputs()
        if f'{self.club}-{self.year[-5:-3]}{self.year[-2:]}' not in RDS._prevent_rescraping():
            self.driver.get(self.URL)
            for link in self._scrape_links():
                self._scrape_stats(f'https:{link}')
            RDS.upload_to_sql(self.club, self.year)
            self._display_graphs()
            self.driver.quit()
            logging.info('Program successfully finished.')
        else:
            logging.warning('RDS database already contains data on this club from this season.')
            self._display_graphs()
            self.driver.quit()
            logging.info('Program successfully finished.')
    

if __name__ == '__main__':
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument('--window-size=1920,1080')
    options.add_argument("--disable-notifications")
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    premierleague = PremierLeagueScraper(driver=webdriver.Chrome(options=options))
    premierleague.run_crawler()
