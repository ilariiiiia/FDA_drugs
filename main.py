import contextlib
import json

data = []

applicantDict = {}
tradeNameDict = {}
drugNames = []
drugTradenames = []

def filePath(i):
    return f"./assets/drug-label-000{i}-of-0011.json" if i < 10 else f"./assets/drug-label-00{i}-of-0011.json"

def colored(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text} \033[38;2;255;255;255m"

def are_similar(n:str, o:str) -> bool:
    name = n.upper().split(' ')
    other = o.upper().split(' ')
    for elem in ["LTD", "LLC", "CO", "PHARMA", "PHARMACEUTICAL"]:
        with contextlib.suppress(ValueError):
            name.remove(elem)
        with contextlib.suppress(ValueError):
            other.remove(elem)
    return name == other

def get_drug_info():
    with open('assets/drug_info.json') as f:
        return json.load(f)
    
def generate_drug_info():
    for drug in get_drug_info():
        if applicantDict.get(drug["Applicant"]):
            applicantDict[drug["Applicant"]].append(drug)
        else:
            applicantDict[drug["Applicant"]] = [drug]
        if tradeNameDict.get(drug["Trade_Name"]):
            tradeNameDict[drug["Trade_Name"]].append(drug)
        else:
            tradeNameDict[drug["Trade_Name"]] = [drug]

"""
FILE STRUCTURES:

drug_info.json

list[
    object {
        "Ingredient":"BUDESONIDE",
        "DF;Route":"AEROSOL, FOAM;RECTAL",
        "Trade_Name":"UCERIS",
        "Applicant":"SALIX",
        "Strength":"2MG\/ACTUATION",
        "New Drug Application Type":"N",
        "NDA Application Number":205613,
        "Product_No":1,
        "Therapeutic Equivalence (TE) Code":null,
        "Approval_Date":1412640000000,
        "Reference Listed Drug (RLD)":"Yes",
        "Reference Standard (RS)":"Yes",
        "Type":"RX",
        "Applicant_Full_Name":"SALIX PHARMACEUTICALS INC",
        "LOE Date":null,
        "Patent Expiry Date":null,
        "Treatment \/ Indication for Use":null
    }
]

drug-label-00{num}-of-0011.json:

object {
    "meta": useless,
    "results": list[
        {
            useless
            "storage_and_handling": list[str], # NEEDED, THIS IS WHAT WE WANT
            useless
            "indications_and_usage": list[str], # NEEDED, THIS IS WHAT WE WANT
            "set_id": 0xstr,
            "id": 0xstr,
            useless
            "openfda": object{
                "application_number": list[str],
                "brand_name": list[str],
                "generic_name": list[str],
                "manufacturer_name": list[str],
                useless
                ]
            },
            "dosage_and_administration": list[str] # NEEDED, THIS IS WHAT WE WANT
            useless
            }
    ]
}

"""

import time

generate_drug_info()

# result.json is a WAY TOO BIG of a file (over 6GB), so it's impossible to open.
# I will instead loop through the 11 different JSON files and, for each, try to find a match in the drug_info file.
for i in range(11):
    if i: print(f"[INFO] Finished file {i+1} in time {time.time() - startNewFile}")
    startNewFile = time.time()
    print(f"[INFO] Opened file {i+1}")

    with open(filePath(i+1)) as drugLabel:

        drugs = json.load(drugLabel)['results']

        totalDrugs = len(drugs)

        startDrugs = time.time()

        for j, drug in enumerate(drugs):

            startDrug = time.time()

            try:
                brandName = drug['openfda']['brand_name'][0]
            except KeyError:
                print(colored(255, 0, 0, "[ERROR] Could not find brand name"))
                continue

            try:
                manufacturer = drug['openfda']['manufacturer_name'][0]
            except KeyError:
                print(colored(255, 0, 0, "[ERROR] Could not find manufacturer name"))
                continue

            drug_info = get_drug_info()

            for d in drug_info:

                applicant = d['Applicant_Full_Name']
                ingredient = d['Ingredient']
                trade_name = d['Trade_Name']

                if brandName.upper() == trade_name.upper() and are_similar(applicant.upper(), manufacturer.upper()):
                    print(brandName, trade_name, manufacturer, applicant)
                    print("SUCCESS!")
                    # exit(0)
                    with open("matches.json", "r") as file:
                        matches = json.load(file)
                    with open("matches.json", "w") as file:
                        json.dump(matches.append({"drug":drug, "drug_info":drug_info}), file)

            print(colored(0, 255, 255, f"[INFO] Finished drug n {j}/{totalDrugs} in time {round(time.time() - startDrug, 3)}; average: {round((time.time() - startNewFile) / (j+1), 4)}, ETA: {(time.time() - startNewFile) / (j+1) * (totalDrugs-j)}"))