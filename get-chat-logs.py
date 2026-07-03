import requests
import json
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os

def get_log_ids(steam_id):
    page = 1
    reached_last_page = False
    tr_ids = []
    try:
        while (not reached_last_page):
            url = f"https://logs.tf/profile/{steam_id}?p={page}"
            response = requests.get(url, allow_redirects=False)
            response.raise_for_status()
            
            html_content = response.text
            if (response.status_code) == 200:
                print(f"Getting log ids for page: {page}")
                soup = BeautifulSoup(html_content, 'html.parser')
                page_tr_ids = [tr.get('id') for tr in soup.find_all('tr') if tr.get('id')]
                tr_ids += page_tr_ids
                page += 1
            else:
                reached_last_page = True
        log_ids = []
        for tr_id in tr_ids:
            log_id = tr_id.split("_")[1]
            log_ids.append(log_id)
        return log_ids

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"The request timed out: {timeout_err}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")

def get_chat_logs(steam_id, log_ids):
    chat_logs = []
    for log_id in log_ids:
        print(f"Getting chat logs for: {log_id}")
        try:
            url = f"https://logs.tf/{log_id}#{steam_id}"
            response = requests.get(url, allow_redirects=False)
            response.raise_for_status()
            html_content = response.text
            if (response.status_code) == 200:
                soup = BeautifulSoup(html_content, 'html.parser')
                players_in_match = get_players_in_match(soup)
                table = soup.find('table', id='chat')
                for tr in table.find_all('tr'):
                    tds = tr.find_all('td')
                    row_data = [td.get_text(strip=True) for td in tds]
                    player_id = "id_not_found"
                    for player in players_in_match:
                        #print (row_data[1])
                        #print (player["matchPlayerName"])
                        if row_data[1] == player["matchPlayerName"]:
                            player_id = player["matchPlayerId"]
                            #break       
                    chat_log_obj = {
                        "team": row_data[0],
                        "playerName": row_data[1],
                        "playerSteamId": player_id,
                        "chatLog": row_data[2],
                        "matchId": log_id
                    }
                    #print(chat_log_obj)
                    chat_logs.append(chat_log_obj)

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"The request timed out: {timeout_err}")
        except requests.exceptions.RequestException as err:
            print(f"An error occurred: {err}")
    return chat_logs

def get_players_in_match(soup):
    
    players = []
    player_tds = soup.find_all('td', class_='log-player-name')
    for td in player_tds:
        #print(td)
        a_tags = td.find_all('a', class_='dropdown-toggle')
        if a_tags:
            player_name = a_tags[0].get_text()
            #print(player_name)
        li_tags = td.find_all('li')
        if li_tags:
            li_tag = li_tags[0]
            li_a_tags = li_tag.find_all('a')
            if li_a_tags:
                li_a_tag = li_a_tags[0]
                player_id_link = li_a_tag['href']
                player_id = player_id_link.split("e/")[1]
                #print(player_id)
            player_obj = {
                "matchPlayerName":player_name,
                "matchPlayerId":player_id
            }
            players.append(player_obj)
            #print(player_obj)
    return players

def gen_csv_sheet(chat_logs, steam_id):
    today = datetime.today().strftime('%d-%m-%Y')
    file_name = f"chat_logs_{steam_id}_{today}"
    print(f"Dumping chat logs to file: {file_name}")
    
    curr_local_path = os.path.dirname(os.path.realpath(__file__))
    chat_log_file = os.path.join(curr_local_path, file_name)
    with open('{}.csv'.format(chat_log_file), 'w', newline='', encoding='utf-8') as output_file:
        csv.excel.delimiter = ';'
        writer = csv.writer(output_file, dialect=csv.excel)
        writer.writerow(["Team", "Player Name", "Steam Id", "Chat Log", "Match Id"])
        for log in chat_logs:
            writer.writerow([log["team"], log["playerName"], log["playerSteamId"], log["chatLog"], log["matchId"]])
    print("Done")

def main():
    #runtime variables
    steam_id = "76561198085860792" #ksz
    
    log_ids = get_log_ids(steam_id)
    chat_logs = get_chat_logs(steam_id, log_ids)
    gen_csv_sheet(chat_logs, steam_id)

if __name__ == "__main__":
    main()
