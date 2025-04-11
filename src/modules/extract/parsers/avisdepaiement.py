import pandas as pd

from src.modules.extract.parsers.utils import add_SEPHORA

async def avps_parsing(df_avps : pd.DataFrame):  

    # Supprimer la colonne rib si elle existe
    if "rib" in df_avps.columns:
        df_avps = df_avps.drop(["rib"], axis=1)
    

    df_avps.loc[df_avps["delta"] == True, "lien"] = "=HYPERLINK(\"delta/" + df_avps['siret'].astype(str) + '/' + df_avps['id'].astype(str) + '.pdf")'
    df_avps.loc[df_avps["delta"] != True, "lien"] = "=HYPERLINK(\"data/" + df_avps['siret'].astype(str) + '/' + df_avps['id'].astype(str) + '.pdf")'
    df_avps = df_avps.drop(["delta"], axis=1)

    df_avps["montant"] = df_avps["montant"].str.replace('\xa0', '')
    df_avps["montant"] = df_avps["montant"].str.replace(',', '.')
    df_avps["montant"] = df_avps["montant"].astype(float)


    df_avps.loc[df_avps["siret"].fillna('').str.startswith('393712286'), "employeur"] = df_avps["employeur"].apply(add_SEPHORA)
    df_avps['date'] = pd.to_datetime(df_avps['date'],  format='%d/%m/%Y')
    return df_avps