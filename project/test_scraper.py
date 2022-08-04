import unittest
from numpy import place
from selenium import webdriver
from scraper import PremierLeagueScraper
from RDS import upload_to_sql
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PremierLeagueScraperTestCase(unittest.TestCase):
    def setUp(self):
        '''Opens the match results page in headless mode.'''
        self.options = Options()
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument("--disable-notifications")
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.pl = PremierLeagueScraper(driver=webdriver.Chrome(options=self.options))
        self.pl.club = 'Chelsea'  # Test
        self.pl.year = '2021/22'

    def test_select_season(self):
        '''Tests that the correct season has been selected from the dropdown menu.'''
        self.pl.driver.get(self.pl.URL)
        self.pl._accept_cookies()
        self.pl._close_ad()
        self.pl._select_season()
        self.pl._close_ad()
        year_selected = self.pl.driver.find_element(By.CSS_SELECTOR, '[aria-labelledby="dd-compSeasons"][role="button"]').get_attribute('textContent')
        self.assertEqual(self.pl.year, year_selected)
    
    def test_scroll_to_bottom(self):
        '''
        Tests to ensure the document height page does not change after the first scroll i.e. is already fully loaded.
        Tests the page lengths are the same to 2sf. 
        '''
        self.pl.driver.get(self.pl.URL)
        self.pl._accept_cookies()
        self.pl._scroll_to_bottom()
        height_1 = self.pl.driver.execute_script('return document.body.scrollHeight')
        self.pl._scroll_to_bottom()
        height_2 = self.pl.driver.execute_script('return document.body.scrollHeight')
        self.assertAlmostEqual(height_1/1000, height_2/1000, place==1)

    def test_get_fixture_link_list(self):
        '''Tests that the fixture list has the required 38 games.'''
        self.pl.driver.get(self.pl.URL)
        self.pl._accept_cookies()
        self.pl._select_season()
        self.pl._scroll_to_bottom()
        link_list = self.pl._get_fixture_link_list(38)
        self.assertEqual(len(link_list), 38)

    def test_split_stats_list(self):
        '''Tests the number of statistics remains the same after splitting and reconstructing.'''
        link = 'https://www.premierleague.com/match/66716'  # Test game
        self.pl.driver.get(link)
        self.pl._accept_cookies()
        WebDriverWait(self.pl.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//li[@data-tab-index="2"]'))).click()
        stats = self.pl._get_match_info(link)[2]
        split_stats = self.pl._split_stats_list(stats)
        self.assertEqual(len(split_stats), len(stats))

    def test_get_match_info(self):
        '''Tests that the method returns a list of 6 elements.'''
        link = 'https://www.premierleague.com/match/66716'  # Test game
        self.pl.driver.get(link)
        self.pl._accept_cookies()
        WebDriverWait(self.pl.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//li[@data-tab-index="2"]'))).click()
        self.assertEqual(len(self.pl._get_match_info(link)), 6)

    def test_create_dictionary(self):
        '''Tests the dictionary contains the correct number of statistics.'''
        link = 'https://www.premierleague.com/match/66716'  # Test game
        self.pl.driver.get(link)
        self.pl._accept_cookies()
        WebDriverWait(self.pl.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//li[@data-tab-index="2"]'))).click()
        stats_dict = self.pl._create_dictionary(
            self.pl._get_match_info(link),
            self.pl._split_stats_list(self.pl._get_match_info(link)[2])
            )
        self.assertEqual(len(stats_dict), 18)

    def test_upload_to_sql(self):
        '''Tests the panda uploaded contains 38 rows and 16 columns.'''
        df = upload_to_sql(self.pl.club, self.pl.year)
        self.assertEqual(df.shape, (38, 20))

    def tearDown(self):
        '''Closes the browers and deletes the test instance.'''
        self.pl.driver.quit()
        del self.pl


if __name__ == '__main__':
    unittest.main()
