import os
import json

database = {"domains": []}

database_info = {}
total_count = 0

for i in range(1, 21, 1):
    if i < 10:
        domain = '0' + str(i)
    else:
        domain = str(i)

    filename = f"./year/1949_{domain}.json" # replace with the actual path to your year folder
    with open(filename, "r") as file:
        data = json.load(file)
        domain = {"domain_id": data["domain"], "domain_total_count": data["domain_total_count"], "domain_yearly_count": data["domain_yearly_count"]}
        database["domains"].append(domain)
        total_count += data['domain_total_count']

database_info['database'] = "eurlex"
database_info['url'] = "https://eur-lex.europa.eu/browse/directories/legislation.html"
database_info['total_count'] = total_count
database_info['record_distribution'] = database

with open("./database.json", "w") as file:
    json.dump(database_info, file)