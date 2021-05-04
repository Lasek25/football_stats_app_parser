from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from points import update_points
from matches import get_matches


def get_stats(leagues, url_end):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome("D:/programy/chromedriver_win32/chromedriver.exe", chrome_options=options)

    matches_stats = []
    for league in leagues:
        # last_date_p = last_date[leagues.index(league)][0]
        print(league.split('/')[1].replace('-', ' ').title())
        last_date_p = select_update_at(league.split('/')[1].replace('-', ' ').title())[0]
        if isinstance(None, type(last_date_p)):
            last_date_p = datetime.datetime.strptime("2020-08-01 00:00", "%Y-%m-%d %H:%M")

        # version without get_matches() function
        # driver.get("https://www.flashscore.pl/pilka-nozna/" + league + "wyniki/")
        # page_source = driver.page_source
        #
        # soup = BeautifulSoup(page_source, 'lxml')
        # match_id_list = []
        # matches = soup.find_all('div', class_='event__match')
        # for match in matches:
        #     if datetime.datetime.strptime(match.text[:12], "%d.%m. %H:%M") \
        #             .replace(year=datetime.datetime.now().year) > last_date_p:
        #         # required id number starts from 5th character
        #         match_id_list.append(match.get('id')[4:])
        #
        # for match_id in match_id_list:
        #     match_url = 'https://www.flashscore.pl/mecz/' + match_id + '/#statystyki-meczu;0'
        #     driver.get(match_url)
        #     # try:
        #     element = WebDriverWait(driver, 1).until(EC.presence_of_element_located
        #                                              ((By.ID, "tab-statistics-0-statistic")))
        #     # except 'TimeoutException':
        #     #     "You cannot parse data because website has not been ready (TimeoutException)"
        #     page_source = driver.page_source
        #     soup = BeautifulSoup(page_source, 'lxml')
        #
        #     round_number = soup.select('span.description__country a')[0].text[-2:].strip()
        #     date_string = soup.select('div.description__time')[0].text
        #     date = str(datetime.datetime.strptime(date_string, "%d.%m.%Y %H:%M").strftime("%Y-%m-%d %H:%M"))
        #     result = [soup.select('span.scoreboard')[0].text, soup.select('span.scoreboard')[1].text]
        #     # all_stats = soup.select('div.statTextGroup')[1].text
        #     all_stats_html = soup.select('#tab-statistics-0-statistic div.statText')
        #     print(all_stats_html)
        #     all_stats = []
        #     for i in range(len(all_stats_html)):
        #         all_stats.append(all_stats_html[i].text)
        #
        #     teams = [soup.select('div.tname__text a')[0].text, soup.select('div.tname__text a')[1].text]
        #     # print(all_stats)
        #
        #     match_stats = \
        #         {'flashscore_id': match_id, 'round': round_number, 'date': date, 'teams': teams, 'result': result,
        #          'all_stats': all_stats}
        #     matches_stats.append(match_stats)

        link = "https://www.flashscore.pl/pilka-nozna/" + league + url_end
        matches_stats = get_matches(matches_stats, last_date_p, link, driver)
    driver.quit()
    return matches_stats


