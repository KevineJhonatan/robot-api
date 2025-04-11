import os
from src.modules.storage.common import VerifyIfDirExistElseCreate
import src.modules.extract.parsers.constants as constants
from datetime import datetime, timedelta
import json
from typing import Optional
import shutil
import logging

lg = logging.getLogger()
lg.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s;')

async def save_alts(alternants : dict, siret : str) -> None:
    save_path = f"{constants.ALTERNANTS_FOLDER}/{siret}"
    await VerifyIfDirExistElseCreate(save_path)
    list_of_files = map(lambda x : save_path + "/" + x , os.listdir(save_path))
    list_of_jsons = [x for x in list_of_files if x[-5:] == ".json"]
    if os.listdir(save_path) != []:
        last_file = max(list_of_jsons, key=os.path.getctime)
        lg.debug("Vérification de la sauvegarde")
        with open(last_file,'r') as fr :
            content = fr.read()
            if content != json.dumps(alternants, indent=4) :
                await file_save_alts(alternants,save_path,siret)
            else:
                lg.info("Pas de nouveau avp pour cette entreprise")
            fr.close()
    else:
        await file_save_alts(alternants,save_path,siret)



async def file_save_alts(jsontxt : dict, path : str, siret : str):

        lg.debug("Sauvegarde à faire")

        with open(path + '/alts_' + siret +'_' + datetime.now().strftime("%d%m%Y-%H-%M-%S") + '.json','w') as f :
            f.write(json.dumps(jsontxt, indent=4))
            f.close()
            lg.debug("Fichier : alts_" + siret +'_' + datetime.now().strftime("%d%m%Y-%H-%M-%S") + ".json créé")



async def get_stored_alts(siret : str) -> dict :
    save_path = f"{constants.ALTERNANTS_FOLDER}/{siret}"
    list_of_jsons = list(map(lambda x : save_path + "/" + x , os.listdir(save_path)))

    list_of_jsons = [x for x in list_of_jsons if x[-5:] == ".json"]
    if os.listdir(save_path) != []:
        last_file = max(list_of_jsons, key=os.path.getctime)
        lg.debug("Récupération de la sauvegarde")
        with open(last_file,'r') as fr :
            content = fr.read()
            fr.close()
            return json.loads(content)
    else:
        lg.error("No alternant file saved, save them first")
        raise Exception("No alternant file saved, save them first")