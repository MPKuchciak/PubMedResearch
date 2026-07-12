# Biomedical Literature Analysis: PubMed Corpus Pipeline

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)
[![Kaggle](https://img.shields.io/badge/Kaggle-Dataset-20BEFF?logo=kaggle&logoColor=white)](https://www.kaggle.com/datasets/mpkuchciak/pubmedabstracts)

A reproducible pipeline that harvests biomedical journal abstracts from PubMed, verifies them against the source, cleans them into a columnar dataset, and analyses three decades of the literature: its diseases and chemicals, its MeSH and keyword structure, its co-authorship networks, the COVID-19 shock, and its latent topics.

**Authors:** Maciej Kuchciak, Mateusz Pliszka, Łukasz Janisiów

## Overview

The project builds a large corpus of PubMed records and carries it from raw harvest through to entity and topic analysis. It is organised as a sequence of notebooks (00 to 11), each producing an inspectable artifact and reading the output of earlier stages.

Harvest and preparation (00 to 02) produce the clean corpus. Analysis (03 to 11) reads that corpus and never re-touches the raw data.

### Corpus at a glance

| Property | Value |
|---|---|
| Source | PubMed / MEDLINE (NCBI E-utilities API) |
| Raw records harvested | ~4.26 million |
| Clean analysis corpus | 3,063,120 unique abstract-bearing records |
| Date range | 1994-01 to 2025-12 (monthly) |
| Files | 384 monthly JSONL files |
| Scope | English-language, US-affiliated, human-subject journal articles with abstracts |

The two record counts are different stages, not a discrepancy: roughly 4.26 million raw records are harvested, then deduplication and dropping of empty or duplicate-content rows yields the 3,063,120-record corpus used for all downstream analysis.

## Data availability

The cleaned corpus is published as a dataset on Kaggle: [PubMed Abstracts](https://www.kaggle.com/datasets/mpkuchciak/pubmedabstracts).

This repository does not commit the data (see `.gitignore`). Either run the pipeline to regenerate it, or download the snapshot from Kaggle. Bibliographic metadata is provided by NLM without use restrictions; abstract text carries the original publishers' copyright, so the dataset is shared for non-commercial research and text mining only, with PubMed/NLM as the source.

### Query

```
english[Language]
  AND (USA[Affiliation] OR US[Affiliation])
  AND hasabstract[text]
  AND humans[Filter]
  AND Journal Article[pt]
```

No disease-term pre-filtering is applied; disease and topic detection are left to downstream NER, MeSH, and topic modelling so the corpus stays general.

## Directory layout

```
**biomedical-literature-analysis/
├── notebooks/
│   ├── 00_api_data_gathering.ipynb     harvest PubMed to monthly JSONL
│   ├── 01_verification.ipynb           validate the harvest (read-only)
│   ├── 02_data_cleaning.ipynb          column-by-column cleaning to Parquet
│   ├── 03_eda.ipynb                    exploratory data analysis
│   ├── 04_mesh_cooccurrence.ipynb      MeSH co-occurrence network
│   ├── 05_coauthorship_network.ipynb   co-authorship metrics and network
│   ├── 06_keyword_trends.ipynb         author-keyword trends
│   ├── 07_covid19_timeseries.ipynb     COVID-19 case study
│   ├── 08_tokenization_ner.ipynb       entity extraction from abstracts
│   ├── 09_entity_dataset.ipynb         per-article entity dataset
│   ├── 10_entity_analysis.ipynb        entity trends, associations, networks
│   └── 11_topic_modeling.ipynb         LDA topic modelling
├── data/                               gitignored; created by the pipeline
│   ├── 0_raw/
│   │   ├── results/                    results_YYYY_MM.jsonl (one per month)
│   │   ├── errors/                     missing_*.json, failed_*.json
│   │   ├── progress.json               resume state
│   │   └── harvest.log                 run log
│   ├── 2_clean/                        clean_*.parquet (corpus used by 03 to 11)
│   ├── 3_entities/                     entity tables, timelines, co-occurrence (09)
│   └── 4_topics/                       LDA model, topic tables, timelines (11)
└── README.md**
```

Paths are resolved from each notebook's location, so notebooks run whether Jupyter starts in `notebooks/` or at the project root. The `data/` directory is gitignored (only folder structure is kept via `.gitkeep`); raw and derived data files are not committed.

## Pipeline

### 00. API Data Gathering

[`notebooks/00_api_data_gathering.ipynb`](notebooks/00_api_data_gathering.ipynb)

Harvests the query month by month and writes one JSONL file per month.

- **History server.** Each month's search is posted to NCBI's history server (`usehistory=y`); records are paged out of `efetch`.
- **The 10,000-record wall.** For `db=pubmed`, no result set can be paged past offset 10,000. Any oversized query is split first by day, and if a single day still exceeds the cap (common in older years, where PubMed dates many year-only records to January 1), by PMID range (`lo:hi[UID]`), bisected recursively down to a single PMID so no piece can stay stuck above the wall.
- **Resume.** `progress.json` tracks completed months and, for an in-progress month, the finished date and PMID pieces. Re-running skips completed work and re-fetches only what is missing, deduplicated by PMID. Safe because historical months are frozen result sets.
- **Robustness.** Per-request timeouts; retries on network errors, HTTP 429/5xx, and transient XML parse errors with exponential backoff; a global rate limiter with headroom under the NCBI ceiling; `tool`/`email` identification per NCBI policy; JSONL appended with `fsync` and torn-line repair on resume.

Output: `data/0_raw/results/results_YYYY_MM.jsonl`, one record per line. Deleted or withheld PMIDs (normal in PubMed) are tallied per month in `errors/missing_*.json`.

### 01. Data Verification

[`notebooks/01_verification.ipynb`](notebooks/01_verification.ipynb)

Read-only validation of the harvested corpus with independent checks: inventory (file count, total rows, date coverage, schema consistency); integrity (duplicate PMIDs within and across files, empty critical fields); date sanity (precision breakdown, records bucketed outside their own pubdate year); cross-check of per-month saved counts against PubMed's live `esearch` count; copy-paste Advanced-Search strings for manual verification; count reconciliation; error and missing-log surfacing; and column-schema reporting. Reported results: sampled months matched PubMed exactly, schema consistent across all 384 files, and a low deleted/withheld rate (around 0.5%).

### 02. Column-by-Column Exploration and Cleaning

[`notebooks/02_data_cleaning.ipynb`](notebooks/02_data_cleaning.ipynb)

Flattens the raw JSONL into a Parquet store, then walks each column in turn (inspect fill rate and sample values, then apply a documented cleaning function), and finishes by dropping unusable rows, deduplicating, and saving the clean corpus. Per-column steps cover `uid`, `title`, `journal`, `abstract` (structured sections flattened to one string), `pubdate` (integer `year` derived, precision flag kept), `authors` (flattened to name and affiliation lists), `mesh_terms`, `keywords`, and `coi_statement`. Row rules drop empty title or abstract, duplicate PMIDs, and duplicate content (same normalized title and abstract under a different PMID).

Output: `data/2_clean/clean_*.parquet`, the 3,063,120-record corpus used by every downstream notebook.

### 03. Exploratory Data Analysis

[`notebooks/03_eda.ipynb`](notebooks/03_eda.ipynb)

Surveys scale, coverage over time, journals, MeSH topics, author teams, and abstract text, and how field completeness changes across decades. Surfaces a key indexing artifact around 2013 to 2015, where established journals nearly vanish from the record while new megajournals grow, a caution for any year-by-year trend reading.

### 04. MeSH Co-occurrence Network

[`notebooks/04_mesh_cooccurrence.ipynb`](notebooks/04_mesh_cooccurrence.ipynb)

Maps the topical structure of the corpus through MeSH descriptor co-occurrence: which subjects appear together, which bridge the most research areas, and how the structure differs by era. Uses normalized (Jaccard) associations and community detection after stripping generic descriptors.

### 05. Co-authorship Network

[`notebooks/05_coauthorship_network.ipynb`](notebooks/05_coauthorship_network.ipynb)

Examines how research is authored: how team sizes changed, how collaboration grew, and the co-authorship network structure among prolific authors. Built in two parts because a single graph over all articles is not tractable. The prolific-author network resolves into collaboration communities that align with recognisable specialities.

### 06. Keyword Trends

[`notebooks/06_keyword_trends.ipynb`](notebooks/06_keyword_trends.ipynb)

Tracks author-supplied keywords (free text, unlike controlled MeSH): cleaning and normalizing surface variants, then measuring which topics rose, faded, or emerged across 2015 to 2025, with trends computed per 1,000 articles.

### 07. COVID-19 Time-Series Case Study

[`notebooks/07_covid19_timeseries.ipynb`](notebooks/07_covid19_timeseries.ipynb)

A focused study of how the pandemic reshaped publishing. Establishes a genuine but minuscule pre-2020 baseline using a historical term union, then measures the surge (roughly 151-fold on a share basis) peaking in 2022, and maps the clinical and public-health pillars of the literature.

### 08. Biomedical Entity Extraction

[`notebooks/08_tokenization_ner.ipynb`](notebooks/08_tokenization_ner.ipynb)

The first notebook to use the abstract text itself. Extracts diseases and chemicals two ways: a fast dictionary match across all abstracts (full-corpus trends) and a scispaCy NER model (`en_ner_bc5cdr_md`) on a representative sample (higher recall and a quality check).

### 09. Entity-Annotated Dataset

[`notebooks/09_entity_dataset.ipynb`](notebooks/09_entity_dataset.ipynb)

Builds a per-article entity dataset both ways (dictionary always; scispaCy model optionally on GPU) and derives frequency tables, timelines, and disease-chemical and disease-disease co-occurrence. Saves everything to `data/3_entities/`.

### 10. Entity Analysis

[`notebooks/10_entity_analysis.ipynb`](notebooks/10_entity_analysis.ipynb)

Turns the saved entity tables into interpretable analysis: the most-studied diseases and chemicals, what is rising or falling, the strongest drug-disease associations, a disease co-occurrence network with communities, and entity richness over time. Runs on either the dictionary or the model tables via a `METHOD` switch.

### 11. Topic Modeling

[`notebooks/11_topic_modeling.ipynb`](notebooks/11_topic_modeling.ipynb)

Moves from entities to themes. Fits Latent Dirichlet Allocation over the abstracts, chooses the topic count by C_v coherence, assigns each article a topic mixture, tracks topics over time with a Kendall trend test and an era breakdown, cross-references topics against the disease entities from notebook 09 by enrichment, and offers an optional interactive pyLDAvis map and an optional BERTopic comparison. Saves to `data/4_topics/`.

## Data schema

### Raw records (`data/0_raw/results/*.jsonl`), 11 fields

| field | type | description |
|---|---|---|
| `uid` | str | PubMed ID (PMID) |
| `title` | str | article title |
| `journal` | str | journal name |
| `pubdate` | str | normalized date, `YYYY-MM-DD` |
| `pubdate_raw` | str | original date string from PubMed |
| `pubdate_precision` | str | `full_date` / `year_month` / `year` |
| `abstract_sections` | list[dict] | `{label, category, text}` per section |
| `authors` | list[dict] | `{name, initials, orcid, affiliations}` per author |
| `mesh_terms` | list[dict] | `{descriptor, major_topic, qualifiers}` per heading |
| `keywords` | list[str] | author keywords |
| `coi_statement` | str | conflict-of-interest statement |

### Cleaned records (`data/2_clean/*.parquet`), 18 columns

`uid`, `title`, `journal`, `year`, `pubdate`, `pubdate_precision`, `abstract`, `abstract_len`, `author_names` (list[str]), `affiliations` (list[str]), `n_authors`, `mesh_descriptors` (list[str]), `n_mesh`, `keywords` (list[str]), `n_keywords`, `coi_statement`, `has_coi`, `source_month`.

## Key decisions and rationale

- **History server plus date/PMID splitting** is mandatory, not optional: the 10,000-record wall applies to `db=pubmed` with or without the history server, and many months exceed 10k.
- **`[PDAT]` for date bucketing** is correct: it is the publication date, not the date the record was added to PubMed (`[EDAT]`/`[CRDT]`).
- **Date precision is tracked** (`pubdate_precision`) because a large share of the corpus has imprecise dates (year or year-and-month only). PubMed buckets these by `[PDAT]`, often onto January 1, which is why per-month counts summed can exceed a single all-time count of the query. This is expected, not an error.
- **Cleaning keeps abstracts;** any decision about redistributing abstract text is deferred.

## Caveats and limitations

- **Affiliation coverage is era-dependent.** `(USA OR US)[Affiliation]` misses "United States", "U.S.", bare state names, and empty affiliation fields (common pre-2000); PubMed also only began recording all authors' affiliations around 2014. US-affiliated work before roughly 2013 is undercounted.
- **Field sparsity by era.** MeSH terms are sparse pre-2000, keywords pre-2012, COI statements pre-2017.
- **Indexing artifacts.** The 2013 to 2015 indexing shift distorts journal-level counts; longitudinal claims account for it.
- **Relative vs absolute trends.** Topic and entity trends are shares of the yearly literature; a falling share does not mean a field is shrinking in absolute terms.
- **Deleted/withheld PMIDs** (around 0.5%) are counted but not retrievable; these are normal PubMed housekeeping records, not data loss.
- **Downstream scope.** Entity and topic analysis covers abstracts only, within the filtered corpus, and inherits the limits of the extraction methods (dictionary recall is a lower bound; the NER and topic models trade recall for precision).

## Environment

Two conda environments, kept separate so the heavy NLP stack does not bloat the data-gathering environment:

- **`pubmed`** for harvesting and cleaning (notebooks 00 to 02): `requests`, `pyarrow`, `pandas`, `matplotlib`, `tqdm`.
- **`ner`** for abstract-text work (notebooks 08 to 11): scispaCy and the `en_ner_bc5cdr_md` model, scikit-learn, gensim, networkx, pandas, seaborn, and optionally BERTopic and sentence-transformers.

Recreate them from the environment files:

```bash
conda env create -f environment-pubmed.yml
conda env create -f environment-ner.yml
```

Notebook outputs are kept in version control for the analysis notebooks via a `keep_output` flag so figures and tables render on GitHub; `nbstripout` strips outputs elsewhere to keep diffs clean.

## Reproducibility and running

Each step is verifiable. Notebook 01 prints exact PubMed Advanced-Search strings so any month's count can be checked by hand at <https://pubmed.ncbi.nlm.nih.gov/advanced/>. Historical months are frozen, so a re-run reproduces the same records.

1. Set credentials (`NCBI_API_KEY`, `EMAIL`) in a `.env` file. An NCBI API key is optional but recommended (it raises the rate limit).
2. Run `00_api_data_gathering.ipynb` to harvest (resumable; safe to interrupt).
3. Run `01_verification.ipynb` to validate.
4. Run `02_data_cleaning.ipynb` to produce the clean Parquet corpus.
5. Run `03` through `11` in order for the analysis.

## Source and licensing

Source: PubMed / MEDLINE, U.S. National Library of Medicine (NLM), via the E-utilities API. Courtesy of the U.S. National Library of Medicine.

Bibliographic metadata (PMIDs, titles, authors, affiliations, MeSH terms, dates) is provided by NLM without use restrictions. Abstract text may be protected by the original authors' or publishers' copyright; NLM does not claim and does not hold this copyright. Any redistribution of abstract text is the redistributor's responsibility to clear, and should carry appropriate license terms and a disclaimer. This corpus is intended for non-commercial research and text mining. This document is not legal advice.

Datasets built from this pipeline are static snapshots and do not reflect the most current data available from NLM; query PubMed directly for up-to-date records. Not affiliated with or endorsed by NLM/NIH/HHS.
