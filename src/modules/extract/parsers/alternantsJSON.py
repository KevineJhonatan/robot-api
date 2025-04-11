import logging
import pandas as pd
import src.modules.extract.parsers.constants as constants

logger = logging.getLogger(__name__)


async def alts_parsing(df_alts: pd.DataFrame):
    """
    Parse et transforme le DataFrame des alternants.

    Args:
        df_alts (pd.DataFrame): DataFrame d'entrée contenant les données des alternants

    Returns:
        pd.DataFrame: DataFrame traité avec colonnes réorganisées et données transformées
    """

    logger.info("Début du traitement des alternants")

    # Suppression des colonnes ignorées
    df_alts = df_alts.drop(constants.IGNORED_COLUMNS_ALT, axis=1)

    # Suppression des lignes Embauche PME
    df_alts.drop(
        df_alts[df_alts["mesure"].str.startswith("Embauche PME")].index, inplace=True
    )

    for index, row in df_alts.iterrows():
        df_alts.at[index, "siret"] = row["employeur"]["siret"]
        df_alts.at[index, "denominationENT"] = row["employeur"]["denomination"]
        montantObtenu = 0
        DSN = False

        for rowDetails in row["details"]:
            if "montant_aide" in rowDetails and rowDetails["montant_aide"] != "":
                montantObtenu += float(rowDetails["montant_aide"])
            if "salaire_brut" in rowDetails:
                if (
                    rowDetails["salaire_brut"] == ""
                    or rowDetails["salaire_brut"] == "0"
                ):
                    DSN = True
        df_alts.at[index, "montantAideObtenu"] = montantObtenu
        if DSN:
            df_alts.at[index, "AnomalieDSN"] = "X"
        else:
            df_alts.at[index, "AnomalieDSN"] = ""

    # Remplacer les valeurs dans la colonne mesure si elle existe
    for old_value, new_value in constants.MESURE_REPLACEMENTS.items():
        df_alts["mesure"] = df_alts["mesure"].str.replace(old_value, new_value)

    df_alts["montantAideObtenu"] = df_alts["montantAideObtenu"].astype(float)

    df_alts["Millésime"] = df_alts["dateDebut"].apply(lambda x: x.split("/")[-1])
    df_alts["AnnéePaiement"] = df_alts["dateDebut"].apply(lambda x: x.split("/")[-1])

    df_alts = df_alts.drop(["employeur"], axis=1)
    # df_alts = df_alts.drop(['details'], axis=1)

    # Réorganiser les colonnes si elles existent
    existing_columns = [
        col for col in constants.colonnes_ordonnees if col in df_alts.columns
    ]
    if existing_columns:
        df_alts = df_alts[existing_columns]

    return df_alts
