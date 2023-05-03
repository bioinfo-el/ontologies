# coding: utf-8
import pronto
from functools import lru_cache
import requests
import json
from tqdm import tqdm
from json import JSONDecodeError
import sys
from collections import defaultdict

sys.path.append("../../ipc_library")
import ipc

cvcl = pronto.Ontology("cellosaurus-slim_v0.obo")
ipc.init("*")


def normalize(keyword, entity_type):
    return ipc.normalize(keyword, entity_type)


num_celllines = defaultdict(int)

for term in tqdm(cvcl.terms()):
    new_xrefs = set()
    for xref in term.xrefs:
        if xref.id.startswith("MESH"):
            continue

        new_xrefs.add(xref)

        if xref.id.startswith("NCIt"):
            keyword = xref.description
            keyword = keyword.replace("of the mouse", "of the").replace(
                "of the rat", "of the"
            )
            keyword = keyword.replace("Mouse ", "").replace("Rat ", "")
            disease = normalize(keyword, "disease")
            if disease["name"] is None:
                num_celllines[(keyword, None, 0)] += 1
                continue
            mesh_xref = pronto.Xref(
                id=(disease["ontology"] + ":" + disease["ontology_id"]),
                description=disease["name"],
            )
            num_celllines[
                (keyword, disease["name"], int(disease["score"]))
            ] += 1
            new_xrefs.add(mesh_xref)
    term.xrefs = frozenset(new_xrefs)

with open("cellosaurus-slim.obo", "wb") as f:
    cvcl.dump(f, "obo")
