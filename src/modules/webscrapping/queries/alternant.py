import logging
import requests
import src.config as config
from bs4 import BeautifulSoup as bs4

lg = logging.getLogger()
lg.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s;')

async def get_alternant(sessionID : str, empId : str, altId : str) -> list :
    lg.info("Récupération des alterntants de l'entreprise")
    cookies = dict(JSESSIONID=sessionID)
    r = requests.post(config.VERIFID_URL + str(empId),
                      cookies=cookies)
    
    r = requests.get(config.ALT_URL + str(altId),
                      cookies=cookies)
    if r.ok == False or r.status_code != 200:
        raise Exception("La requête d'extraction des alternants à échouée")
    

    soup = bs4(r.text,'html.parser')
    table = soup.find('table',{"id":"saisirMois"})

    if not table or table.name != "table" :
        raise Exception("La table n'as pas été trouvé")
    
    results = []

    for row in table.find_all('tr'):
        aux = row.find_all('td')
        if len(aux) >= 6 and aux[0]['headers'][0] == 'mois'  :
            data = {
                "mois": aux[0].get_text(strip=True),
                "date_reception": aux[1].get_text(strip=True),
                "salaire_brut": aux[3].get_text(strip=True),
                "montant_aide": aux[4].get_text(strip=True),
                "etat": aux[5].get_text(strip=True)
            }
            results.append(data)
        elif len(aux) >= 5 and aux[0]['headers'][0] == 'mois'  :
            data = {
                "mois": aux[0].get_text(strip=True),
                "nb_absence": aux[1].get_text(strip=True),
                "salaire_brut": aux[2].get_text(strip=True),
                "etat": aux[3].get_text(strip=True)
            }
            results.append(data)
        elif len(aux) >3:
            print("ligne ignorée",row)

    lg.info("Récupération réussie")
    return results
