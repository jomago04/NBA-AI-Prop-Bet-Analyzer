# NBA AI Prop Bet Analyzer

Python project that scrapes NBA player statistics for prop bet analysis.

## Features
- Scrapes NBA player stats
- Stores data for analysis
- Uses OpenAI to analyze the data and provide a prop bet analysis
- Uses FastAPI to create a type of API for the scraper to use with an AI query
- Displays the data in a frontend

## Technologies
- Python
- Selenium
- FastAPI
- OpenAI

## Future Plans
- Implement automated prop bet scraping so you no longer have to manually find prop bets
- Implement a frontend for the project
- Add additional sports to the project

## To Do
- Fix a lot of the scraping issues
- Add more relevant scraped data to prompt
- Add prompt engineering depending on prop bet type

## Update Log
- 12/22/2024: 
- Added a readme!

- 12/23/2024: 
- Added FastAPI to create a type of API for the scraper to use with an AI query. After realizing that BS4 was not working as well as I'd like, I decided to move to a more dynamic scraping method.
- Added Selenium scraper and test scraper to move to a more dynamic scraping method. Learned a lot about how to use Selenium to scrape data from a website but it's not working as well as I'd like. Next update will be a better attempt at scraping the data with selenium.
- Ended up putting todays Selenium work in a archive folder to keep the project clean and to reference it later.

- 12/24/2024 :
- Reworked the playerInfo.py file to get the best data to use for prop bets

- 12/26/2024:
- Started work on a Selenium scraper in place of the BS4 Scraper

- 12/27/2024:
- Added rest of the playerInfo.py file to the seleniumScraper.py file as well as the advanced gamelog data
- Made a new class in playerInfo.py to store the last 5 game stats and display the individual game stats
- Added utilities folder
- Added timeConverter.py file to convert the time from float to string
- Added nameFormat.py file to format the player name

- 12/29/2024:
- Finished work on the seasonal selenium scraping with a few tweaks needed
- Need to get player info and opposing team stats working
- Need to make a better way to load pages needed once so we grab all data on one load per page

- 12/31/2024:
- Added scraping for PlayerInfo

- 1/3/2025:
- Added scraping for Opposing Team Stats
- Added FastAPI to create a type of API for the scraper to use with an AI query.
- Added AI Analysis to the FastAPI API

---
© 2024 Joshua Gould. All rights reserved.
