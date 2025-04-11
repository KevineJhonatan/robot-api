import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

from src.modules.storage.common import verify_file_exist

lg = logging.getLogger()
lg.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s;")


async def delta_to_data(avps: dict, siret: str):
    save_path = "data/sylae/avps/" + siret
    delta_save_path = "data/sylae/avps_delta/" + siret

    for avp in avps:
        if "delta" in avp:
            if avp["delta"] == True:
                avp_file = save_path + "/" + str(avp["id"]) + ".pdf"
                delta_file = delta_save_path + "/" + str(avp["id"]) + ".pdf"

                if await verify_file_exist(delta_file):
                    shutil.move(delta_file, avp_file)
                    avp["delta"] = False
    return avps


async def refresh_deltas_in_avps(siret: str, avps: dict):
    save_path = "data/sylae/avps/" + siret
    delta_save_path = "data/sylae/avps_delta/" + siret

    for avp in avps:
        avp_file = save_path + "/" + str(avp["id"]) + ".pdf"
        delta_file = delta_save_path + "/" + str(avp["id"]) + ".pdf"

        if await verify_file_exist(avp_file):
            if not "delta" in avp:
                print(None, "->", "False")
            elif avp["delta"] != False:
                print(avp["delta"], "->", "False")
            avp["delta"] = False
            if await verify_file_exist(delta_file):
                os.remove(delta_file)
                print(delta_file, "removed", "!")

        elif await verify_file_exist(delta_file):
            if not "delta" in avp:
                print(None, "->", "True")
            elif avp["delta"] != True:
                print(avp["delta"], "->", "True")
            avp["delta"] = True

        else:
            avp["delta"] = True
    return avps


async def refresh_deltas_in_avps_bydate(
    siret: str, avps: dict, reference_date: datetime
):
    """
    Met à jour les AVPs en fonction de leur date de création.
    Les AVPs plus récents que la date de référence sont placés dans delta,
    les autres dans data.

    Args:
        siret: SIRET de l'entreprise
        avps: Liste des AVPs à traiter
        reference_date: Date de référence pour le tri
    """
    save_path = "data/sylae/avps/" + siret
    delta_save_path = "data/sylae/avps_delta/" + siret

    for avp in avps:
        avp_file = save_path + "/" + str(avp["id"]) + ".pdf"
        delta_file = delta_save_path + "/" + str(avp["id"]) + ".pdf"

        # Convertir la date de l'AVP en datetime
        avp_date = datetime.strptime(avp.get("date", ""), "%d/%m/%Y")

        # Si le fichier existe dans data
        if await verify_file_exist(avp_file):
            # Si l'AVP est plus récent que la date de référence, on le déplace dans delta
            if avp_date > reference_date:
                os.makedirs(os.path.dirname(delta_file), exist_ok=True)
                shutil.move(avp_file, delta_file)
                avp["delta"] = True
            else:
                avp["delta"] = False
                if await verify_file_exist(delta_file):
                    os.remove(delta_file)

        # Si le fichier existe dans delta
        elif await verify_file_exist(delta_file):
            # Si l'AVP est plus ancien que la date de référence, on le déplace dans data
            if avp_date <= reference_date:
                os.makedirs(os.path.dirname(avp_file), exist_ok=True)
                shutil.move(delta_file, avp_file)
                avp["delta"] = False
            else:
                avp["delta"] = True

        # Si le fichier n'existe ni dans data ni dans delta
        else:
            # On marque comme delta si plus récent que la date de référence
            avp["delta"] = avp_date > reference_date

    return avps


def delete_all_emptyfolders(path):

    deleted = set()

    for current_dir, subdirs, files in os.walk(path, topdown=False):

        still_has_subdirs = False
        for subdir in subdirs:
            if os.path.join(current_dir, subdir) not in deleted:
                still_has_subdirs = True
                break

        if not any(files) and not still_has_subdirs:
            os.rmdir(current_dir)
            deleted.add(current_dir)
    if deleted != set():
        print(deleted)