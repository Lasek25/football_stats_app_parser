from bs4 import BeautifulSoup
from selenium import webdriver
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config


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


def get_teams(leagues):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome("D:/programy/chromedriver_win32/chromedriver.exe", chrome_options=options)

    teams = []
    for league in leagues:
        driver.get("https://www.flashscore.pl/pilka-nozna/" + league)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        teams_table = soup.find_all('a', class_='rowCellParticipantName___2pCMCKl')
        for team in teams_table:
            teams.append([str(team.string)])

    return teams


def main():
    leagues = ['anglia/premier-league/', 'francja/ligue-1/', 'hiszpania/laliga/', 'niemcy/bundesliga/',
               'polska/pko-bp-ekstraklasa/', 'wlochy/serie-a/', 'anglia/championship', 'polska/fortuna-1-liga/']
    # leagues = ['polska/fortuna-1-liga/']
    teams = get_teams(leagues)
    insert_teams(teams)


if __name__ == "__main__":
    main()
