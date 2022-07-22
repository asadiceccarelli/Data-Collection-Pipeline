# Data Collection Pipeline Project

> My third project for AiCore. Webscraping the match statistics of a club from any season from the official Premier League website.

## Milestone 1: Deciding the website to scrape

- The aim of this project is to gain a deeper understanding as to how a clubs match stats vary with factors such as the location and result of the game.

- The main reason as to why the Premier League official website has been selected is due to the reliability of the information shown on each game. It stores information from every team's fixtures from the past 29 seasons therefore providing a very large quanitity of data for the program to scrape from.

- They Python package ```Selenium``` will be imported to use it's WebDriver as a means to automate web browser interaction. Google Chrome will be the browser used.

-  Git branches will be used locally before being commited and pushed to the remote repository via pull requests.

> Insert an screenshot of fixture list.

## Milestone 2: Finding the URL for each game

- The class ```PremierLeagueScraper``` has been created with the WebDriver as an attribute, to allow the user to dictate which browser they want to use. 

- ```self.club``` and ```self.year``` attributes are created from user inputs in the terminal, and verified as bein valid by checking the respective dictionary and list in the file ```valid_inputs.py```. ```self.URL``` is the URL of the Premier League website's results page.

- Class methods were added to open the page on Chrome, accept all cookies, close the ad if required and select the season to be inspected from the dropdown menu. Then, the ```get_fixture_link_list()``` method will extract the links to each of the club to be inspected's matches from the list of fixtures.

- The ```scroll_to_bottom()``` method was implemented as the page only displayed the first few games without being scrolled. More games get loaded automatically as the page is scrolled.

- !!! The links are found using Selenium's ```.find_element(By. XPATH)``` method to locate the href attribute containing the URL of each fixture. i.e.:
```python
fixture_list = self.driver.find_element(By.XPATH, '//section[@class="fixtures"]')
            home_games = fixture_list.find_elements(By.XPATH, f'//li[@data-home="{self.club}"]')
            away_games = fixture_list.find_elements(By.XPATH, f'//li[@data-away="{self.club}"]')
```

- !!! The method ```Expected Conditions``` is imported from the package ```selenium.webdriver.support``` as ```EC``` to allow us to wait for certain conditions to be met before we execute a command. For example, in order for us to wait until the fixture list has been loaded before we start scrolling, we use the following method. The second parameter in ```WebDriverWait``` is the length of time before the program will throw a ```TimeoutError``` if the expected conditions are still not met.

```python
WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="fixtures__matches-list"]')))
```

- These links are appended to a list which can then be iterated through to get the data required from each game.

- The class was initialised within the ```if __name__ == '__main__'``` block, so that it only runs if the file ```scraper.py``` is run directly rather than on any import.

```python
if __name__ == '__main__':
    premierleague = Scraper(driver=webdriver.Chrome())
    premierleague.run_crawler()
```

> Insert screenshot of what you have built working.

## Milestone 3: Retrieving data from each page
- The method ```scrape_stats()``` was introduced in order to extract the date, location, result and match stats a particular link (one game).
- The unique 9 character Match ID was created from the unique match number and abbreviated team name separated with a dash.
    - The match number was lifted from the last 5 characters of the URL of each link.
    - The dictionary in ```valid_inputs``` contains the shortened name of each club as the key.
- A Version 4 universally unique identifier (V4 UUID) is also generated and assigned to each match. V4 UUIDs are randomly generated 32 character, unlike previous versions, and contain 32 characters making them unique for the practical purposes. The probability of duplicates is negligable. They are easily generated from the Python ```uuid``` package.
```python
import uuid
def generate_uuid(self):
        return uuid.uuid4()
```

- These raw statistics are then converted into a list, before finally being turned into a dictionary by the ```create_dictionary()``` method. This dictionary contained information on:
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

- Finally, this data is saved locally in the directory ```raw_data```. Each sub-directory named after the match ID containing a ```data.json``` file with this information in the form of a dictionary. If the directory for the match does not exist, the method will create a new one and if the file already exists, it will simply overwrite it. 
```python
def save_data_locally(self, match_id, raw_stats):
        path = f'/Users/asadiceccarelli/Documents/AiCore/Data-Collection-Pipeline/raw_data/{self.club}-{self.year[-5:-3]}{self.year[-2:]}/{match_id}'
        if not os.path.exists(path):
            os.makedirs(path)
        json_str = json.dumps(raw_stats)
        with open(f'{path}/data.json', 'w') as outfile:
            outfile.write(json_str)    
```

