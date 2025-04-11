from datetime import datetime
import json
import os
from src.modules.storage.common import VerifyIfDirExistElseCreate

import logging

lg = logging.getLogger()
lg.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s;")


async def file_save_avps(jsontxt: dict, path: str, siret: str):

    lg.debug("Sauvegarde à faire")

    with open(
        path
        + "/avp_"
        + siret
        + "_"
        + datetime.now().strftime("%d%m%Y-%H-%M-%S")
        + ".json",
        "w",
    ) as f:
        f.write(json.dumps(jsontxt, indent=4))
        f.close()
        lg.debug(
            "Fichier : avp_"
            + siret
            + "_"
            + datetime.now().strftime("%d%m%Y-%H-%M-%S")
            + ".json créé"
        )


async def file_update_avps(jsontxt: dict, path: str, siret: str):

    lg.debug("Sauvegarde à faire")

    with open(
        path
        + "/avp_"
        + siret
        + "_"
        + datetime.now().strftime("%d%m%Y-%H-%M-%S")
        + ".json",
        "w",
    ) as f:
        f.write(json.dumps(jsontxt, indent=4))
        f.close()
        lg.debug(
            "Fichier : avp_"
            + siret
            + "_"
            + datetime.now().strftime("%d%m%Y-%H-%M-%S")
            + ".json créé"
        )


async def save_avps(avps: dict, siret: str) -> None:
    save_path = "data/sylae/avps/" + siret
    await VerifyIfDirExistElseCreate(save_path)
    list_of_files = map(lambda x: save_path + "/" + x, os.listdir(save_path))
    list_of_jsons = [x for x in list_of_files if x[-5:] == ".json"]
    if os.listdir(save_path) != []:
        last_file = max(list_of_jsons, key=os.path.getctime)
        lg.debug("Vérification de la sauvegarde")
        with open(last_file, "r") as fr:
            content = fr.read()
            if content != json.dumps(avps, indent=4):
                await file_save_avps(avps, save_path, siret)
            else:
                lg.info("Pas de nouveau avp pour cette entreprise")
            fr.close()
    else:
        await file_save_avps(avps, save_path, siret)


async def update_avps(avps: dict, siret: str) -> None:
    save_path = "data/sylae/avps/" + siret
    await VerifyIfDirExistElseCreate(save_path)
    list_of_files = map(lambda x: save_path + "/" + x, os.listdir(save_path))
    list_of_jsons = [x for x in list_of_files if x[-5:] == ".json"]
    if os.listdir(save_path) != []:
        last_file = max(list_of_jsons, key=os.path.getctime)
        lg.debug("Vérification de la sauvegarde")
        with open(last_file, "r") as fr:
            content = fr.read()
            if content != json.dumps(avps, indent=4):
                await file_update_avps(avps, save_path, siret)
            else:
                lg.info("Pas de nouveau avp pour cette entreprise")
            fr.close()
    else:
        await file_update_avps(avps, save_path, siret)


def complete_pdf_avps(siret) -> bool:
    save_path = "data/sylae/avps/" + siret
    list_of_files = list(map(lambda x: save_path + "/" + x, os.listdir(save_path)))
    list_of_pdf = [x for x in list_of_files if x[-4:] == ".pdf"]
    list_of_jsons = [x for x in list_of_files if x[-5:] == ".json"]

    if list_of_jsons == []:
        print(str(siret) + " : no data for this company, please download avps")
        return False
    else:
        last_file = max(list_of_jsons, key=os.path.getctime)
        with open(last_file, "r") as fr:
            content = fr.read()
            fr.close()
            avps = json.loads(content)
        if len(avps) == len(list_of_pdf):
            return True
        else:
            return False


async def get_stored_avps(siret: str) -> dict:
    save_path = "data/sylae/avps/" + siret
    list_of_jsons = list(map(lambda x: save_path + "/" + x, os.listdir(save_path)))

    list_of_jsons = [x for x in list_of_jsons if x[-5:] == ".json"]
    if os.listdir(save_path) != []:
        last_file = max(list_of_jsons, key=os.path.getctime)
        lg.debug("Récupération de la sauvegarde")
        with open(last_file, "r") as fr:
            content = fr.read()
            fr.close()
            return json.loads(content)
    else:
        lg.error("No avis de paiment file saved, save them first")
        raise Exception("No avis de paiment file saved, save them first")
