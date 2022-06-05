# coding: utf-8
import pronto

bto = pronto.Ontology("BTO.obo")
bto.metadata.subsetdefs = frozenset(
    {
        pronto.Subset(name=x, description=x)
        for x in ["tissue", "cell_type", "cell_line"]
    }
)
cvcl = pronto.Ontology("cellosaurus-slim.obo")
# Any BTO ids found as xrefs in CVCL are put into this set
bto_celllines = set()
for term in cvcl.terms():
    for xref in term.xrefs:
        if xref.id.startswith("BTO"):
            bto_celllines.add(xref.id)


def is_cellline(term):
    return ("cell line" in term.name) or (term.id in bto_celllines)


def is_celltype(concept):
    if (
        ("cell" in term.name)
        or ("cyte" in term.name)
        or term.name.endswith("phage")
        or term.name.endswith("neuron")
    ):
        return True
    if len(term.name) >= 5 and term.name.endswith("blast"):
        return True
    for syn in map(lambda x: x.description, term.synonyms):
        if ("cell" in syn) or ("cyte" in syn):
            return True
        if len(syn) >= 5 and syn.endswith("blast"):
            return True
        if syn.endswith("phage"):
            return True
    return False


for term in bto.terms():
    if is_cellline(term):
        term.subsets = frozenset({"cell_line"})
    elif is_celltype(term):
        term.subsets = frozenset({"cell_type"})
    else:
        term.subsets = frozenset({"tissue"})

print(
    "Number of cell lines in BTO: ",
    len([term for term in bto.terms() if "cell_line" in term.subsets]),
)
print(
    "Number of cell type in BTO: ",
    len([term for term in bto.terms() if "cell_type" in term.subsets]),
)
print(
    "Number of tissues in BTO: ",
    len([term for term in bto.terms() if "tissue" in term.subsets]),
)
with open("bto-refined.obo", "wb") as f:
    bto.dump(f, "obo")
