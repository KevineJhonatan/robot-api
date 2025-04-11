from datetime import datetime, timedelta
import json
import logging
import os
from typing import Optional
#import shutil
from src.modules.storage.common import VerifyIfDirExistElseCreate
import src.modules.extract.parsers.constants as constants

lg = logging.getLogger()
lg.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s;')

async def cache_session(sessionId : str, expiration : str):
    #Création de tous les dossiers necessaire
    if not os.path.exists(f"{constants.SESSION_FOLDER}/{constants.SESSION_FILENAME}"):
        await VerifyIfDirExistElseCreate(constants.ENTREPRISE_FOLDER)
        await VerifyIfDirExistElseCreate(constants.NEW_ENTREPRISE_FOLDER)
        await VerifyIfDirExistElseCreate(constants.SESSION_FOLDER)
        await VerifyIfDirExistElseCreate(constants.ALTERNANTS_FOLDER)
        await VerifyIfDirExistElseCreate(constants.AVPS_FOLDER)
        await VerifyIfDirExistElseCreate(constants.AVPS_DELTA_FOLDER)
        await VerifyIfDirExistElseCreate(constants.EXCEL_FOLDER)
        await VerifyIfDirExistElseCreate(constants.STAT_FOLDER)

    expiration = (datetime.now() + timedelta(minutes=15)).strftime("%d%m%Y-%H-%M-%S")
    session = {"SessionId" : sessionId, "Expired" : expiration}    
    file_path = f"{constants.SESSION_FOLDER}/{constants.SESSION_FILENAME}"

    with open(file_path,'w') as fw :
        fw.write(json.dumps(session, indent=4, default=str))
        fw.close()
        
async def get_cached_session() -> Optional[str] : 
    file_path = f"{constants.SESSION_FOLDER}/{constants.SESSION_FILENAME}"
    if os.path.exists(file_path):
        with open(file_path,'r') as fr :
            content = json.loads(fr.read())
            if datetime.strptime(content["Expired"],"%d%m%Y-%H-%M-%S") < datetime.now():
                return None
            else:
                return content["SessionId"]
    else:
        return None