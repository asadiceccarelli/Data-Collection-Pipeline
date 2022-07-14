import unittest
from time import sleep
from selenium import webdriver
from project import PremierLeagueScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PremierLeagueScraperTestCase(unittest.TestCase):
    def setUp(self):
        '''Opens the match results page and accepts cookies.'''
        self.pl = PremierLeagueScraper(driver=webdriver.Chrome(),
            club='Chelsea')
    
    def test_scroll_to_bottom(self):
        '''Tests to see if the document has been fully loaded from scrolling to the bottom.'''
        self.pl.driver.get(self.pl.URL)
        self.pl.accept_cookies()
        self.pl.scroll_to_bottom()
        height_1 = self.pl.driver.execute_script('return document.body.scrollHeight')
        self.pl.scroll_to_bottom()
        height_2 = self.pl.driver.execute_script('return document.body.scrollHeight')
        self.assertEqual(height_1, height_2)

    def test_get_fixture_link_list(self):
        '''Tests that the fixture list has the required 38 games.'''
        self.pl.driver.get(self.pl.URL)
        self.pl.accept_cookies()
        self.pl.scroll_to_bottom()
        link_list = self.pl.get_fixture_link_list()
        self.assertEqual(len(link_list), 38)

    def test_split_stats_list(self):
        '''Tests the number of statistics remains the same after splitting and reconstructing.'''
        self.pl.driver.get('https://www.premierleague.com/match/66716')  # Test game
        self.pl.accept_cookies()
        WebDriverWait(self.pl.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//li[@data-tab-index="2"]'))).click()
        stats = self.pl.get_match_info()[2]
        split_stats = self.pl.split_stats_list(stats)
        self.assertEqual(len(split_stats), len(stats))

    def test_home_or_away(self):
        '''Tests that the method returns a string ('Home' or 'Away').'''
        self.pl.driver.get('https://www.premierleague.com/match/66716')  # Test game
        self.pl.accept_cookies()
        WebDriverWait(self.pl.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//li[@data-tab-index="2"]'))).click()
        self.assertEqual(type(self.pl.home_or_away()), str)

    def test_get_result(self):
        '''Tests that the method returns a list e.g. [2, 1, 'Win'].'''
        self.pl.driver.get('https://www.premierleague.com/match/66716')  # Test game
        self.pl.accept_cookies()
        WebDriverWait(self.pl.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//li[@data-tab-index="2"]'))).click()
        result = self.pl.get_result(self.pl.home_or_away())
        self.assertEqual(type(result), list)

    def test_get_match_info(self):
        '''Tests that the method returns a list of 3 elements.'''
        self.pl.driver.get('https://www.premierleague.com/match/66716')  # Test game
        self.pl.accept_cookies()
        sleep(1)
        WebDriverWait(self.pl.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//li[@data-tab-index="2"]'))).click()
        self.assertEqual(len(self.pl.get_match_info()), 3)

    def test_get_match_id(self):
        '''Tests that the method returns the match ID as a 9 character string.'''
        match_id = self.pl.get_match_id('https://www.premierleague.com/match/66716')  # Test game
        self.assertEqual(len(str(match_id)), 9)

    def test_create_dictionary(self):
        '''Tests the dictionary contains the right number of statistics.'''
        URL = 'https://www.premierleague.com/match/66716'  # Test game
        self.pl.driver.get(URL)
        self.pl.accept_cookies()
        WebDriverWait(self.pl.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//li[@data-tab-index="2"]'))).click()
        stats_dict = self.pl.create_dictionary(
            self.pl.get_match_id(URL),
            self.pl.get_match_info(),
            self.pl.home_or_away(),
            self.pl.get_result(self.pl.home_or_away()),
            self.pl.split_stats_list(self.pl.get_match_info()[2])
            )
        self.assertEqual(len(stats_dict), 16)

    def tearDown(self):
        '''Closes the browers and deletes the test instance.'''
        self.pl.driver.quit()
        del self.pl


if __name__ == '__main__':
    unittest.main()
