### Module extract_data

# AlternantsPDF
## Regex
REGEX_PATTERN_NOM_DOSSIER   = r"M(?:ME|LE)?\s+([A-Z]['A-Z\s-]+)\s+DOSSIER\s+((?:E?[AP])?\d+\s*\d*)"
REGEX_DETECT_PAIEMENT       = r"^Paiement (?:des mois de |du mois de )(?:([A-Z]+(?:/[A-Z]+)*)|(\d{2}/\d{4}|[A-Z]+)) (\d{1,3}(?:\s?\d{3})*,\d{2})$"
REGEX_DETECT_REGULARISATION = r'^(Regularisation du mois de \d{2}\/\d{4}|\bRegulation du mois de [A-Z]+|\bRegulation des mois de [A-Z]+(?:\/[A-Z]+){1,2}|REGUL \d{2}\/\d{4} AURAIT DU PERCEVOIR .+ A PERCU .+) [0-9]{1,3}(?:\s?[0-9]{3})*(?:,[0-9]{2})?$'
REGEX_DETECT_ACOMPTE        = r"^ACOMPTE \d{2}/\d{4} \d+(?:,\d{2})?$"

CAPTURE_DATE = r'((?:0?[1-9]|1[0-2])\/20\d{2}|\d{2}\/\d{4}|(?:JANVIER|FEVRIER|MARS|AVRIL|MAI|JUIN|JUILLET|AOUT|SEPTEMBRE|OCTOBRE|NOVEMBRE|DECEMBRE))'
CAPTURE_MONTANT = r"\b(?:\d{1,3}(?:\s\d{3})*|\d+)(?:,\d{2})?(?=\s*$)"

## Data Paths
SESSION_FOLDER = "data/sylae/pw_session"
SESSION_FILENAME = "sessionID_"
ENTREPRISE_FOLDER = "data/sylae/entreprises"
NEW_ENTREPRISE_FOLDER = "data/sylae/new_entreprises"
ALTERNANTS_FOLDER = "data/sylae/alternants"
AVPS_FOLDER = "data/sylae/avps"
AVPS_DELTA_FOLDER = "data/sylae/avps_delta"
EXCEL_FOLDER = "data/sylae/excel"
STAT_FOLDER = "data/sylae/stats"

PATH_DATA_JSON = "data.json"
PATH_FINAL_JSON = "alts.json"
LOG_FILE = "avps.txt"

## Dict Fields
CHAMP_SIRET_ENT = "siret"
CHAMP_ID_AVP = "id"



## Parsing data
SEPARATOR = "\n"

FIN_HEADER = ["PAYE"]
DEBUT_FOOTER = ["Pour tout","POUR TOUTE"]

IGNOREDLINES = [
    "Aide Exceptionnelle aux Employeurs d'Apprentis",
    "MINISTERE TRAVAIL PLEIN EMPLOI INSERTION",
    "Aide Unique aux Employeurs d'Apprentis",
    "MINISTERE DU TRAVAIL",
    "TOTAL A PAYER",
    "MONTANT NET PAYE EN VOTRE FAVEUR",
    "Aide Embauche PME","Aide Exceptionnelle aux Employeurs recrutant en Contrat de Professi",
    "TOTAL A RETENIR",
    "MONTANT DU NEGATIF DE LA SERIE PRECEDENTE",
    "MONTANT DU NEGATIF RESTANT",
    "Aide de l'Etat",
    "Aide a l'Embauche des Jeunes",
    "Aide a L'Embauche des Jeunes",
    "MONTANT RETENU SUR LA SERIE EN COURS",
    "VOTRE SITUATION FAIT APPARAITRE",
    "CONSEIL DEPARTEMENTAL D'ILLE ET VILAINE",
    "Contribution forfaitaire RSA du Conseil General d'Ille et Vilaine",
    "Aide Embauche des Travailleurs Handicapes",
    "No RETENUE     TYPE DE RETENUE    REFERENCE RETENUE",
    "ORDRE DE REVERSEMENT"
    ]

# Entreprises

IGNORED_COLUMNS_ENT = ['procedureCollective', 'questionRenseignee', 'allDossierAUEA', 'allDossierCUI', 'hasRevueHab', 'elligibleCA',"empId_Tiers_Dec","empId","empIdNoe"]


## Dict Fields
CHAMP_DENOMINATION_ENT = "denomination"
IGNORED_DENOMINATION_PART = ' (Contrat de prestation)'

## Alternants
IGNORED_COLUMNS_ALT = ["id","etatGestion","numeroVersion","empId","outOfDate","editable","payable","proprietaire","idDipositif","estNeutralise","empPasGestionnaireDuDossier","codeSiteResp","estContratTPE","estContratPremiereEmbauche","estContratEmbauchePME","estContratAUEA","estContratAECA","estContratCPRO","estContratAE","estMesureDSN","blocageSuspension","blocageSuiviDossier","saisieTrimestrielle","changed","errors"]


MESURE_REPLACEMENTS = {
    ' (Apprentissage moins de 250 salaries ET niveau de diplome superieur a 4)': ' (Apprentissage)',
    ' (Contrat professionnalisation moins de 250 salaries ET niveau de diplome superieur a 4)': ' (Professionnalisation)',
    ' (Apprentissage 250 salaries et plus)': ' (Apprentissage)',
    ' (Contrat professionnalisation 250 salaries et plus)': ' (Apprentissage)'
}

colonnes_ordonnees = [
        # Informations d'identification
        "nom",
        "prenom",
        "numeroDossier",
        # Informations temporelles
        "dateDebut",
        "dateFinPrevue",
        "dateFinReelle",
        "dateFinSupposee",
        "last_date",
        # Informations sur l'entreprise
        "siret",
        "denominationENT",
        # Informations sur l'état et les détails
        "mesure",
        "etatSuivi",
        "listeMotifsRupture",
        "blocageMotifRupture",
        "AnomalieDSN",
        # Informations financières et administratives
        "montantAideObtenu",
        "Millésime",
        "dernierJourMoisFinPEC",
        "details",
        "AnnéePaiement",
    ]