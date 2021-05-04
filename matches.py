import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime


def get_matches(matches_stats, last_date_p, link, driver):
    driver.get(link)
    while "wyniki" in link:
        try:
            driver.execute_script("arguments[0].click();", WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "event__more"))))
            time.sleep(1)
        except:
            break

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    match_id_list = []
    matches = soup.find_all('div', class_='event__match')
    for match in matches:
        match_datetime = datetime.datetime.strptime(match.text[:12], "%d.%m. %H:%M")

        # month (after ending the season and before starting the new one) necessary for the correct year selection
        month = 7

        if datetime.datetime.now().month > month > match_datetime.month:
            match_datetime = match_datetime.replace(year=datetime.datetime.now().year + 1)
        elif datetime.datetime.now().month < month < match_datetime.month:
            match_datetime = match_datetime.replace(year=datetime.datetime.now().year - 1)
        else:
            match_datetime = match_datetime.replace(year=datetime.datetime.now().year)
        # if datetime.datetime.strptime(match.text[:12], "%d.%m. %H:%M") \
        #         .replace(year=datetime.datetime.now().year) > last_date_p:
        if last_date_p < match_datetime < (datetime.datetime.now() + datetime.timedelta(weeks=5)):
            # required id number starts from 5th character
            match_id_list.append(match.get('id')[4:])

    for match_id in match_id_list:
        match_url = 'https://www.flashscore.pl/mecz/' + match_id + '/#szczegoly-meczu/statystyki-meczu/0'
        driver.get(match_url)
        # data in web tag with chosen id or class should be different in the following pages
        if "wyniki" in link:
            # element = WebDriverWait(driver, 5).until(EC.presence_of_element_located
            #                                          ((By.ID, "tab-statistics-0-statistic")))
            element = WebDriverWait(driver, 5).until(EC.visibility_of_any_elements_located
                                                     ((By.CLASS_NAME, "statRow___3x8JuS9")))
        else:
            # element = WebDriverWait(driver, 5).until(EC.visibility_of_any_elements_located
            #                                          ((By.CLASS_NAME, "participant-imglink")))
            element = WebDriverWait(driver, 5).until(EC.visibility_of_any_elements_located
                                                     ((By.CLASS_NAME, "participantImage___2Oi0lJ_")))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        # round_number = soup.select('span.description__country a')[0].text[-2:].strip()
        round_number = soup.select('span.country___24Qe-aj a')[0].text[-2:].strip()
        # date_string = soup.select('div.description__time')[0].text
        date_string = soup.select('div.startTime___2oy0czV')[0].text
        print(date_string)
        date = str(datetime.datetime.strptime(date_string, "%d.%m.%Y %H:%M").strftime("%Y-%m-%d %H:%M"))
        # teams = [soup.select('div.tname__text a')[0].text, soup.select('div.tname__text a')[1].text]
        teams = [
            soup.select('a.participantName___3lRDM1i')[0].text,
            soup.select('a.participantName___3lRDM1i')[1].text
        ]
        print(teams)
        if "wyniki" in link:
            # result = [soup.select('span.scoreboard')[0].text, soup.select('span.scoreboard')[1].text]
            result = [
                soup.select('div.wrapper___3rU3Jah span')[0].text,
                soup.select('div.wrapper___3rU3Jah span')[2].text
            ]
            print(result)
            # all_stats_html = soup.select('#tab-statistics-0-statistic div.statText')
            all_stats_html = soup.select('div.statCategory___33LOZ_7 div')
            print(all_stats_html)
            all_stats = []
            for i in range(len(all_stats_html)):
                all_stats.append(all_stats_html[i].text)
            print(all_stats)
            match_stats = \
                {'flashscore_id': match_id, 'round': round_number, 'date': date, 'teams': teams, 'result': result,
                 'all_stats': all_stats}
        else:
            match_stats = {'flashscore_id': match_id, 'round': round_number, 'date': date, 'teams': teams}
        matches_stats.append(match_stats)
    return matches_stats
