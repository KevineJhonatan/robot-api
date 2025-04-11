import logging
import requests
import src.config as config

lg = logging.getLogger()
lg.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s;')

async def get_alternant_datas(sessionID : str, empId : str) -> dict :
    lg.info("Récupération des alterntants de l'entreprise")
    cookies = dict(JSESSIONID=sessionID)
    r = requests.post(config.VERIFID_URL + str(empId),
                      cookies=cookies)

    form_data = {"pageSize":"2500","pageNumber":"1","sortIndex":"1","ascending":"true"}
    r = requests.post(config.ALTS_URL,
                      cookies=cookies, data=form_data)

    if r.ok == False or r.status_code != 200:
        raise Exception("La requête d'extraction des alternants à échouée")
    lg.info("Récupération réussie")
    return r.json()
