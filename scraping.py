import requests
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://results.eci.gov.in/PcResultGenJune2024/"
url = base_url + "index.htm"
response = requests.get(url)
response.encoding = 'utf-8'

soup = BeautifulSoup(response.text, 'html.parser')
main_data = []
state_list = soup.find('select')  

data_frames = {}
for state in state_list:
    if (str(state).replace('<option value="', "").split('"')[0]).strip() == "":
        continue

    url_state_code = "partywiseresult-{}.htm".format((str(state).replace('<option value="', "").split('"')[0]))
    state_name = (str(state).split('>')[1].split('<')[0])
    state_url = base_url + url_state_code


    state_response = requests.get(state_url)
    state_response.encoding = 'utf-8'
    state_soup = BeautifulSoup(state_response.text, 'html.parser')
    state_table = state_soup.find("table")

    if state_table is None:
        continue

    state_data = []
    for row in state_table.find_all('tr'):
        links = state_soup.find_all('a', href=True)


        cols = [cell.text.strip() for cell in row.find_all(['td', 'th'])]
        if cols[0] in ["Total", "Party"]:
            continue
        del cols[2:4]

        for i, link in enumerate(links):
            if (str(link).split('href')[1].split('>')[0][2:-1].split('-')[0] == 'partywisewinresult'):
                constituency_url =  base_url + (str(link).split('"')[1])


                constituency_response = requests.get(constituency_url)
                constituency_response.encoding = 'utf-8'
                constituency_soup = BeautifulSoup(constituency_response.text, 'html.parser')

                for cons_row in constituency_soup.find_all('tr'):
                    cons_cols = [cons_cell.text.strip() for cons_cell in cons_row.find_all(['td'])]
                    if cons_cols == []: continue
                    main_data.append(cols + cons_cols[1:] + [state_name])
                    
        state_data.append(cols)


header = ['Party Name', 'Total Winning', 'Constituency', 'Winning Candidate', 'Total Votes', 'Margin', 'State']

linked_df = pd.DataFrame(main_data)

linked_df.to_csv('election_data.csv', header=header)
