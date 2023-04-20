import contextlib
import json
import csv

data = []

applicantDict: object = {}
matches = []

def filePath(i):
    return f"./assets/drug-label-000{i}-of-0011.json" if i < 10 else f"./assets/drug-label-00{i}-of-0011.json"

def colored(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text} \033[38;2;255;255;255m"

def minimize(name: str) -> str:
    namelist = name.upper().split(' ')
    for elem in ["LTD", "LLC", "CO", "INC", "INC.", "PHARMA", "PHARMACEUTICAL", "CORP", "COMPANY", "AND", "&", "SUBSIDIARY", "OF", "CORPORATION", "CORP."]:
        with contextlib.suppress(ValueError):
            namelist.remove(elem)
    return '_'.join(namelist)

def are_similar(n:str, o:str) -> bool:
    return minimize(n) == minimize(o) or minimize(o).startswith(minimize(n)) or minimize(o).endswith(minimize(n))

def get_drug_info():
    with open('assets/drug_info.json') as f:
        return json.load(f)
    
def generate_drug_info():

    for drug in get_drug_info():

        minName = minimize(drug["Applicant"])

        if applicantDict.get(minName):
            applicantDict[minName].append(drug)
            
        else:
            applicantDict[minName] = [drug]

def generate_matches_csv():
    with open('matches.json', 'r') as f:
        matches = json.load(f)

    with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # header
        writer.writerow(list(matches[0].keys()))
        
        for item in matches:
            res = []
            for k in item.keys():
                value = item[k]
                if isinstance(value, str):
                    value = value.encode('utf-8', errors='replace').decode('utf-8')
                res.append(item[k])
            writer.writerow(res)

"""
FILE STRUCTURES:

drug_info.json

list[
    object {
        "Ingredient":"BUDESONIDE",
        "DF;Route":"AEROSOL, FOAM;RECTAL",
        "Trade_Name":"UCERIS",
        "Applicant":"SALIX",
        "Strength":"2MG/ACTUATION",
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
        "Treatment / Indication for Use":null
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

"""
HOW THIS WORKS

I have created a dictionary, applicantDict, which has as keys the "minified" version of the applicant's name,
and as values a list of the drugs that have that applicant's name.

For each file, I will then search whether the applicantDict contains the applicant's name in the keys, and if so,
check whether the corresponding drug is the same as the one for the file. If it is, add both to a list called matches.

"""

startTime = time.time()
failedName = 0
notMatch = 0
foundNotMatch = 0
startNewFile = startTime
for i in range(11):
    if i: print(f"[INFO] Finished file {i+1} in time {time.time() - startNewFile}")
    print(f"[INFO] Opening file {i+1}")
    matchesFound = 0

    with open(filePath(i+1)) as drugLabel:

        drugs = json.load(drugLabel)['results']

        totalDrugs = len(drugs)

        startNewFile = time.time()

        for j, drug in enumerate(drugs):

            try:
                brandName = drug['openfda']['brand_name'][0]
            except KeyError:
                failedName += 1
                notMatch += 1
                print(colored(255, 0, 0, "[ERROR] Could not find brand name"))
                continue

            try:
                manufacturer = drug['openfda']['manufacturer_name'][0]
            except KeyError:
                failedName += 1
                notMatch += 1
                print(colored(255, 0, 0, "[ERROR] Could not find manufacturer name"))
                continue

            applicantList:list = applicantDict.get(minimize(manufacturer), [])

            foundMatch = False

            for infoDrug in applicantList:
                if are_similar(infoDrug['Trade_Name'], brandName):
                    newDrug = infoDrug
                    newDrug['Dosage_and_administration'] = drug.get('dosage_and_administration', ['No dosage information found'])[0]
                    newDrug['Indications_and_usage'] = drug.get('indications_and_usage', ['No Indications and Usage information found'])[0]
                    newDrug['Storage_and_handling'] = drug.get('storage_and_handling', ['No storage and handling information found'])[0]
                    matches.append(newDrug)
                    matchesFound += 1
                    foundMatch = True
                    print(colored(0, 255, 0, "[SUCCESS] Found a match!"))

            if not foundMatch:
                notMatch += 1
                foundNotMatch += 1

            timeFile = time.time() - startNewFile
            print(f"[INFO] Finished drug n {j+1}/{totalDrugs}; average: {round(timeFile / (j+1), 6)}")
        
        print(colored(0, 255, 0, f"[INFO] Found {matchesFound} matches"))

print(f"Found {len(matches)} matches in total in {time.time() - startTime} s")
print(colored(255, 0, 0, f"Failed to find name: {failedName}"))
print(f"Not a match: {notMatch}")
print(f"Not a match but found its name: {foundNotMatch}")

with open('matches.json', 'w') as f:
    json.dump(matches, f, indent=4)

generate_matches_csv()