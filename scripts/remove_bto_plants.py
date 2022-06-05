# THE CODE FOR REMOVING PLANTS AND FUNGI AND STUFF
import pronto
from tqdm import tqdm

distances = {}

diseases = pronto.Ontology(
    "https://raw.githubusercontent.com/bioinfo-el/ontologies/main/obo/disease.obo"
)
# this creates the distance matrix for diseases
for term in tqdm(diseases.terms()):
    distances[(term.name, term.name)] = 0
    for i in range(10):
        for other in term.superclasses(i):
            key = (term.name, other.name)
            if key in distances:
                continue
            distances[key] = -1 * i
        for other in term.subclasses(i):
            key = (term.name, other.name)
            if key in distances:
                continue
            distances[key] = i


# for BTO, superclasses includes part of and subclass relationships
def superclasses(term, depth):
    terms = []
    if depth == 0:
        return terms

    # this code block is for getting "part_of" relationship
    for rel, others in term.relationships.items():
        if rel.name not in ["part of", "derives from/develops from"]:
            continue
        terms += list(others)
        for other in list(others):
            terms += superclasses(other, depth - 1)

    # this code block handles subclass relationships
    others = term.superclasses(distance=1, with_self=False)
    terms += list(others)
    for other in list(others):
        terms += superclasses(other, depth - 1)
    return list(set(terms))


tissues = pronto.Ontology("bto-refined.obo")
for term in tqdm(tissues.terms()):
    distances[(term.name, term.name)] = 0
    for i in range(10):
        for other in superclasses(term, i):
            key = (term.name, other.name)
            if key in distances:
                distances[key] = min(distances[key], i)
            else:
                distances[key] = -1 * i

            rev = tuple(reversed(key))
            if rev in distances:
                distances[rev] = min(distances[rev], i)
            else:
                distances[rev] = i


def distance(t1, t2):
    """
    Distance between two terms in ontology
    If there's no path between the terms then returns None
    Imagine ontology top to bottom (roots are on top),
    this function returns  height(t1)-height(t2)

    distance is 0 if t1==t2
    distance > 0 if t1 is superclass of t2
    distance < 0 if t1 is subclass of t2

    e.g.
    >>> distance('Triple Negative Breast Neoplasms', 'Neoplasms')
    -3
    """
    return distances.get((t2, t1), None)


def to_remove(term) -> bool:
    # removes the term if its one of yuck, or its a descendent of yuck
    # if its a descendent of both yuck and an animal then its not removed
    yuck = ["plant", "fungus", "organism form", "other source"]
    if term.name in yuck:
        return True
    for y in yuck:
        if distance(y, term.name) is not None:
            if (
                distance(y, term.name) < 0
                and distance(term.name, "animal") is None
            ):
                return True
    return False


print("Number of terms before: ", len(tissues))


def copy_term(og_term):
    term = None
    if isinstance(og_term, pronto.relationship.Relationship):
        term = new_tissues.create_relationship(og_term.id)
    else:
        term = new_tissues.create_term(og_term.id)
    for attr in [
        "name",
        "annotations",
        "xrefs",
        "definition",
        "created_by",
        "creation_date",
    ]:
        setattr(term, attr, getattr(og_term, attr))
    for syn in og_term.synonyms:
        term.add_synonym(syn.description, syn.scope, syn.type)
    term.subsets = og_term.subsets


def copy_relations(og_term):
    if not hasattr(og_term, "superclasses"):
        return
    for og_other in og_term.superclasses(distance=1, with_self=False):
        if og_other.id in new_tissues:
            new_tissues[og_term.id].superclasses().add(
                new_tissues[og_other.id]
            )
    new_tissues[og_term.id].relationships = og_term.relationships


new_tissues = pronto.Ontology()
new_tissues.metadata.subsetdefs = frozenset(
    {
        pronto.Subset(name=x, description=x)
        for x in ["tissue", "cell_type", "cell_line"]
    }
)
new_tissues.metadata.synonymtypedefs = tissues.metadata.synonymtypedefs
for _, term in tissues.items():
    if to_remove(term):
        continue
    copy_term(term)
for _, term in tissues.items():
    if to_remove(term):
        continue
    copy_relations(term)

print("Number of terms after: ", len(new_tissues))

with open("new_tissues.obo", "wb") as f:
    new_tissues.dump(f, format="obo")
