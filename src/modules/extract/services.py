import shutil
import pandas as pd
import asyncio
import os

from src.modules.storage.common import VerifyIfDirExist
from src.modules.extract.parsers.alternantsJSON import alts_parsing
from src.modules.storage.alternants.alternants import get_stored_alts
from src.modules.extract.parsers.alternantsPDF import alternants_extract_pdf
from src.modules.extract.parsers.avisdepaiement import avps_parsing
from src.modules.extract.parsers.entreprises import entreprise_parsing
from src.modules.extract.parsers.utils import (
    delete_all_emptyfolders,
    save_excel,
)

from src.modules.storage.avps.avps import get_stored_avps


async def ents_extract(entreprises_dict: dict):
    df_ent = entreprise_parsing(entreprises_dict)
    return await df_ent


async def avp_extract(entreprises_dict: dict):
    df_avps = pd.DataFrame()
    for entreprise in entreprises_dict:
        avps_dict = await get_stored_avps(entreprise["siret"])
        df_avps = pd.concat(
            [df_avps, pd.DataFrame.from_dict(avps_dict)], ignore_index=True
        )

    if df_avps.empty:
        return df_avps
    
    df_avps = avps_parsing(df_avps)
    return await df_avps


async def export_xlsx_pdfs(
    df_avps: pd.DataFrame,
    df_ent: pd.DataFrame,
    df_alts: pd.DataFrame,
    isNewSiret: bool
):
    excel_base_dir = "data/sylae/excel"
    if isNewSiret:
        excel_base_dir = "data/sylae/excel/new_siret"
    # Nettoyer les dossiers de destination
    execl_delta_dir = f"{excel_base_dir}/delta"
    if os.path.exists(execl_delta_dir):
        shutil.rmtree(execl_delta_dir)
    os.makedirs(execl_delta_dir, exist_ok=True)

    # Supprimer le fichier Excel s'il existe
    if os.path.exists(f"{excel_base_dir}/output.xlsx"):
        os.remove(f"{excel_base_dir}/output.xlsx")

    with pd.ExcelWriter(f"{excel_base_dir}/output.xlsx", engine="xlsxwriter") as writer:
        save_excel(writer, df_avps, "AVPs")
        save_excel(writer, df_ent, "Entreprises")
        save_excel(writer, df_alts, "Alternants")

    await asyncio.gather(
        asyncio.to_thread(
            shutil.copytree,
            "data/sylae/avps_delta",
            f"{excel_base_dir}/delta",
            dirs_exist_ok=True,
        ),
    )
    # Nettoyage en parallèle
    await asyncio.gather(
        asyncio.to_thread(delete_all_emptyfolders, f"{excel_base_dir}/delta"),
    )


async def altsPDF_extract():
    df_alts = alternants_extract_pdf()
    return df_alts


async def altsJSON_extract(entreprises_dict: dict):
    # Créer une liste pour stocker les DataFrames
    dfs = []
    for entreprise in entreprises_dict:
        if await VerifyIfDirExist("data/sylae/alternants/" + entreprise["siret"]):
            alts_dict = await get_stored_alts(entreprise["siret"])
            dfs.append(pd.DataFrame.from_dict(alts_dict))

    # Concaténer une seule fois à la fin
    if dfs:
        df_alts = pd.concat(dfs, ignore_index=True)

        if(df_alts.empty):
            return pd.DataFrame()
        
        df_alts = await alts_parsing(df_alts)
        return df_alts
    
    return pd.DataFrame()
