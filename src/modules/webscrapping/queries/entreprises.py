import logging
from typing import Optional
import requests
import src.config as config

lg = logging.getLogger()
lg.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s;')


async def get_entreprises_list(sessionID : str) -> dict:
    lg.info("Récupération des entreprises du compte")

    form_data = {"pageSize":"2500","pageNumber":"1","sortIndex":"1","ascending":"true"}
    cookies = dict(JSESSIONID=sessionID)
    r = requests.post(config.ENTREPRISES_URL,
                      cookies=cookies, data=form_data)

    if r.ok == False or r.status_code != 200:
        raise Exception("La requête d'extraction des entreprises a été refusée par le serveur")
    if r.text.startswith("\n\n\n"):
        r = requests.post(config.ENTREPRISES_URL,
                      cookies=cookies, data=form_data)
        if r.text.startswith("\n\n\n"):
            raise Exception("La requête d'extraction des entreprises a échouée, Vérifiez le MDP")
    lg.info("Récupération réussie")
    return r.json()