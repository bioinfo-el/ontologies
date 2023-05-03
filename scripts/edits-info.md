### Edits done to cellosaurus.obo

For pronto to be able to read cellosaurus.obo we have to do the following

otherwise it gives a parsing error
1. Remove license (entire block preceded by '!')
2. Remove 'date' header in the topmost block

3. Then do this
`grep -vE 'xref: .*:[^!]+ [^!]+( ! .*)?' cellosaurus-edited.obo > cellosaurus-edited-v2.obo`

4. Remove comments and synonyms to make it slim
5. Correct the way BTO and NCBITaxon xrefs are written
```
grep -vE '^comment' cellosaurus-edited-v2.obo > cellosaurus-edited-v3.obo
grep -vE '(^synonym:|^relationship|^creation_date:|^xref: [^BN])' cellosaurus-edited-v3.obo > cellosaurus-slim_0.obo
sed 's/xref: BTO:BTO/xref: BTO/' cellosaurus-slim_0.obo > cellosaurus-slim_1.obo
rm cellosaurus-slim_0.obo
sed 's/xref: NCBI_TaxID/xref: NCBITaxon/' cellosaurus-slim_1.obo > cellosaurus-slim_2.obo
rm cellosaurus-slim_1.obo
sed -E 's/(^xref: .*) ! (.*)$/\1 "\2"/' cellosaurus-slim_2.obo > cellosaurus-slim_3.obo
rm cellosaurus-slim_2.obo
mv -i cellosaurus-slim_3.obo cellosaurus-slim_v0.obo
```
run `python insert_mesh_xrefs_into_cvcl.py`

### Edits done to cl-basic.obo
Remove this line
```
xref: A type of interneuron that has two clusters of dendritic branches that originate directly from the soma and extend in opposite directions and axons that form a plexus which spreads widely. Compared to bipolar neurons\, bitufted neurons have branching that occur close to the soma. {xref="PMID:18568015"}
```

No edits in May update

### Edits for CHEBI
remove this line
```
xref: KEGG:D 2959 
```

### Edits for BTO

run `bto_add_subset_defs.py`

run `remove_bto_plants.py` and pass it the output of the previous step
