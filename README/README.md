# Data Collection Pipeline Project

> My third project for AiCore. Webscraping the statistics of Chelsea FC during the 2021/22 season from the official Premier League website.

## Milestone 1: Deciding the website to scrape

- The aim of this project is to gain a deeper understanding as to how Chelsea's match stats vary with factors such as the location and result of the game.

- The main reason as to why the Premier League official website has been selected is due to the reliability of the information it provides. Furthermore, it stores data on previous seasons' fixtures meaning that this program could be adapted to scrape data from other seasons leading to a more accurate model. It also stores information of every team's matches, therefore this program could also be extended to allow the user to choose which team to look into.

- They Python package Selenium will be imported to use it's WebDriver as a means to automate web browser interaction. Google Chrome will be the browser used.

-  Git branches will be used locally before being commited and pushed to the remote repository via a pull request.

> Insert an screenshot of fixture list.

## Milestone 2: Finding the URL for each game

- The class ```Scraper``` has been created with attributes that include the website link, WebdDiver and pause time. The pause time between clicks is important for two reasons:
    - A new page must be fully loaded after being clicked else the program may search for an element that is not yet present, causing an error.
    - Too many clicks in a short period of time may be deemed as spam by the website, causing it to be non-functional.

- Class methods were added to open the page on Chrome, accept all cookies and extract the links to each Chelsea game from the list of fixtures for the season.

- The ```scroll_to_bottom``` method was implemented as the page originally only displayed the first four Chelsea games. More games get loaded automatically as the page is scrolled.

- The links are found using Selenium's ```.find_element(By. XPATH)``` method to locate the href attribute containing the URL of each fixture. i.e.:
```python
fixture_list = self.driver.find_element(By.XPATH, '//section[@class="fixtures"]')
        home_games = fixture_list.find_elements(By.XPATH, '//li[@data-home="Chelsea"]')
        away_games = fixture_list.find_elements(By.XPATH, '//li[@data-away="Chelsea"]')
```

- These links are appended to an empty list which can then be iterated through to get the data required from each game.

- The class was initialised within the ```if __name__ == '__main__'``` block, so that it only runs if the main.py file is run directly rather than on any import.

```python
if __name__ == '__main__':
    premierleague = Scraper(driver=webdriver.Chrome(),
                            URL='https://www.premierleague.com/results?co=1&se=418&cl=-1',
                            pause_time=1)
    premierleague.run_crawler()
```

> Insert screenshot of what you have built working.

## Milestone 3: Retrieving data from each page
- The method ```scrape_stats``` was introduced in order to extract the date, location, result and match stats a particular link (one game).
- The unique 5 digit Match ID was lifted from the URLs of each match.
- A universally unique identifier (UUID) is also generated and assigned to each match. Version 4 UUIDs are randomly generated 32 character, unlike previous versions, and contain 32 characters making them unique for the practical purposes. The probability of duplicates is negligable. They are easily generated from the Python UUID package:
```python
import uuid
def generate_uuid(self):
        return uuid.uuid4()
```

- These raw statistics are then converted into a list, before finally being turned into a dictionary by the ```create_dictionary``` method. This dictionary contained information on:
    - Match ID
    - V4 UUID
    - Match date
    - Location
    - Home/Away
    - Result
    - Goals scored
    - Goals conceeded
    - Possession
    - Shots on target
    - Shots 
    - Touches
    - Passes
    - Tackles
    - Clearances
    - Corners
    - Offsides
    - Yellow cards
    - Red cards
    - Fouls conceeded

- Finally, this data is saved locally in the directory ```raw_data```. Each sub-directory named after the match ID containing a ```data.json``` file with this information in the form of a dictionary. If the directory for the match does not exist, the method will create a new one and if the file already exists, it will simply overwrite it. This was done as follows:
```python
def save_data(self, match_id, raw_stats):
        path = f'/Users/asadiceccarelli/Documents/AiCore/Data-Collection-Pipeline/raw_data/{match_id}'
        if not os.path.exists(path):
            os.makedirs(path)
        json_str = json.dumps(raw_stats)
        with open(f'{path}/data.json', 'w') as outfile:
            outfile.write(json_str)
```

- Now data has been extracted for each of Chelsea's games from the 2021/22 season and stored in the file ```raw_data```.
> Insert an screenshot of raw_data.