```
Data/
├── 0.Raw/
│   └── API_data/          # Raw JSON or raw API results
├── 1.EarlyCleaned/
│   ├── cleaned_parquet/   # First cleaning stage Parquet files
│   └── raw_parquet/       # Converted raw data in Parquet format
├── 2.Processed/
│   ├── EDA/               # Exploratory Data Analysis
│   ├── ModellingData/     # Data prepared for models (e.g., tokenized files)
│   └── Other/             # Any intermediate processed files
└── 99.Backup/             # Data backups
Data-README.md
```
