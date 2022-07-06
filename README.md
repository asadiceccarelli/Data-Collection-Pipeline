# Data-Collection-Pipline
My third project for AiCore. Webscraping football statistics from SofaScore.

# Data Collection Pipeline Project

> My third project for AiCore. Webscraping the statistics of Chelsea FC during the 2021/22 season from the official Premier League website.

## Milestone 1: Deciding the website to scrape

- The aim of this project is to gain a deeper understanding as to how Chelsea's match stats vary with the location and result of the game.

- The Premier League official website was selected as it provides the stats of every game of the season on the same page. Furthermore, it stores data on previous seasons' fixtures meaning that this model could be adapted to scrape data from other seasons leading to a more accurate model. It also stores information of every team's matches, therefore this model could be extended to allow the user to choose which team to look into.

- Git branches will be used for each milestone.

> Insert an screenshot of fixture list.

## Milestone 2: Finding the URL for each game

- The class Scraper has been created with attributes such that the website link, WebdDiver and pause time between clicks can be varied. The pause time between clicks is important for two reasons:
    - A new page must be fully loaded after being clicked else the program may search for an element that is not yet present, causing an error.
    - Too many clicks in a short period of time may be deemed as spam by the website, causing it to be non-functional.

- Class methods were added to open the page, accept cookies and extract the links to each Chelsea game from the list of fixtures.

- A method to scroll to the bottom of the page was implemented as the page only displayed the first four Chelsea games. More were loaded as the program scrolled down the page.

- The class was initialised within the ```if __name__ == "__main__"``` block, so that it only runs if the main.py file is run directly rather than on any import.

```python
if __name__ == '__main__':
    premierleague = Scraper(driver=webdriver.Chrome(),
                            URL='https://www.premierleague.com/results?co=1&se=418&cl=-1',
                            pause_time=1)
    premierleague.scrape_links()
```

> Insert screenshot of what you have built working.
