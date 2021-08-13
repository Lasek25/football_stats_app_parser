from bs4 import BeautifulSoup
from selenium import webdriver
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config


def select_current_teams():
    query_teams = "SELECT name FROM teams"

    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query_teams)
        select_data = list(map(''.join, cursor.fetchall()))
        print(select_data)

        conn.commit()
        return select_data

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def insert_teams(teams):
    query = "INSERT INTO teams(name,created_at,updated_at) VALUES(%s,now(),now())"

    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.executemany(query, teams)

        conn.commit()
    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def get_teams(leagues, current_teams):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')

    teams = []
    for league in leagues:
        driver = webdriver.Chrome("D:/programy/chromedriver_win32/chromedriver.exe", chrome_options=options)
        driver.get("https://www.flashscore.pl/pilka-nozna/" + league)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        # teams_table = soup.find_all('a', class_='rowCellParticipantName___2pCMCKl')
        # teams_table = soup.find_all('a', class_='rowCellParticipantName___38vskiN')
        teams_table = soup.find_all('a', class_='tableCellParticipant__name')
        for team in teams_table:
            if team.string not in current_teams:
                print(str(team.string))
                teams.append([str(team.string)])
    return teams


def main():
    leagues = ['anglia/premier-league/', 'francja/ligue-1/', 'hiszpania/laliga/', 'niemcy/bundesliga/',
               'polska/pko-bp-ekstraklasa/', 'wlochy/serie-a/', 'anglia/championship/', 'polska/fortuna-1-liga/',
               'japonia/j1-league/', 'norwegia/eliteserien/']
    # leagues = ['japonia/j1-league/']
    # leagues = ['francja/ligue-1/', 'anglia/championship/']
    current_teams = select_current_teams()
    teams = get_teams(leagues, current_teams)
    insert_teams(teams)


if __name__ == "__main__":
    main()
