# NBA AI Prop Bet Analyzer

Python project that scrapes NBA player statistics for prop bet analysis.

## Startup 
- Run uvicorn main:app --reload
- Goto http://127.0.0.1:8000/docs#/default/analyzeBet_analyze_post (LOCAL ONLY)
- Enter a name, prop bet type, and the line and click analyze
- The data will be displayed in the response

## Features
- Scrapes NBA player stats
- Stores data for analysis
- Uses OpenAI to analyze the data and provide a prop bet analysis
- Uses FastAPI to create a type of API for the scraper to use with an AI query
- Displays the data in a frontend
- **Tracks prediction outcomes**: every AI analysis is saved to a SQLite database, can be
  graded against the real bet result, and rolled up into accuracy stats

## Outcome Tracking

Each analysis from `/analyze` is persisted with its parsed OVER/UNDER prediction. Once a
game is played you submit the real stat result and the system grades whether the bot was
right. These graded records are the foundation for an upcoming feature that simulates a
period in time to test the bot's probability outcomes (backtesting).

Endpoints:
- `POST /analyze` — runs analysis and stores it; response includes the new `id`,
  `predicted_direction`, and `confidence`. Optional `game_date` (ISO date) can be supplied.
- `POST /analyses/{id}/outcome` — submit `{"actual_value": <number>}` to settle a bet.
  The system computes OVER/UNDER/PUSH vs the line and whether the prediction was correct.
- `GET /analyses/{id}` — fetch a single stored analysis and its outcome.
- `GET /analyses` — list/filter analyses (`status`, `player_name`, `bet_type`,
  `start_date`, `end_date`).
- `GET /stats/accuracy` — aggregate accuracy, filterable by player, bet type, and date
  range (the basis for the time-period simulation feature).

The database lives at `data/nba_bets.db` by default (override with the `BET_DB_PATH`
environment variable). Run the offline tests with `python tests/test_outcome_tracker.py`.

## Technologies
- Python
- Selenium
- FastAPI
- OpenAI

## Future Plans
- Front end for the project
- Start scraping historical stats and bet lines to apply machine learning models to better predict prop bets (might be a seperate project and use stocks instead)
  - This allows AI analysis AND machine learning models to be used to predict prop bets

- Implement a frontend for the project
- Add additional sports to the project

## To Do
- Add better error handling and testing capabilities


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

- 1/9/2025:
- Attempted to add a prop line API but it's not working due to how the API works, easier for now to manually enter the prop line
- Starting to think about a seperate project that involves stocks and crypto 
- As this project comes to a close I'm reflecting on this project and the amount of learnt through this project. I've learned a lot about how to scrape data from a website, how to use OpenAI to analyze data, and how to use FastAPI to create an API. I've learned a lot about how projects work and   how to properly structure a project. I'm proud of the work I've done and I'm excited to see where this next project takes me. 

- 5/31/2026:
- Added bet outcome tracking: AI analyses are now persisted to a SQLite database with their
  parsed OVER/UNDER prediction, can be settled against the real bet result, and aggregated
  into accuracy stats (filterable by player, bet type, and date range).
- This lays the groundwork for the next feature: simulating a period in time to test the
  bot's probability outcomes (backtesting).
- Added an offline test suite for the tracking logic under `tests/`.
---
© 2024 Joshua Gould. All rights reserved.
