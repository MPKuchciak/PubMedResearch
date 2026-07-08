# PubMed Queries

## Harvest query (the corpus)

The exact query used by `00_api_data_gathering.ipynb` to build the corpus. It applies no disease-term filter. Disease and topic detection are handled downstream (NER and MeSH), so the corpus stays general and is not biased by a keyword pre-filter.

    english[Language]
    AND (USA[Affiliation] OR US[Affiliation])
    AND hasabstract[text]
    AND humans[Filter]
    AND Journal Article[pt]

Period: 1994-01 to 2025-12, harvested month by month. Run interactively at https://pubmed.ncbi.nlm.nih.gov/advanced/

## Per-month verification

`01_verification.ipynb` prints, for each month, an Advanced-Search string that adds a publication-date window to the harvest query:

    <harvest query> AND YYYY/MM/DD:YYYY/MM/DD[PDAT]

Pasting any of these into PubMed Advanced Search returns the live count for that month, which should match the harvested count.

Notes:

- `[PDAT]` is the publication date, not the date the record was added to PubMed (`[EDAT]` / `[CRDT]`).
- Records with year-only or year-and-month precision are bucketed by PubMed onto the start of their period (often January 1), so summed monthly counts can exceed a single all-time count of the query. This is expected, not an error.
- The 10,000-record paging cap applies to `db=pubmed`, so months above the cap are split by day, and single days above the cap are split by PMID range. See notebook 00.

## Earlier exploratory queries (not used for the final corpus)

These disease-term queries were explored early to gauge how a disease pre-filter would shrink the corpus. They are kept for reference only. The final pipeline does not pre-filter on disease terms, so none of these define the corpus.

Title/Abstract disease filter (about 733,000 results at the time):

    ("disease"[Title/Abstract] OR "diseases"[Title/Abstract]
     OR "illness"[Title/Abstract] OR "illnesses"[Title/Abstract]
     OR "health problem"[Title/Abstract] OR "health problems"[Title/Abstract])
    AND english[Language]
    AND (USA[Affiliation] OR US[Affiliation])
    AND hasabstract[text]
    AND humans[Filter]

Broader All-Fields variant (wider; includes non-clinical matches such as veterinary work):

    ("disease"[All Fields] OR "diseases"[All Fields]
     OR "illness"[All Fields] OR "illnesses"[All Fields]
     OR "health problem"[All Fields] OR "health problems"[All Fields])
    AND english[Language]
    AND (USA[Affiliation] OR US[Affiliation])
    AND hasabstract[text]
    AND humans[Filter]

Difference set (records the All-Fields filter adds over the Title/Abstract filter, used to inspect what the broader match pulls in):

    (<All Fields disease filter>) NOT (<Title/Abstract disease filter>)

Note on the original drafts: the OR terms must be fully parenthesised as one group before the `AND` clauses, otherwise PubMed binds the last `OR` to the `AND` and the affiliation and human filters do not apply to every term. The versions above are grouped correctly.
