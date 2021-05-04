from selenium import webdriver
import datetime
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
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
        link = "https://www.flashscore.pl/pilka-nozna/" + league + url_end
        matches_stats = get_matches(matches_stats, last_date_p, link, driver)
    driver.quit()
    return matches_stats


def insert_matches(matches_info, stats_info, url_end):
    query_teams_in_matches = "UPDATE teams_in_matches SET goals=%s, corners=%s, yellow_cards=%s, red_cards=%s," \
                             "fouls=%s, offsides=%s, shots_on_goal=%s, updated_at=now() WHERE " \
                             "(match_id IN (SELECT id FROM matches WHERE BINARY flashscore_id = %s)) AND " \
                             "(teams_in_competition_id IN (SELECT id FROM teams_in_competitions WHERE team_id IN " \
                             "(SELECT id FROM teams WHERE name=%s)))"

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
    data_type = "wyniki"
    # data_type = "spotkania"
    matches_stats = get_stats(leagues, data_type)
    insert_matches(matches_stats, chosen_stats, data_type)
    # update_points()


if __name__ == "__main__":
    main()
