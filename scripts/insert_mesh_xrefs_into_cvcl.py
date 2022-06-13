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
ipc.init(
    "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.RDNhaUSr0zwm6MWBDhQ59jnNFKjGSmmSQfm_UQFYPBy7wAbAcFJV-SvFFgk9n5NQKyogkpl7KZwokvDhNTeEzluup2GzZj_bFmbEiYHX-nWZY7vN6NIqdP4AmYXnAuK8nJyT8D8sjHHLGgpez8GVzF4OoNu0TIoQuDaTodXzz5jCKhGSvxJl5kbvTZDoQqWzvj43RH7KA1T47FmmuEdjz4Y3xbUraaOHmnLbUknL9VtR0OVhPnpjwgUs9CzF3RfzAk22j1n61zD1PDaVEViDcCeJb1tTbG9TMsF45TnoF_CFi_ILeDpeUi5UPeiMge4-04ED-pQ5JhSKfRqP4G9SkA.mFnHjgr_IHyKRavg.32ss0VHk5hngIln1V9roPGy2-F_WjUD6FK4SqRVXa4gVJTFsRf4WrUPgodiJQ52c3fA7Jxb47PV_TMPzGHdXFGDsirmFVolaemTEbJEGrXjaNAIepDiky_oNP7lQ1g6yqUpqMmeiYsFazwsZU3ygvjL5zjbxpz2t5gwMYHFoEDvVovJ8no1FbjDyNN96I9IQjv1MmBi5f1XLyCgPXDM0wLxsG79G3tewkd0MGFMPSEMC5BbtXwcI4Zk0_XXtG7ZdnKwn2H0pbZkCMKHspUuXxDgZ1KFmF0U7l60Uk_F9utfafokuyM3-oCe-o5e46OV81M49G1E1wGcxp_NoRIznY958cyoE6NVXjMURI8UuCEx_mDchz8fXL8P-32iXZdVVKPEyeSfkoZBcyqqqXfWE915pT-dsjXbDfAj985Lpmc3zPjnFJiMIc5wdfGWyrHjpg4VWgJykrblRMTdGvRj27v9H-OUJxo-3z6_cn-dlQYrq2PvMSF-0QCrC2iS_PalzuVF7qrZLbC0nGitjhEBiY0y-rWEJML25axLgy2z8evSOVf4KoJu6emswrNaL04aKUtQkwSZ1uHXjUKTvvYhlNmGCph21kU_ppAPSYzMPKyVF7MuMLzzUMubNEz5FZj1eUxj5DIMYVkDOKwoSO6zFc1d_Da-iPhiyQa3SGYuExWshDek7TjAXkfMVLEoNEsxd7jtE3ARLMDd07M5wve9w9cxvCii0D-XbMLRtI3oKgqoWLqIvhxGpyYQkoIlA7BmBGxzeUkPszHIZtCfzst0QOY2BOMN-LMI1RWHKKgkEuUOxp2nKlxaPvsqcJ89FbBo4L9DFypqv8zSsAXJEgkMN_FwilHg1e2w_6u5l-qzc9ZrOAv9JEG3QmK1rMkrfM6uqFBW0BzSw1r6fZCDVpDYTUU2bGBu0dUpY_Fv5va9g0DsCf_zzfaVimbw34c6iBD3-Qc_4GBS_9SL6U29wCstwuEqa4TqRSM1s-yAlN6mlAEcI2z3IIbjkoYY36jGJx7Q0ruvAtdjcl2C6yxHnDy6E8HVorHZSfs0g88rC5l8zlWbsqC6yHQ_ez12HeubK3lFHzDqx_DQj2IrFQxrr8nwEuQqJoeTLq5HTxKBJuhrtVoZTsRljjmwtAp65nlpUjZ4XWAzPsEJeoGMCjKfOLDq1KxBiqS9_OMEF6LoYcRs36fQ-YJoXN6k5G8cHQrto71ka2Ml02S4blf8Zw40xQ0wvQIeo2eqWRrdgDCM1TBmm58XIkhv_DmDhnaPhngGMWzXVmZi64X0OuyvOWkmCtSzx6AZZp57-MqJgNrKdBn45tMSojy9fw--cjxSxMn4.JaJcExeLHSGWAllPoiAoEA"
)


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