def insert_matches(matches_info, stats_info, url_end):
    # query_matches = "INSERT INTO matches(flashscore_id,round,date,created_at,updated_at) VALUES (%s,%s,%s,now(),now())"
    # query_matches = "UPDATE matches SET date=%s, updated_at=now() WHERE BINARY flashscore_id = BINARY %s"
    # to insert data of past matches in new league
    # query_teams_in_matches = "INSERT INTO teams_in_matches(goals,corners,yellow_cards,red_cards,fouls,offsides," \
    #                          "shots_on_goal,match_id,teams_in_competition_id,created_at,updated_at) VALUES " \
    #                          "(%s,%s,%s,%s,%s,%s,%s,(SELECT `id` FROM `matches` WHERE `flashscore_id` = %s)," \
    #                          "(SELECT id FROM teams_in_competitions WHERE team_id IN " \
    #                          "(SELECT id FROM teams WHERE name = %s)),now(),now())"
    query_teams_in_matches = "UPDATE teams_in_matches SET goals=%s, corners=%s, yellow_cards=%s, red_cards=%s," \
                             "fouls=%s, offsides=%s, shots_on_goal=%s, updated_at=now() WHERE " \
                             "(match_id IN (SELECT id FROM matches WHERE BINARY flashscore_id = %s)) AND " \
                             "(teams_in_competition_id IN (SELECT id FROM teams_in_competitions WHERE team_id IN " \
                             "(SELECT id FROM teams WHERE name=%s)))"

    # round_date = []
    # # teams_home_stats = []
    # # teams_away_stats = []
    # teams_stats = []
    # for match in matches_info:
    #     print(match)
    #     round_date.append((match['flashscore_id'], match['round'], match['date']))
    #     teams_home_stats_tmp = []
    #     teams_away_stats_tmp = []
    #     if url_end == "wyniki":
    #         teams_home_stats_tmp = [match['result'][0]]
    #         teams_away_stats_tmp = [match['result'][1]]
    #         for i in stats_info:
    #             if i in match['all_stats']:
    #                 tmp = match['all_stats'].index(i)
    #                 teams_home_stats_tmp.append(match['all_stats'][tmp - 1])
    #                 teams_away_stats_tmp.append(match['all_stats'][tmp + 1])
    #             else:
    #                 teams_home_stats_tmp.append(0)
    #                 teams_away_stats_tmp.append(0)
    #     teams_home_stats_tmp.append(match['flashscore_id'])
    #     teams_away_stats_tmp.append(match['flashscore_id'])
    #     teams_home_stats_tmp.append(match['teams'][0])
    #     teams_away_stats_tmp.append(match['teams'][1])
    #     teams_stats.append(teams_home_stats_tmp)
    #     teams_stats.append(teams_away_stats_tmp)
    # #     teams_home_stats.append(teams_home_stats_tmp)
    # #     teams_away_stats.append(teams_away_stats_tmp)
    # # print(teams_home_stats)
    # # print(teams_away_stats)
    # print(round_date)
    matches_data = []
    teams_in_matches_data = []
    for match in matches_info:
        print(match)
        matches_data.append(
            (match['flashscore_id'], match['round'], match['date'], match['teams'][0], match['teams'][1]))
        teams_home_stats_tmp = []
        teams_away_stats_tmp = []
        if url_end == "wyniki":
            teams_home_stats_tmp = [match['result'][0]]
            teams_away_stats_tmp = [match['result'][1]]
            for i in stats_info:
                if i in match['all_stats']:
                    tmp = match['all_stats'].index(i)
                    teams_home_stats_tmp.append(match['all_stats'][tmp - 1])
                    teams_away_stats_tmp.append(match['all_stats'][tmp + 1])
                else:
                    teams_home_stats_tmp.append(0)
                    teams_away_stats_tmp.append(0)
        teams_home_stats_tmp.append(match['flashscore_id'])
        teams_away_stats_tmp.append(match['flashscore_id'])
        teams_home_stats_tmp.append(match['teams'][0])
        teams_away_stats_tmp.append(match['teams'][1])
        teams_in_matches_data.append(teams_home_stats_tmp)
        teams_in_matches_data.append(teams_away_stats_tmp)
    print(matches_data)

    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        # cursor.executemany(query_matches, round_date)
        # (matches_info['round'], matches_info['date'])
        # cursor.executemany(query_teams_in_matches, teams_stats)
        # cursor.executemany(query_teams_in_matches, teams_home_stats)
        # cursor.executemany(query_teams_in_matches, teams_away_stats)
        for match_info in matches_data:
            print(match_info)
            cursor.callproc('insert_update_matches', match_info)
        if url_end == "wyniki":
            # cursor.executemany(query_matches, [matches_info[2], matches_info[0]])
            cursor.executemany(query_teams_in_matches, teams_in_matches_data)
        # else:
        #     for match_info in matches_data:
        #         print(match_info)
        #         cursor.callproc('insert_update_matches', match_info)

        conn.commit()
    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def select_update_at(competition):
    # old version
    # query = "SELECT MAX(tim.updated_at) FROM teams_in_matches tim JOIN teams_in_competitions tic " \
    #         "ON tim.teams_in_competition_id = tic.id GROUP BY tic.competition_id ORDER BY tic.competition_id ASC"

    query = "SELECT MAX(tim.updated_at) FROM teams_in_matches tim JOIN teams_in_competitions tic " \
            "ON tim.teams_in_competition_id = tic.id JOIN competitions com ON tic.competition_id = com.id " \
            "WHERE com.name = %s"

    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query, [competition])
        tmp = cursor.fetchone()

        conn.commit()

        print(tmp)
        return tmp
    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def main():
    leagues = ['anglia/premier-league/', 'francja/ligue-1/', 'hiszpania/laliga/', 'niemcy/bundesliga/',
               'polska/pko-bp-ekstraklasa/', 'wlochy/serie-a/', 'anglia/championship/', 'polska/fortuna-1-liga/']
    # leagues = ['polska/fortuna-1-liga/']  # , 'hiszpania/laliga/', 'wlochy/serie-a/']
    chosen_stats = ['Rzuty rożne', 'Żółte kartki', 'Czerwone kartki', 'Faule', 'Spalone', 'Strzały na bramkę']
    # to get correct data, first you should run with link parameter (data_type variable)
    # "wyniki" and next once again with link parameter (data_type variable) "spotkania"
    # data_type = "wyniki"
    data_type = "spotkania"
    matches_stats = get_stats(leagues, data_type)
    insert_matches(matches_stats, chosen_stats, data_type)
    # update_points()


if __name__ == "__main__":
    main()
