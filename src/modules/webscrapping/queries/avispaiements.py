from datetime import datetime
import logging
import requests
from src.modules.storage.common import save_file, verify_file_exist
import src.config as config

lg = logging.getLogger()
lg.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s;")


async def fetch_avps_list(sessionID: str, empId: str, ref_date: datetime) -> dict:
    cookies = dict(JSESSIONID=sessionID)
    r = requests.post(config.VERIFID_URL + str(empId), cookies=cookies)

    form_data = {
        "pageSize": "2500",
        "pageNumber": "1",
        "sortIndex": "3",
        "ascending": "false",
        "empId": "",
        "annee": "0",
        "mois": "0",
    }
    r = requests.post(config.AVP_URL, cookies=cookies, data=form_data)

    if r.ok == False or r.status_code != 200:
        lg.error(f"Échec de la requête avec le code {r.status_code}")
        raise Exception("La requête d'extraction des avis de paiement à échouée")
    if r.text.startswith("\n\n\n"):
        r = requests.post(config.AVP_URL, cookies=cookies, data=form_data)
        if r.text.startswith("\n\n\n"):
            raise Exception("La requête d'extraction des avis de paiement  a échouée")

    # Récupérer les données
    avps_data = r.json()
    if isinstance(avps_data, dict) and "items" in avps_data:
        avps_data = avps_data["items"]

    # Dédoublonnage des AVPs basé sur l'ID
    seen_ids = set()
    unique_avps = []
    for avp in avps_data:
        if isinstance(avp, str):
            lg.warning(f"AVP inattendu (string): {avp}")
            continue

        avp_id = avp.get("id")
        if not avp_id:
            lg.warning(f"AVP sans ID: {avp}")
            continue

        date_avp_str = avp.get("date")
        if not date_avp_str:
            lg.warning(f"AVP sans date: {avp}")
            continue

        date_avp = datetime.strptime(date_avp_str, "%d/%m/%Y")
        if not date_avp:
            lg.warning(f"Format de la date invalide: {date_avp_str}")
            continue

        if date_avp <= ref_date:
            continue

        if avp_id not in seen_ids:
            seen_ids.add(avp_id)
            unique_avps.append(avp)

    return unique_avps


async def get_entreprise_avps_pdf(
    sessionID: str, empId: str, siret: str, avps: dict
) -> dict:
    save_path = "data/sylae/avps/" + siret
    delta_save_path = "data/sylae/avps_delta/" + siret
    cookies = dict(JSESSIONID=sessionID)
    r = requests.post(config.VERIFID_URL + str(empId), cookies=cookies)

    # Log des AVPs existants avant traitement
    existing_in_avps = set()
    existing_in_delta = set()
    duplicates = set()

    pdf_contents = []  # Liste pour stocker les contenus PDF avec leurs métadonnées

    for avp in avps:
        avp_file = save_path + "/" + str(avp["id"]) + ".pdf"
        delta_file = delta_save_path + "/" + str(avp["id"]) + ".pdf"
        pdf_info = {"id": avp["id"]}

        if await verify_file_exist(avp_file):
            existing_in_avps.add(avp["id"])
            with open(avp_file, "rb") as f:
                pdf_info["content"] = f.read()
            pdf_info["delta"] = False
            pdf_contents.append(pdf_info)
            continue

        if await verify_file_exist(delta_file):
            existing_in_delta.add(avp["id"])
            with open(delta_file, "rb") as f:
                pdf_info["content"] = f.read()
            pdf_info["delta"] = True
            pdf_contents.append(pdf_info)
            continue

        # Téléchargement du nouveau PDF
        form_data = {
            "dispatchMethod": "download",
            "ignore_no_cache": "true",
            "id": avp["id"],
        }
        r = requests.get(config.PDF_AVP_URL, cookies=cookies, params=form_data)

        if r.ok == False or r.status_code != 200:
            raise Exception(
                "La requête d'extraction des PDFs a été refusée par le serveur"
            )
        if r.text.startswith("\n\n\n"):
            r = requests.get(config.PDF_AVP_URL, cookies=cookies, params=form_data)
            if r.text.startswith("\n\n\n"):
                raise Exception("La requête d'extraction des PDFs a échouée")

        lg.info(f"Téléchargement AVP {avp['id']} dans delta_save_path")
        pdf_content = r.content
        await save_file(delta_save_path, delta_file, pdf_content)
        pdf_info["content"] = pdf_content
        pdf_info["delta"] = True
        pdf_contents.append(pdf_info)

    duplicates = existing_in_avps.intersection(existing_in_delta)
    if duplicates:
        lg.warning(f"AVPs présents dans les deux dossiers: {duplicates}")

    lg.info(f"Stats finales:")
    lg.info(f"- AVPs dans le dossier avps: {len(existing_in_avps)}")
    lg.info(f"- AVPs dans le dossier delta: {len(existing_in_delta)}")
    lg.info(f"- AVPs en double: {len(duplicates)}")

    return pdf_contents  # Retourne la liste des PDFs avec leurs métadonnées et contenus


async def get_entreprise_avps_pdf_memory(
    sessionID: str, empId: str, siret: str, avps: dict
) -> dict:
    """
    Récupère les PDFs des AVPs d'une entreprise directement en mémoire sans stockage local.

    Args:
        sessionID: ID de session pour l'API
        empId: ID de l'entreprise
        siret: SIRET de l'entreprise
        avps: Liste des AVPs à télécharger

    Returns:
        Dict contenant les PDFs en mémoire
        Format: {
            'siret_AVP1': {
                'content': bytes_content,
                'delta': bool
            }
        }
    """
    cookies = dict(JSESSIONID=sessionID)
    r = requests.post(config.VERIFID_URL + str(empId), cookies=cookies)

    pdf_contents = {}

    for avp in avps:
        avp_id = str(avp["id"])

        # Téléchargement du PDF
        form_data = {
            "dispatchMethod": "download",
            "ignore_no_cache": "true",
            "id": avp_id,
        }

        r = requests.get(config.PDF_AVP_URL, cookies=cookies, params=form_data)

        if r.ok == False or r.status_code != 200:
            lg.error(
                f"Échec du téléchargement du PDF {avp_id} avec le code {r.status_code}"
            )
            raise Exception(
                f"La requête d'extraction du PDF {avp_id} a été refusée par le serveur"
            )

        if r.text.startswith("\n\n\n") or not r.content:
            r = requests.get(config.PDF_AVP_URL, cookies=cookies, params=form_data)
            if r.text.startswith("\n\n\n") or not r.content:
                lg.error(
                    f"Échec du téléchargement du PDF {avp_id} après nouvelle tentative - Contenu vide"
                )
                raise Exception(
                    f"La requête d'extraction du PDF {avp_id} a échoué - Contenu vide"
                )

        # Vérification de la taille minimale du PDF (un PDF vide fait environ 1KB)
        if len(r.content) < 1024:  # 1KB
            lg.error(
                f"PDF {avp_id} trop petit ({len(r.content)} bytes) - probablement corrompu"
            )
            raise Exception(f"Le PDF {avp_id} semble être corrompu ou vide")

        lg.info(f"PDF {avp_id} téléchargé avec succès ({len(r.content)} bytes)")
        pdf_contents[f"{siret}_{avp_id}"] = {
            "content": r.content,
            "delta": False,  # Sera mis à jour plus tard par refresh_deltas
        }

    return pdf_contents
