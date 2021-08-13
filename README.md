# :soccer: Football Stats App - scrapers

## General Informations
This repo contains set of web scrapers created with Python language, they are a part of the [Football Stats App](https://github.com/Lasek25/football_stats_app).
They scrape selected data about football leagues, teams and matches stats from [Flashscore](https://flashscore.pl) website and then save them in application's database.

## Tech Stack
* Python (version: 3.6.4)
* MySQL
* Selenium (version: 3.141.0)
* ChromeDriver (version depends on your Chrome version)

## Instalation
1. Firstly you should get acquainted with readme file from main app repo ([Football Stats App](https://github.com/Lasek25/football_stats_app)) and install backend of this application or create database from the schema by yourself.
2. Chrome web browser is required.
3. Download project from this repo.
4. Create `config.ini` file in main directory of the project and refill data about your database, e.g.
```
[mysql]
host = localhost
database = football_stats_app
user = root
password =
```
## Usage

1. Add countries and leagues to right tables in your database.
2. Run the scripts from the table below in order (`teams.py` and `teams_in_competitions.py` only once if you have added new league or new season has started).
  Run last script (`matches_stats.py`) every time if you want to update matches data.

| SCRIPT NAME | DESCRIPTION |
| --- | --- |
| `teams.py` | get new football teams |
| `teams_in_competitions.py` | assign new teams to the appropriate leagues |
| `matches_stats.py` | get new selected matches stats and assign them to the right teams |
