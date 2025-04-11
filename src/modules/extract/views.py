from fastapi import APIRouter, status
import asyncio

import logging


from src.modules.extract.services import altsJSON_extract, avp_extract, ents_extract, export_xlsx_pdfs
from src.modules.storage.entreprises.entreprises import get_stored_entreprises


lg = logging.getLogger()
lg.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s;')

router = APIRouter()


@router.get("/xlsx", status_code=status.HTTP_200_OK)
async def to_xlsx(is_new_siret: bool)->str :

    lg.info('Début récupération des relevés de toutes les entreprises')

    entreprises_dict = await get_stored_entreprises()
    
    # Exécuter les extractions en parallèle
    df_futures = await asyncio.gather(
        ents_extract(entreprises_dict),
        avp_extract(entreprises_dict),
        altsJSON_extract(entreprises_dict)
    )

    df_ent, df_avps, df_alts = df_futures
    await export_xlsx_pdfs(df_avps, df_ent, df_alts, is_new_siret)
    return "xlsx => ok"