- For example, the ```data.json``` file for one of Chelsea's match stats from the season 2019/20 will be stored in teh directory ```Chelsea-1920/46613-CHE```.

> Insert an screenshot of raw_data.

## Milestone 4: Refining and Testing

- Docstrings are added to the ```PremierLeagueScraper``` class and all of its methods, using the Google format. These are much more easily accessed using the ```__doc__``` attribute or the built-in ```help()``` function, in comparison to regular ```#``` comments.

- Several methods have been worked upon and rewritten, making these areas clearner or more efficient. 

- Each public method of the scraper class has also been tested using the ```unittest``` module. This is to ensure that all the individual units of the code work correctly.
    - Certain methods, such as ```open_page()``` and ```accept_cookies()``` were omitted from the tests, due to the simplicity in their nature.

- A new file ```test.py``` has been created to hold these unit tests, with a test class ```PremierLeagueScraperTestCase(unittest.TestCase)```. The test class is created as we are using the same intance of the class for each test, so it saves having to rewrite it each time.

- The class is initialsed using the ```setUp()``` method...

```python
def setUp(self):
        self.pl = PremierLeagueScraper(driver=webdriver.Chrome())
```

- ... and finished with the ```tearDown()``` method.

```python
def tearDown(self):
        self.pl.close_browser()
        del self.pl
```

- The 7 tests take around 300 seconds to run. There is a slight issue with the ```scroll_to_bottom()``` method due to the page not loading fast enough, however more times than not the test passes. A ```while``` loop to refresh the page and try again if all fixtures are not loaded properly and the driver option ```options.add_argument('--start-maximized')``` have been added to avoid this.

## Milestone 5: Scalably storing the data

- An Amazon Simple Storage Service (S3) is a data lake which is used to store files on the Amazon Web Service (AWS) server. The bucket ```premier-league-bucket``` has been created and the ```user_inputs()``` method gives the user the option to store the ```data.json``` files locally, in the cloud or both has been added. This is achieved using the AWS software development kit (SKD) ```boto3```.

```python
s3_client = boto3.client('s3')
        s3_client.upload_file(f'raw_data/{self.club}-{self.year[-5:-3]}{self.year[-2:]}/{match_id}/data.json', 'premier-league-bucket', match_id)
```

This would upload a file to the S3 bucket with the match ID as the reference.

> Uploading to the S3 bucket using ```boto3```.

- Amazon Relational Database Service (RDS) allows us to create a highly scalably database in the cloud. First, a virtual network is established to limit the range of IP addresses that can be used to access this service. Then, the database ```date-pipeline-project``` is created with PostgreSQL and accessed using pgAdmin 14. The function ```upload_to_sql()``` is created in the ```RDS_access.py``` file to download the files containing the data for the club being inspected from the S3 bucket, create a dataframe using pandas and upload to the RDS database using ```sqlalchemy```.

```python
DATABASE_TYPE = 'postgresql'
    DBAPI = 'psycopg2'
    HOST = 'aicore-db.ckoq1wsuhqob.us-east-1.rds.amazonaws.com'
    USER = 'postgres'
    PASSWORD = '**********'
    DATABASE = 'data-pipeline-project'
    PORT = 5432
    engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
```
> Creating the RDS engine using ```sqlalchemy```.

## Milstone 6: Preventing rescraping and getting more data

- To prevent rescraping, an ```if``` statement is added to the ```run_crawler``` method which checks to see if the RDS database to see if there is already information on the inputted club and year. If no data exists then the program will begind scraping and gathering the required information. If the database already contains this data, then the message ```'RDS database already contains data on this club from this season.'``` will be outputted in the terminal.

- To check that the scraper can run for extended periods of time, a simple ```for``` loop is introduced as a test. This contains a list of 4 clubs which the program iterates through to ensure it can process larger quanitites of data without crashing. If the program can run this, it would be scraping data from 152 links and uploading these entries to S3 and the RDS database, and so it is unlikley to have a problem running for even longer periods.

## Milestone 7: Containerising the scraper and running it on a cloud server

- A final refactoring of the code has been completed, ensuring all aspects are as neat and efficient as possible.

- CHECK TESTS ARE ALL STILL PASSING

- To run a scraper in a docker container, it must first be able to complete all the necessary tasks in 'headless mode' i.e. without the GUI. To do this, the ```options.headless = True```


## Milestone 8: Monitoring and alerting



## Milestone 9: Setting up a CI/CD pipeline for the docker image
