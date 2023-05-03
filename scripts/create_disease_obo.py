# coding: utf-8
import json

with open("mesh2023.json", "r") as f:
    mesh = json.load(f)

import pronto

diseases = pronto.Ontology()
for item in mesh:
    term = diseases.create_term(item["concept_id"])
    term.name = item["concept_name"]
    for syn in item["synonyms"]:
        term.add_synonym(syn, "EXACT")

for item in mesh:
    for parent in item["parents"]:
        try:
            tp = diseases[parent]
        except KeyError as e:
            continue
        tc = diseases[item["concept_id"]]
        tp.subclasses().add(tc)

with open("diseases.obo", "wb") as f:
    diseases.dump(f, "obo")
