import re
import pandas as pd
import os
from pypdf import PdfReader

import src.modules.extract.parsers.constants as constants
import src.modules.extract.parsers.utils as utils


def alternants_extract_pdf():
    ents = utils.get_last_stored_json(constants.ENTREPRISE_FOLDER)
    #data = []
    alts = []

    for ent in ents:
        
        save_path_avps = f"{constants.AVPS_FOLDER}/{ent[constants.CHAMP_SIRET_ENT]}"
        delta_save_path_avps = f"{constants.AVPS_DELTA_FOLDER}/{ent[constants.CHAMP_SIRET_ENT]}"
        
        avps = utils.get_last_stored_json(save_path_avps)
        
        for avp in avps:
            if 'delta' in avp and avp['delta'] == True :
                avp_file = delta_save_path_avps + '/' + str(avp[constants.CHAMP_ID_AVP]) + ".pdf"
            else:
                avp_file = save_path_avps + '/' + str(avp[constants.CHAMP_ID_AVP]) + ".pdf"
            reader = PdfReader(avp_file)
            pages = reader.pages
            raw = utils.parse_pages(
                pages,
                constants.FIN_HEADER,
                constants.DEBUT_FOOTER,
                constants.LOG_FILE,
                avp_file
                )  
            raw = raw.split(constants.SEPARATOR)
            raw = utils.eliminatespaces(raw)
            ignored_line = constants.IGNOREDLINES
            alternant = []
            paiements = []
            paiements_dict = {}
            for line in raw :
                find_nom = re.findall(constants.REGEX_PATTERN_NOM_DOSSIER, line, re.IGNORECASE)
                find_paiement = re.findall(constants.REGEX_DETECT_PAIEMENT,line, re.IGNORECASE)
                find_acompte = re.findall(constants.REGEX_DETECT_ACOMPTE,line, re.IGNORECASE)
                find_regularisation = re.findall(constants.REGEX_DETECT_REGULARISATION,line, re.IGNORECASE)
                if find_nom:
                    if alternant != []:
                        if paiements == []:
                            utils.logjson(constants.LOG_FILE,"fichier bizarre : " + avp_file + "\n" + str(raw))
                        else :
                            for paiement in paiements:
                                paiements_dict["nom"] = alternant[0]
                                paiements_dict["num_dossier"] = alternant[1]
                                paiements_dict["siret_ent"] = alternant[2]
                                paiements_dict["type_versement"] = paiement[0]
                                paiements_dict["montant"] = paiement[2]
                                paiements_dict["date"] = paiement[1]
                                paiements_dict["texte"] = paiement[3]
                                if 'delta' in avp and avp['delta'] == True :
                                    paiements_dict["fichierPDF"] = "=HYPERLINK(\"data/" + alternant[2] + '/' + str(avp[constants.CHAMP_ID_AVP]) + '.pdf")'
                                else :
                                    paiements_dict["fichierPDF"] = "=HYPERLINK(\"delta/" + alternant[2] + '/' + str(avp[constants.CHAMP_ID_AVP]) + '.pdf")'
                                alts.append(paiements_dict)
                            paiements = []
                    nom_prenom, numero_dossier = find_nom[0]
                    numero_dossier = numero_dossier.replace(" ", "")
                    alternant = [nom_prenom.strip(), numero_dossier, ent[constants.CHAMP_SIRET_ENT], avp_file]
                else: 
                    if find_paiement or find_acompte:
                        date = re.findall(constants.CAPTURE_DATE,line, re.IGNORECASE)[0]
                        montant = float(re.findall(constants.CAPTURE_MONTANT,line, re.IGNORECASE)[0].replace(" ","").replace(",","."))
                        paiements.append(["paiement",date,montant,line])    
                    elif  find_regularisation:
                        date = re.findall(constants.CAPTURE_DATE,line, re.IGNORECASE)[0]
                        montant = float("-" + re.findall(constants.CAPTURE_MONTANT,line, re.IGNORECASE)[0].replace(" ","").replace(",","."))
                        paiements.append(["regularisation",date,montant,line])
                        #print("regularisation",date,montant)
                    elif any(words in line for words in ignored_line):
                        pass
                    else:
                        print(line, avp_file)
            #print(raw)
            #data.append(raw)
    # createjson(config.path_data_json,data)
    df_alts = pd.DataFrame()
    df_alts = pd.concat([df_alts,pd.DataFrame.from_dict(alts)], ignore_index= True)
    return df_alts