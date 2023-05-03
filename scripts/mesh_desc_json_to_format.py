# coding: utf-8
import json

subtrees_to_ignore = [
    "C23.550.260",  # death
    "C23.550.288",
    "C23.550.291",  # disease attributes
    "C26.304",  # drowning
]


def is_ignored(tree_number):
    return any(
        [tree_number.startswith(subtree) for subtree in subtrees_to_ignore]
    )


def write_json(obj, filename):
    with open(filename, "w") as f:
        json.dump(obj, f, indent=2)


# Read the input JSON file
with open("desc2023_no_qualifiers_formatted.json", "r") as infile:
    data = json.load(infile)

tree_to_onto = {}
for entry in data:
    for tree_number_entry in entry["treeNumbers"]:
        tree_to_onto[tree_number_entry["treeNumber"]] = entry["id"]

output_data = []
for entry in data:
    tree_numbers = [
        tree_number_entry["treeNumber"]
        for tree_number_entry in entry["treeNumbers"]
    ]

    if all([not tree_number.startswith("C") for tree_number in tree_numbers]):
        continue

    if all([is_ignored(tree_number) for tree_number in tree_numbers]):
        continue

    concept_name = entry["name"]
    concept_id = f"MESH:{entry['id']}"
    synonyms = []

    concepts_to_consider = [
        concept for concept in entry["concepts"] if concept["isPreferred"]
    ]
    for concept in concepts_to_consider:
        for term in concept["terms"]:
            synonyms.append(term["name"])

    # Remove duplicates
    synonyms = list(set(synonyms))

    # Calculate parent tree numbers by removing the last ".xxx" part
    parent_tree_numbers = set()
    for tree_number_entry in entry["treeNumbers"]:
        tree_number = tree_number_entry["treeNumber"]
        parent_tree_number = ".".join(tree_number.split(".")[:-1])
        parent_tree_numbers.add(parent_tree_number)

    parents = set()
    for parent_tree_number in parent_tree_numbers:
        parent = tree_to_onto.get(parent_tree_number)
        if parent is None:
            continue
        parents.add(f"MESH:{parent}")

    output_data.append(
        {
            "concept_name": concept_name,
            "concept_id": concept_id,
            "synonyms": synonyms,
            "parents": list(parents),
            "tree_numbers": tree_numbers,
        }
    )

write_json(output_data, "mesh2023.json")
