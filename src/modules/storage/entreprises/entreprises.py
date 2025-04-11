from datetime import datetime
import json
import logging
import os
import shutil
import src.modules.extract.parsers.constants as constants
from src.modules.storage.common import VerifyIfDirExistElseCreate

lg = logging.getLogger()
lg.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s;')

async def save_entreprises(jsontxt : dict):
    save_path = constants.ENTREPRISE_FOLDER
    list_of_jsons = map(lambda x : save_path + "/" + x , os.listdir(save_path))
    if os.listdir(save_path) != []:
        last_file = max(list_of_jsons, key=os.path.getctime)
        lg.debug("Vérification de la sauvegarde")
        with open(last_file,'r') as fr :
            content = fr.read()
            if content != json.dumps(jsontxt["items"], indent=4) :
                await file_save_entreprises(jsontxt)
            else:
                lg.info("Last Entreprises Data are already at the last version")
            fr.close()
    else:
        await file_save_entreprises(jsontxt)

async def save_new_entreprises(all_ent: list, old_ent: list):
    old_sirets = {str(ent["siret"]) for ent in old_ent} 
    new_ent = []
    for i, ent in enumerate(all_ent):
        if "siret" in ent and str(ent["siret"]) not in old_sirets:
            new_ent.append(ent)

    save_path = constants.NEW_ENTREPRISE_FOLDER
    await VerifyIfDirExistElseCreate(save_path)

    list_of_jsons = map(lambda x : save_path + "/" + x , os.listdir(save_path))
    if os.listdir(save_path) != []:
        for path in list_of_jsons:
            if os.path.isfile(path):
                os.remove(path)

    save_path = constants.ENTREPRISE_FOLDER
    await VerifyIfDirExistElseCreate(save_path)

    list_of_jsons = map(lambda x : save_path + "/" + x , os.listdir(save_path))
    if os.listdir(save_path) != []:
        for path in list_of_jsons:
            if os.path.isfile(path):
                os.remove(path)

    new_entreprise_path = f"{constants.NEW_ENTREPRISE_FOLDER}/new_entreprises_{datetime.now().strftime("%d-%m-%Y")}.json"
    with open(new_entreprise_path,'w') as f :
        f.write(json.dumps(new_ent, indent=4))
        f.close()

    entreprise_path = f"{constants.ENTREPRISE_FOLDER}/new_entreprises_{datetime.now().strftime("%d-%m-%Y")}.json"
    with open(entreprise_path,'w') as f :
        f.write(json.dumps(new_ent, indent=4))
        f.close()


async def save_old_entreprises(items : list):
    save_path = constants.ENTREPRISE_FOLDER
    list_of_jsons = map(lambda x : save_path + "/" + x , os.listdir(save_path))
    if os.listdir(save_path) != []:
        for path in list_of_jsons:
            if os.path.isfile(path):
                os.remove(path)

    old_entreprise_path = f"{constants.ENTREPRISE_FOLDER}/old_entreprises_{datetime.now().strftime("%d-%m-%Y")}.json"
    with open(old_entreprise_path,'w') as f :
        f.write(json.dumps(items, indent=4))
        f.close()

async def clean_all_folders():
    alt_folder = constants.ALTERNANTS_FOLDER
    avp_folder = constants.AVPS_FOLDER
    avp_delta_folder = constants.AVPS_DELTA_FOLDER
    ent_folder = constants.ENTREPRISE_FOLDER
    session_folder = constants.SESSION_FOLDER
    stat_folder = constants.STAT_FOLDER
    if os.path.exists(alt_folder):
        shutil.rmtree(alt_folder)

    if os.path.exists(avp_folder):
        shutil.rmtree(avp_folder)

    if os.path.exists(avp_delta_folder):
        shutil.rmtree(avp_delta_folder)

    if os.path.exists(ent_folder):
        shutil.rmtree(ent_folder)

    if os.path.exists(session_folder):
        shutil.rmtree(session_folder)

    if os.path.exists(stat_folder):
        shutil.rmtree(stat_folder)

    os.makedirs(alt_folder, exist_ok=True)
    os.makedirs(avp_folder, exist_ok=True)
    os.makedirs(avp_delta_folder, exist_ok=True)
    os.makedirs(ent_folder, exist_ok=True)
    os.makedirs(session_folder, exist_ok=True)
    os.makedirs(stat_folder, exist_ok=True)


async def file_save_entreprises(jsontxt : dict):
    stat_path = f"{constants.STAT_FOLDER}/stats_{datetime.now().strftime("%d%m%Y-%H-%M-%S")}.json"
    entreprise_path = f"{constants.ENTREPRISE_FOLDER}/entreprise_{datetime.now().strftime("%d%m%Y-%H-%M-%S")}.json"

    with open(stat_path,'w') as f :
        f.write(json.dumps(jsontxt["countAll"], indent=4))
        f.close()
        lg.debug("Fichier : stats_" + datetime.now().strftime("%d%m%Y-%H-%M-%S") + ".json créé")


    with open(entreprise_path,'w') as f :
        f.write(json.dumps(jsontxt["items"], indent=4))
        f.close()
        lg.debug("Fichier : entreprise_" + datetime.now().strftime("%d%m%Y-%H-%M-%S") + ".json créé")


async def get_stored_entreprises() -> dict :
    save_path = constants.ENTREPRISE_FOLDER
    list_of_jsons = map(lambda x : save_path + "/" + x , os.listdir(save_path))
    if os.listdir(save_path) != []:
        last_file = max(list_of_jsons, key=os.path.getctime)
        lg.debug("Récupération de la sauvegarde")
        with open(last_file,'r') as fr :
            content = fr.read()
            fr.close()
            return json.loads(content)
    else:
        lg.error("No entreprises file saved, save entreprises first")
        raise Exception("No entreprises file saved, save entreprises first")
    
    
async def get_old_entreprises(folder_name: str) -> list :
    result = []
    ent_save_path = f"data/{folder_name}/entreprises"    
    await VerifyIfDirExistElseCreate(ent_save_path)

    jsons = map(lambda x : ent_save_path + "/" + x , os.listdir(ent_save_path))    
    if os.listdir(ent_save_path) != []:
        last_file = max(jsons, key=os.path.getctime)
        with open(last_file,'r') as fr :
            content = fr.read()
            fr.close()
            ent_json = json.loads(content)
            {result.append(ent) for ent in ent_json}
    
    ent_save_path = f"data/{folder_name}/new_entreprises"  
    await VerifyIfDirExistElseCreate(ent_save_path)

    jsons = map(lambda x : ent_save_path + "/" + x , os.listdir(ent_save_path))
    if os.listdir(ent_save_path) != []:
        last_file = max(jsons, key=os.path.getctime)
        with open(last_file,'r') as fr :
            content = fr.read()
            fr.close()
            ent_json = json.loads(content)
            {result.append(ent) for ent in ent_json}
    
    return result