import requests
from bs4 import BeautifulSoup
import csv
import os
import PySimpleGUI as sg
import datetime as dt

# Gui window
sg.theme('DarkTeal9')


layout = [
    [sg.Text("Enter a date:"), sg.Spin(values=[i for i in range(1, 32)], initial_value=dt.datetime.now().date().day, key="-SPIN-DAY-", size=(5, 1)),
     sg.Text("/"), sg.Spin(values=[i for i in range(1, 13)], initial_value=dt.datetime.now().date().month, key="-SPIN-MONTH-", size=(5, 1)),
     sg.Text("/"), sg.Spin(values=[2023], initial_value=2023, key="-SPIN-YEAR-", size=(5, 1), disabled=True)],
    [sg.Button("OK"), sg.Button("Cancel"), sg.Button("Reset")]
]

window = sg.Window('Simple data entry form',layout)


# scraping the page

def main(page):
    src = page.content
    soup = BeautifulSoup(src, 'lxml')
    matchs_details = []

    championships = soup.find_all("div", {'class': 'matchCard'})

    def get_match_info(championships):

        championship_title = championships.contents[1].find('h2').text.strip()
        all_matches = championships.contents[3].find_all('div', {'class': 'liItem'})
        number_of_matches = len(all_matches)

        for i in range(number_of_matches):
            #  get teams names
            team_A = all_matches[i].find('div', {'class': 'teamA'}).text.strip()
            team_B = all_matches[i].find('div', {'class': 'teamB'}).text.strip()

            # get score
            match_result = all_matches[i].find('div', {'class': 'MResult'}).find_all('span', {'class': 'score'})
            score = f'{match_result[0].text.strip()} - {match_result[1].text.strip()}'

            # match time
            match_time = all_matches[i].find('div', {'class': 'MResult'}).find('span', {'class': 'time'}).text.strip()

            # channel
            try:
                global channel
                channel = all_matches[i].find('div', {'class': 'channel'}).text.strip()
            except:
                channel = '---'

            # match status
            match_status = all_matches[i].find('div', {'class': 'matchStatus'}).text.strip()

            # add match info to matches details
            matchs_details.append({
                'نوع البطولة':championship_title,
                'الفريق الاول':team_A,
                'الفريف الثاني':team_B,
                'ميعاد المبارة':match_time,
               'القناة الناقلة':channel,
                'الحالة':match_status,
                'النتيحة':score
            })

    for i in range(len(championships)):
        get_match_info(championships[i])

    # handling CSV file

    keys = matchs_details[0].keys()

    # creating the file
    global path

    path = rf"{os.path.dirname(os.path.abspath(__file__))}\match-details.csv"
    with open(path, 'w', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(matchs_details)


# clear the input value
def Clear_input():
    for key in values:
        window["-SPIN-DAY-"]('')
        window["-SPIN-MONTH-"]('')
    return None


# controlling the GUI window

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == "Cancel":
        break
    elif event == "OK":
        day = values["-SPIN-DAY-"]
        month = values["-SPIN-MONTH-"]
        year = values["-SPIN-YEAR-"]
        date = f"{month}/{day}/{year}"
        page = requests.get(f'https://www.yallakora.com/match-center/%D9%85%D8%B1%D9%83%D8%B2-%D8%A7%D9%84%D9%85%D8%A8%D8%A7%D8%B1%D9%8A%D8%A7%D8%AA?date={date}#')
        main(page)
        sg.popup(f"file created in {path}")
        break
    elif event == "Reset":
        Clear_input()

window.close()
