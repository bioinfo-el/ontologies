# coding: utf-8
import pronto
from functools import lru_cache
import requests
import json
from tqdm import tqdm
from json import JSONDecodeError

cvcl = pronto.Ontology("cellosaurus-slim_3.obo")


def normalize(keyword, entity_type):
    raise NotImplementedError


for term in tqdm(cvcl.terms()):
    new_xrefs = set()
    for xref in term.xrefs:
        new_xrefs.add(xref)
        if xref.id.startswith("NCIt"):
            keyword = xref.description
            keyword = keyword.replace("of the mouse", "of the").replace(
                "of the rat", "of the"
            )
            keyword = keyword.replace("Mouse ", "").replace("Rat ", "")
            disease = normalize(keyword, "disease")
            if "concept_name" not in disease:
                continue
            mesh_xref = pronto.Xref(
                id=(disease["concept_source"] + ":" + disease["concept_id"]),
                description=disease["concept_name"],
            )
            new_xrefs.add(mesh_xref)
    term.xrefs = frozenset(new_xrefs)

with open("cellosaurus-slim.obo", "wb") as f:
    cvcl.dump(f, "obo")
