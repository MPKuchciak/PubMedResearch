# PubMed Research: Data Gathering, Cleaning, and Analysis Pipeline

This repository provides a comprehensive pipeline to gather, preprocess, analyze, and model PubMed abstracts for biomedical research. 
It includes scripts for API data collection, cleaning, tokenization, sentiment analysis, and topic modeling, enabling large-scale text mining on disease-related publications.

## Table of Contents

1. [Overview](#overview)  
2. [Project Structure](#project-structure)  
3. [Data Folders](#data-folders)  
4. [Functions Folder](#functions-folder)  
5. [Notebooks Folder](#notebooks-folder)  
6. [Usage & Instructions](#usage--instructions)  
7. [Dataset Description](#dataset-description)  
8. [Potential Applications](#potential-applications)  
9. [License](#license)

---

## Overview

Focus: Analyze disease-related PubMed abstracts (1995–2024), including entity recognition, sentiment analysis (BioMedBERT), tokenization, netork analysis, and topic modeling.

Key features:
- Automated abstract fetching from PubMed (via E-utilities/API).
- Cleaning & deduplication of large datasets.
- Multiple token fields (simple, huggingface, spaCy disease tokens).
- Sentiment analysis with a pre-trained BiomedBERT model.
- Topic modeling (LDA) and potential network analysis. 
- network analysis
- ADD MORE

---

## Project Structure

```text
PubMedResearch/
├── Backup/                     # Archives or backup versions of notebooks/files
│   └── Notebooks_backup_27012025/
├── Data/                       # All data-related folders and files
│   ├── 0.Raw/                  # Original raw data (PubMed API results)
│   │   └── API_data/
│   │       └── results/        # JSON or other raw output from PubMed queries
│   ├── 1.EarlyCleaned/         # Early-stage cleaned data (e.g., deduplicated, basic cleaning)
│   │   ├── cleaned_parquet/
│   │   │   └── final/          # Final cleaned parquet files for stage 1
│   │   └── raw_parquet/        # Parquet outputs of initial flattening from JSON
│   ├── 2.Processed/            # Processed or partially analyzed data
│   │   ├── ModellingData/      # Data prepared for modeling (topic modeling, etc.)
│   │   └── SentimentAnalysis/  # Data or results specifically for sentiment tasks
│   │       ├── Labeled_Chunks/ # Sentiment-labeled chunks
│   │       └── Chunks/         # Possibly chunked abstracts for pipeline
│   ├── 3.Outputs/              # Final or intermediate outputs (visualizations, CSVs) for future development
│   └── 4.AdditionalData/       # Misc/domain-specific data (COVID-19, etc.)
│       └── Covid-19/
├── Docs/                       # Documentation files (e.g., extra .md files, user guides)
├── Functions/                  # Python scripts with reusable functions (importable modules)
│   ├── parquet_reader.py       # Utility to read Parquet in batches
│   ├── parquet_save_and_merge.py  # Save DF in batches & merge
│   └── __pycache__/            # Auto-generated Python cache
├── Helpers/                    # Various helper files or images
│   └── kaggle_picture/
├── Notebooks/                  # Main Jupyter notebooks (active dev or final)
│   ├── 0.API_Data_Gathering.ipynb          # Notebook for querying PubMed APIs and gathering raw data
│   ├── 1.Parquet_Early_Data_Cleaning.ipynb # Minimal cleaning & converting raw JSON to Parquet
│   ├── 2.EDA_Tokenization.ipynb            # Exploratory data analysis and tokenization strategies
│   ├── 3.1.Keywords_analysis.ipynb         # Analysis of keyword frequencies or patterns
│   ├── 3.2.Mesh_analysis.ipynb             # Analysis of MeSH terms across abstracts
│   ├── 3.EDA.ipynb                         # Additional EDA (may combine or refine the above steps)
│   ├── 4.Sentiment_abstract.ipynb          # Initial sentiment analysis on abstracts
│   ├── 4.Sentiment_abstract_vol2.ipynb     # Extended or second phase of sentiment analysis
│   ├── 5.Analysis_TopicModelling.ipynb     # LDA or other topic modeling steps on merged tokens
│   ├── 6.Covid.ipynb                       # Focused notebook on COVID-related data or analysis
│   ├── 7.Network.ipynb                     # Co-author or disease network analysis (graphs/networkX)                          
│   └── archive/                # Old or archived notebooks
├── ScispaCy/                   # Possibly environment or code related to SciSpaCy usage
└── README.md (and/or other top-level files like .gitignore, LICENSE, etc.)
```

---

## Data Folders

- **Data/0.Raw/**  
  - **API_data/results/**: Original JSON output from PubMed API queries.
- **Data/1.EarlyCleaned/**  
  - **raw_parquet/**: Flattened from JSON → Parquet.  
  - **cleaned_parquet/** + **final/**: Post-dedup and minimal cleaning outputs.
- **Data/2.Processed/**  
  - **ModellingData/**: Data prepared for advanced tasks (like topic modeling).  
  - **SentimentAnalysis/**:  
    - **Labeled_Chunks/**: Final or intermediate sentiment-labeled data.  
    - **Chunks/**: Possibly chunked data for pipeline steps.
- **Data/3.Outputs/**: Final results or CSV logs.  
- **Data/4.AdditionalData/**: External or specialized domain data (e.g., COVID-19).

---

## Functions Folder

- **parquet_reader.py**  
  Utility to read large Parquet files in chunks, typically with a progress bar.

- **parquet_save_and_merge.py**  
  Helper to split large DataFrames into batches, save them, then merge all batches back into a single Parquet file.

Use them as:

***from Functions.parquet_reader import read_parquet_in_batches_with_progress***

***from Functions.parquet_save_and_merge import save_and_merge_in_batches***

---

## Notebooks Folder

```text
Notebooks/
├── 0.API_Data_Gathering.ipynb          # Notebook for querying PubMed APIs, gathering raw data
├── 1.Parquet_Early_Data_Cleaning.ipynb # Minimal cleaning & converting raw JSON to Parquet
├── 2.EDA_Tokenization.ipynb            # Exploratory data analysis and tokenization strategies
├── 3.1.Keywords_analysis.ipynb         # Analysis of keyword frequencies or patterns
├── 3.2.Mesh_analysis.ipynb             # Analysis of MeSH terms
├── 3.EDA.ipynb                         # Additional EDA (combining earlier steps)
├── 4.Sentiment_abstract.ipynb          # Initial sentiment analysis on abstracts
├── 4.Sentiment_abstract_vol2.ipynb     # Second phase or extended sentiment analysis
├── 5.Analysis_TopicModelling.ipynb     # LDA or other topic modeling on merged tokens
├── 6.Covid.ipynb                       # Focus on COVID-19 subset or domain-specific analysis
├── 7.Network.ipynb                     # Co-author or disease network analysis (graph-based)
└── archive/                            # Old or archived notebooks
```

These notebooks guide you from **data gathering & minimal cleaning** through **tokenization, sentiment, and topic modeling** to **network analysis**. 

---

## Usage & Instructions

1. **Environment Setup**  
   Install dependencies from `requirements.txt`:

   pip install -r requirements.txt

   2. **Data Pipeline**  
- **Run** `0.API_Data_Gathering.ipynb` to fetch raw data from PubMed.  
- **Process** with `1.Parquet_Early_Data_Cleaning.ipynb` for minimal cleaning & Parquet conversion.  
- **EDA & Tokenization** (`2.EDA_Tokenization.ipynb`) to explore data distribution, refine tokenization.  
- **Sentiment Analysis** with `4.Sentiment_abstract.ipynb` or `4.Sentiment_abstract_vol2.ipynb` (using BioMedBERT).  
- **Topic Modeling** with `5.Analysis_TopicModelling.ipynb`.  
- Additional tasks: **keywords**/MeSH analysis, networks, etc.

3. **Saving & Reading Parquet**  
- Use **Functions/** scripts for batch saving or reading large datasets:
  ```
  from Functions.parquet_save_and_merge import save_and_merge_in_batches
  
  # Example usage
  result_path = save_and_merge_in_batches(
      df, batch_size=100_000, output_folder="Data/2.Processed/ModellingData", final_filename="merged.parquet"
  )
  ```

4. **Outputs**  
- Processed data: in **Data/1.EarlyCleaned** or **Data/2.Processed** subfolders.
- Final or advanced outputs: **Data/3.Outputs**.

---

## Dataset Description

This dataset (covering ~1 million abstracts from ~1995–2024) facilitates large-scale text mining and longitudinal research on biomedical publications:
- **Focus**: English, US affiliation, disease related terms (health problems are included too), humans.
- **File Highlights**:
- `P5_final_new.parquet`: Comprehensive fields & multiple token columns (`_simple`, `_hf`, `_spacy`).
- `PubMedAbstracts_final.parquet`: Possibly smaller or final deduplicated dataset.
- **Token Fields**:
- `*_simple`: Lightly cleaned tokens (punctuation removed, bracket citations stripped).
- `*_hf`: Hugging Face subword tokens for BERT-like models.
- `*_spacy`: Specialized disease entity tokens extracted via spaCy.
- **Dedup**: e.g., 401,132 duplicates removed. 
- **Sentiment**: Auto-labeled using a BioMedBERT-based pipeline.

---

## Potential Applications

1. **Longitudinal Disease Study**: Explore how publication rates or disease mentions shift by year, correlate with real-world outbreaks.
2. **NLP**: Summarization, NER, or classification tasks (fine-tune domain LMs on large corpora).
3. **Topic Modeling**: LDA or advanced methods to discover thematic clusters (see `5.Analysis_TopicModelling.ipynb`).
4. **Network Analysis**: Build co-author or disease networks for collaboration or comorbidity patterns.
5. **Bibliometric Trends**: Evaluate spikes in research on certain conditions, or correlation with policy changes.

---

## License

This project is licensed under the MIT License.  
See the [`LICENSE`](LICENSE) file for details.

