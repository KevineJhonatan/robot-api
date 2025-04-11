import logging
import requests
from datetime import datetime
import src.config as config
from bs4 import BeautifulSoup as bs4

lg = logging.getLogger()
lg.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s;')

async def get_alternant_etat_presence(sessionID: str, altId: str) -> list:
    cookies = dict(JSESSIONID=sessionID)
    
    r = requests.get(config.ALT_EDP_URL + str(altId) + "&m=&r=1&s=0",
                    cookies=cookies)
    if r.ok == False or r.status_code != 200:
        raise Exception("La requête d'extraction de l'état de présence a échoué")

    soup = bs4(r.text, 'html.parser')
    table = soup.find('table', {"id": "mainList"})

    if not table or table.name != "table":
        raise Exception("La table n'a pas été trouvée")
    
    presence_list = []

    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 8:
            date_saisie_str = cells[1].get_text(strip=True)
            date_fin_reelle = cells[2].get_text(strip=True)
            
            if date_saisie_str and date_fin_reelle:
                try:
                    try:
                        date_saisie = datetime.strptime(date_saisie_str, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        date_saisie = datetime.strptime(date_saisie_str, '%d/%m/%Y')
                    
                    presence_list.append({
                        'date_saisie': date_saisie.strftime('%Y-%m-%d %H:%M:%S'),
                        'date_fin_reelle': date_fin_reelle
                    })
                except ValueError as e:
                    lg.warning(f"Erreur lors du parsing de la date: {e}")
                    continue
    return presence_list
