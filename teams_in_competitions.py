from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config


def insert_teams_in_competitions(data):
    query = "INSERT INTO teams_in_competitions(season,team_id,competition_id,created_at,updated_at) " \
            "VALUES ('2020/2021',%s,%s,now(),now())"

    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.executemany(query, data)

        conn.commit()
    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def select_competitions_data():
    query_competitions = "SELECT COUNT(id) FROM competitions"
    query_teams = "SELECT COUNT(id) FROM teams"

    select_data = []
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query_competitions)
        select_data.append(cursor.fetchone()[0])
        cursor.execute(query_teams)
        select_data.append(cursor.fetchone()[0])
        print(select_data)

        conn.commit()
        return select_data

    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def get_teams_in_competitions(count_teams):
    tic = []
    # if your table is empty
    # tmp = 0
    # for i in range(1, len(count_teams)+1):
    #     for j in range(1, count_teams[i-1]+1):
    #         tic.append([j+tmp, i])
    #     tmp += count_teams[i-1]
    # adding tic for new competitions
    select_data = select_competitions_data()
    all_teams = select_data[1]
    all_new_teams = 0
    all_leagues = select_data[0]
    tmp_position = 0
    for c in count_teams:
        all_new_teams += c
    for i in range(all_leagues + 1 - len(count_teams), all_leagues + len(count_teams)):
        for j in range(1, count_teams[tmp_position] + 1):
            tic.append([all_teams - all_new_teams + j, i])
        all_new_teams -= count_teams[tmp_position]
        tmp_position += 1
    return tic


def main():
    # count_teams_in_competitions = [20, 20, 20, 18, 16, 20, 24]
    count_teams_in_competitions = [18]
    teams = get_teams_in_competitions(count_teams_in_competitions)
    # print(teams)
    insert_teams_in_competitions(teams)


if __name__ == "__main__":
    main()
