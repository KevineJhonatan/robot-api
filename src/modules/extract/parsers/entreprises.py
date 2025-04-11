import pandas as pd

import src.modules.extract.parsers.constants as constants


async def entreprise_parsing(entreprises_dict : dict):  
    df_ent = pd.DataFrame.from_dict(entreprises_dict)
    # Ne supprimer que les colonnes qui existent
    columns_to_drop = [col for col in constants.IGNORED_COLUMNS_ENT if col in df_ent.columns]
    if columns_to_drop:
        df_ent = df_ent.drop(columns_to_drop, axis=1)
    if constants.CHAMP_DENOMINATION_ENT in df_ent.columns:
        df_ent[constants.CHAMP_DENOMINATION_ENT] = df_ent[constants.CHAMP_DENOMINATION_ENT].str.replace(constants.IGNORED_DENOMINATION_PART,'')
    return df_ent
