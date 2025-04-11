import json
import os

import pandas as pd

# Alternant PDF
def get_last_stored_json(path):
    list_of_files = list(map(lambda x : path + "/" + x , os.listdir(path)))
    list_of_jsons = [x for x in list_of_files if x[-5:] == ".json"]
    if os.listdir(path) != []:
        last_file = max(list_of_jsons, key=os.path.getctime)
        with open(last_file,'r') as fr :
            content = fr.read()
            fr.close()
            return json.loads(content)
        
def createjson(path,data):
    with open(path, 'w') as f:
        f.write(json.dumps(data,indent=4))

def logjson(path,message):
    with open(path, "a") as file :
        file.write(message + "\n")

def eliminatespaces(dict):
    dict = [x for x in dict if x]
    dict = [x.strip() for x in dict if x.isspace() == False]
    return dict

def parse_pages(pages,header_end,footer_begin,logsfile,message):
    index_he = 0
    index_fb = -1
    for n in range(len(pages)):
        x = pages[n].extract_text()
        have_he = False
        have_fb = False
        try :
            if n == 0: 
                for he in header_end:
                    if he in x : 
                        index_he = x.index(he)
                        raw = x[index_he+len(he):]
                        have_he = True
                        break
                if not have_he :
                    logjson(logsfile,"headers not found : " + message)
                    raw = x
                for fb in footer_begin:
                    if fb in raw : 
                        index_fb = raw.index(fb)
                        raw = raw[:index_fb]
                        have_fb = True
                        break
                if not have_fb :
                    logjson(logsfile,"footers not found : " + message)
            else:
                for he in header_end:
                    if he in x : 
                        index_he = x.index(he)
                        raw = x[index_he+len(he):]
                        have_he = True
                        break
                
                for fb in footer_begin:
                    if fb in raw : 
                        index_fb = raw.index(fb)
                        raw = raw[:index_fb]
                        have_fb = True
                        break
                raw = x[index_he+len(he):index_fb]
        except Exception as ex:
            logjson(logsfile,message)
    return raw


# AVP
def add_SEPHORA(champ):
    if not champ:
        return champ
    
    if isinstance(champ, float) or (isinstance(champ, str) and len(champ) >= 3 and champ[:3].isdigit()):
        return f"SEPHORA {champ}"
    
    return champ


# Common
def save_excel(writer, df: pd.DataFrame, sheet):
    df.to_excel(writer, sheet_name=sheet, startrow=1, header=False, index=False)
    worksheet = writer.sheets[sheet]

    (max_row, max_col) = df.shape
    column_settings = [{"header": column} for column in df.columns]
    worksheet.add_table(0, 0, max_row, max_col - 1, {"columns": column_settings})

    worksheet.set_column(0, max_col - 1, 25)


def delete_all_jsonfiles(path):
     for path, subdirs, files in os.walk(path):
        for name in files:
            if name[-5:] == ".json":
                os.remove(os.path.join(path, name))

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

    print(deleted)