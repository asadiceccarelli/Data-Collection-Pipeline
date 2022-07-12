import unittest
from selenium import webdriver
from project import PremierLeagueScraper

class PremierLeagueScraperTestCase(unittest.TestCase):
    def setUp(self):
        '''Opens the match results page and accepts cookies.'''
        self.pl = PremierLeagueScraper(driver=webdriver.Chrome(),
                            club = 'Chelsea',
                            URL='https://www.premierleague.com/results?co=1&se=418&cl=-1',
                            pause_time=2)
    
    def test_scroll_to_bottom(self):
        '''Tests to see if the document has been fully loaded from scrolling to the bottom.'''
        self.pl.open_page(self.pl.URL)
        self.pl.accept_cookies()
        self.pl.scroll_to_bottom()
        height_1 = self.pl.driver.execute_script('return document.body.scrollHeight')
        self.pl.scroll_to_bottom()
        height_2 = self.pl.driver.execute_script('return document.body.scrollHeight')
        self.assertEqual(height_1, height_2)

    def test_get_fixture_link_list(self):
        '''Tests that the fixture list has the required 38 games.'''
        self.pl.open_page(self.pl.URL)
        self.pl.accept_cookies()
        self.pl.scroll_to_bottom()
        link_list = self.pl.get_fixture_link_list()
        self.assertEqual(len(link_list), 38)

    def test_get_stats(self):
        '''Tests the correct number of statistics has been lifted from a certain game.'''
        self.pl.open_page('https://www.premierleague.com/match/66716')  # Test game
        self.pl.accept_cookies()
        self.pl.click_stats()
        stats = self.pl.get_stats()
        self.assertEqual(len(stats), 10)

    def test_split_stats_list(self):
        '''Tests the number of statistics remains the same after splitting and reconstructing.'''
        self.pl.open_page('https://www.premierleague.com/match/66716')  # Test game
        self.pl.accept_cookies()
        self.pl.click_stats()
        stats = self.pl.get_stats()
        split_stats = self.pl.split_stats_list(self.pl.get_stats())
        self.assertEqual(len(split_stats), len(stats))

    def test_home_or_away(self):
        '''Tests that the method returns a string ('Home' or 'Away').'''
        self.pl.open_page('https://www.premierleague.com/match/66716')  # Test game
        self.pl.accept_cookies()
        self.pl.click_stats()
        self.assertEqual(type(self.pl.home_or_away()), str)

    def test_get_result(self):
        '''Tests that the method returns a list e.g. [2, 1, 'Win'].'''
        self.pl.open_page('https://www.premierleague.com/match/66716')  # Test game
        self.pl.accept_cookies()
        self.pl.click_stats()
        result = self.pl.get_result(self.pl.home_or_away())
        self.assertEqual(type(result), list)

    def test_get_match_location(self):
        '''Tests that the method returns a string as the location.'''
        self.pl.open_page('https://www.premierleague.com/match/66716')  # Test game
        self.pl.accept_cookies()
        self.pl.click_stats()
        self.assertEqual(type(self.pl.get_match_location()), str)

    def test_get_match_date(self):
        '''Tests that the method returns a string as the date.'''
        self.pl.open_page('https://www.premierleague.com/match/66716')  # Test game
        self.pl.accept_cookies()
        self.pl.click_stats()
        self.assertEqual(type(self.pl.get_match_date()), str)

    def test_get_match_id(self):
        '''Tests that the method returns the match ID as a 5 digit integer.'''
        match_id = self.pl.get_match_id('https://www.premierleague.com/match/66716')  # Test game
        self.assertEqual(len(str(match_id)), 5)

    def test_generate_uuid(self):
        '''Tests that the method generates a 36 character unique ID (32 digits with 4 hyphens.).'''
        uuid = self.pl.generate_uuid()
        self.assertEqual(len(str(uuid)), 36)

    def test_create_dictionary(self):
        '''Tests the dictionary contains the right number of statistics.'''
        URL = 'https://www.premierleague.com/match/66716'  # Test game
        self.pl.open_page(URL)
        self.pl.accept_cookies()
        self.pl.click_stats()
        stats_dict = self.pl.create_dictionary(
            self.pl.get_match_id(URL),
            self.pl.get_match_date(),
            self.pl.get_match_location(),
            self.pl.home_or_away(),
            self.pl.get_result(self.pl.home_or_away()),
            self.pl.split_stats_list(self.pl.get_stats())
            )
        self.assertEqual(len(stats_dict), 18)



    def tearDown(self):
        '''Closes the browers and deletes the test instance.'''
        self.pl.close_browser()
        del self.pl


if __name__ == '__main__':
    unittest.main()

#%%
print(type(1))
# %%