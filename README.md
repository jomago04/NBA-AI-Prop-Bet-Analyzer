# NBA Stats Scraper

Python project that scrapes NBA player statistics for prop bet analysis.

## Features
- Scrapes NBA player stats
- Stores data for analysis

## Technologies
- Python
- BeautifulSoup4
- Pandas
- Selenium
- FastAPI

## Future Plans
- Implement AI-powered prop bet predictions using scraped stats
- Add automated statistical analysis

## To Do
- Rework playerInfo.py to get the best data to use for prop bets (requires more research)
- Figure out how to scrape the data with Selenium in a good and efficient way

## Update Log
- 12/22/2024: 
- Added a readme!

- 12/23/2024: 
- Added FastAPI to create a type of API for the scraper to use with an AI query. After realizing that BS4 was not working as well as I'd like, I decided to move to a more dynamic scraping method.
- Added Selenium scraper and test scraper to move to a more dynamic scraping method. Learned a lot about how to use Selenium to scrape data from a website but it's not working as well as I'd like. Next update will be a better attempt at scraping the data with selenium.
- Ended up putting todays Selenium work in a archive folder to keep the project clean and to reference it later.

12/24/24 :
- Reworked the playerInfo.py file to get the best data to use for prop bets

12/26/2024:
- Started work on a Selenium scraper in place of the BS4 Scraper

---
© 2024 Joshua Gould. All rights reserved.