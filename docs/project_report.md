# The Most Popular Diseases in Medical Articles on PubMed

Authors:
- Maciej Kuchciak
- Mateusz Pliszka
- Łukasz Janisiów

## Project Overview:
The main goal of this analysis is to identify the most popular diseases in medical articles on PubMed from January 1994 to December 2024. The analysis includes more than 1 million articles, focusing primarily on titles, abstracts, and MeSH terms. 

Additionally, the analysis investigates:
- Sentiment of abstracts
- Network between authors and their co-authors
- Connection between COVID-19 infection rates and the number of COVID-19 related articles
- Exploratory Data Analysis to find others interesting insights from data

Our analysis aims to answer the following questions:
- What is the most popular illness describe in medical articles from 1994 to 2024? How does it vary each year?
- Is there a correlation between COVID-19 cases and the number of related articles?
- Is there a noticeable sentiment in abstracts? Does it change over time?
- Are there any other features that change over time in scientific articles?
---
## **0. API Data Gathering**
### **File** 
[0.API_Data_Gathering.ipynb](https://github.com/MPKuchciak/PubMedResearch/blob/main/Notebooks/0.API_Data_Gathering.ipynb)  
### **Purpose**
This Jupyter Notebook is designed to fetch and process PubMed articles using the PubMed API. It provides a complete pipeline for querying PubMed, fetching article details, and saving the data for further analysis.

The following types of data are downloaded for each PubMed article:
   - uid: The unique PubMed ID (PMID) of the article.
   - title: The title of the article. 
   - journal: The name of the journal in which the article was published. 
   - pubdate: The publication date of the article in the format "YYYY-MM-DD".
   - abstract_sections: A list of sections within the article's abstract, including labels, categories, and text.
   - authors: A list of authors, including their names, initials, ORCID IDs, and affiliations.
   - mesh_terms: Medical Subject Headings (MeSH) terms associated with the article, including descriptors, major topics, and qualifiers.
   - keywords: Keywords associated with the article.

### **Conclusions**
1. The total number of articles downloaded is 1,460,893.

---

## **1. Parquet Early Data Cleaning**
### **File**
[1.Parquet_Early_Data_Cleaning.ipynb](https://github.com/MPKuchciak/PubMedResearch/blob/main/Notebooks/1.Parquet_Early_Data_Cleaning.ipynb)  
### **Purpose**
This Jupyter Notebook is designed to process and clean a collection of JSON files containing article data.
- Load raw JSON data containing PubMed abstracts, flatten the nested structures, and convert the data into Parquet format for efficient storage and processing.
- Address inconsistencies in publication date formats and eliminate duplicate articles.

### **Conclusions**
1. The downloaded data contained 401,132 duplicate rows, accounting for 27.5% of the dataset.
2. The final dataset used for analysis contains 1,059,761 unique rows after deduplication.


---

## **2. Exploratory Data Analysis (EDA)**
### **File**
[2.EDA.ipynb](https://github.com/MPKuchciak/PubMedResearch/blob/main/Notebooks/2.EDA.ipynb)  

### **Purpose**
In this file, we perform Exploratory Data Analysis. We answered to the following questions:

- Who is the most active publisher?
- What is the most popular journal?
- Is the number of co-authors growing?
- Are there other trends in the articles?

### **Conclusions**
1. An increasing trend is observed across various domains, including the number of articles published per year, but also the number of authors per article, the number of words in abstracts, and the number of words per title.
2. The highest average number of articles are published in January, which aligns with the findings from the article "April publishing lull follows end-of-year academic flurry" [1]. This study stated that January and November are the most popular months for publishing.
3. The number of authors per article is on the rise, increasing from an average of approximately 5 authors per article in 1995 to around 11 authors per article in 2024. The overall average number of authors per article from 1995 to 2024 is 6.54.
4. The average number of words in abstracts has increased from slightly below 190 in 1995 to over 230 by 2024. The overall average number of words in abstracts for the entire period is 210.
5. The average number of words in titles has been increasing over the years, rising from 11.5 in 1995 to just over 14 in 2024. This represents an approximate 20% increase over 29 years, mirroring the same percentage increase observed in the length of abstracts.
6. The top publisher in our dataset is David A. Bennett [2], who has authored over 700 filtered articles related to diseases. In his Google Scholar profile, he has 1195 articles.
7. The most popular journal in our dataset is "Scientific Reports" with 8,778 publications, followed by "Clinical Infectious Diseases" with 5,953 publications, and "Nature Communications" with 5,537 publications. The least popular journal among the top 10 is "Proceedings of the National Academy of Sciences of the United States of America" with 3,537 publications.

[1] https://www.nature.com/nature-index/news/april-publishing-lull-follows-end-of-year-academic-flurry

[2] https://scholar.google.com/citations?user=m_NIro4AAAAJ&hl=en


---

## **3. Tokenization**
### **File**
[3.Tokenization.ipynb](https://github.com/MPKuchciak/PubMedResearch/blob/main/Notebooks/3.Tokenization.ipynb)  

### **Purpose**
This notebook processes and analyzes PubMed abstracts and titles to detect diseases using various tokenization methods and SciSpacy's biomedical NER model.

Tokenization Methods:
1. **Simple Tokenization**: Basic whitespace and punctuation-based tokenization.
2. **Hugging Face Tokenization**: Tokenization using the Hugging Face `distilbert-base-uncased` model.
3. **Dictionary-Based Disease Detection**: Filtering tokens based on a predefined disease dictionary.
4. **SciSpacy Biomedical NER**: Using the `en_ner_bc5cdr_md` model to detect disease entities.

### **Conclusions/Final Decision**
The goal was to ensure high-quality data for further analysis and modelling while retaining as much relevant information as possible.

**Choices Considered**:

Title only: Retain rows with illness-related tokens in the title.
*Result*: ~1,000,000 → 480,000 rows removed (~520,000 retained).

- Abstract + Title: Retain rows with tokens in either title or abstract.
*Result*: ~1,000,000 → 84,000 rows removed (~916,000 retained).

- Abstract + Title + MeSH terms: Include tokens found in MeSH terms.
*Result*: ~1,000,000 → 60,000rows removed (~940,000 retained).

- Abstract + Title + MeSH + Hybrid Filtering: Use advanced filtering (e.g., hybrid matching and simpler keyword matching).
*Result*: ~1,000,000 → 54,000 rows removed (~946,000 retained).

- Retain All Rows: Do not remove rows based on token presence.

**Final Decision**:
We chose Option 5 to retain all rows. This decision was based on the reasoning that data lacking illness-related tokens is not inherently irrelevant and there may be possibility to check these inputs (articles) and see what's the problem with them. 

By keeping all rows we additionaly:

- We maintain the integrity and diversity of the dataset.

- Downstream analyses remain flexible, as token filtering can be performed at a later stage if necessary.

- It enables broader exploration and modeling possibilities without prematurely discarding data.

- By taking this approach, the dataset remains inclusive, ensuring no potential insights are lost. This aligns with our goal of providing a comprehensive resource for PubMed data analysis.

---

## **4. 4.Topic Modelling**
### **File**
[3.Tokenization.ipynb](https://github.com/MPKuchciak/PubMedResearch/blob/main/Notebooks/3.Tokenization.ipynb) 

### **Purpose**
Lorem ipsum

### **Conclusions**
Lorem ipsum

---

## **5.1 Keywords Analysis**
### **File**
[5.1.Keywords_analysis.ipynb](https://github.com/MPKuchciak/PubMedResearch/blob/main/Notebooks/5.1.Keywords_analysis.ipynb) 

### **Purpose**
This notebook analyzes keyword trends in articles to identify disease patterns over time.

### **Conclusions**
1. There is a lack of articles with keywords before 2012.
2. Keywords are often associated with names or types of diseases.
3. COVID-19 and SARS-CoV-2 have dominated the keyword trends after 2019.
4. Alzheimer's disease has shown the most rapid growth in recent years, appearing in keywords less than 100 times in 2014 and more than 800 times in 2024.
5. Epidemiology and inflammation have also shown significant growth, peaking in 2021, likely due to the high number of articles associated with COVID-19.
6. Other frequently occurring disease-related keywords exhibit a more consistent growth trend, often peaking in 2021, which is most likely associated with the highest number of articles in that year.

---

## **5.2 MeSH Analysis**
### **File**
[5.2.Mesh_analysis.ipynb](https://github.com/MPKuchciak/PubMedResearch/blob/main/Notebooks/5.2.Mesh_analysis.ipynb) 

### **Purpose**
This notebook explores the use of MeSH (Medical Subject Headings) [1] terms in PubMed articles. MeSH terms provide a standardized way to categorize and index biomedical topics, helping researchers in finding relevant studies more efficiently. By unifying different terms (e.g., "heart attack" and "myocardial infarction"), they enhance the precision and comprehensiveness of searches. We analyze these terms to identify trends in disease topics within the articles.

### **Conclusions**
1. The most common MeSH terms are general terms rather than specific disease names. The top terms include 'humans' (1 057 871 occurrences), 'female' (472 540 occurrences), 'male' (432 617 occurrences), 'middle aged' (289 180 occurrences), 'adult' (283 915 occurrences), and 'aged' (227 184 occurrences). The total number of unique MeSH terms is 27 087.
2. The most common group of diseases in MeSH terms are chronic diseases, followed by HIV infections and cardiovascular diseases.
3. In 2024, the most articles were related to Alzheimer's disease (rapidly growing trend), cardiovascular diseases (growing trend), HIV (decreasing trend), and neoplasms (growing trend).
4. In recent years there was a rapid growth in the number of articles related to Alzheimer's disease. The increase was slow from 1995 to 2014, but from 2015 onwards, there has been a strong rise in related articles, from around 800 articles per year in 2015 to 2000 articles per year in 2024.
5. For HIV infection-related articles, there was a growing trend from 1995 to 2021. However, after 2021, the number of HIV-related articles has been decreasing. This decline might be due to advancements in HIV treatment, making the disease more manageable. However, this observation requires further analysis.

[1] National Library of Medicine. Medical Subject Headings (MeSH). (https://www.nlm.nih.gov/mesh/meshhome.html)

---

## **6. COVID-19 timeseries closer look**
### **File**
[5.2.Covid.ipynb](https://github.com/MPKuchciak/PubMedResearch/blob/main/Notebooks/6.Covid.ipynb) 

### **Purpose**
In this section, we will closely examine the number of COVID-19-related articles and compare them to the new COVID-19 cases worldwide [1].

### **Conclusions**
1. We can observe that the trend in COVID-19 related articles is not monotonous and varies month to month with some peaks.
2. Peaks in articles published related to COVID-19 align with the peaks of new COVID-19 cases. It would be worth investigating whether the increase in new COVID-19 cases influenced researchers to publish faster. Additionally, it could be that the urgency of the situation led reviewers to accelerate the review process, resulting in quicker publication times.
3. After January 2023, COVID-19 cases started to decrease, and accordingly, the mentions of COVID-19 in MESH Terms decreased as well.

[1] Edouard Mathieu, Hannah Ritchie, Lucas Rodés-Guirao, Cameron Appel, Daniel Gavrilov, Charlie Giattino, Joe Hasell, Bobbie Macdonald, Saloni Dattani, Diana Beltekian, Esteban Ortiz-Ospina and Max Roser (2020) - “COVID-19 Pandemic” Published online at OurWorldinData.org. Retrieved from: 'https://ourworldindata.org/coronavirus' [Online Resource]

---

## **7. Network between the authors and co-authors of the articles**
### **File**
[7.Network.ipynb](https://github.com/MPKuchciak/PubMedResearch/blob/main/Notebooks/7.Network.ipynb) 
### **Purpose**
In this notebook, we will investigate the network between the authors and co-authors of the articles.

### **Conclusions**
1. The top publisher in our dataset is David A. Bennett [1], who has a little more than 700 filtered articles with diseases. In his Google Scholar profile, he has 1195 articles in total.
2. Among the top 30 publishers, the strongest connection is between Blennow Kaj and Zetterberg Henrik, who have co-authored around 160 articles together.
3. In some articles, the same name and surname appear more than once. However, this is not a mistake. Sometimes people with the same names co-author the same article. For example, two people named Li Li co-authored 8 articles.

[1] https://scholar.google.com/citations?user=m_NIro4AAAAJ&hl=en

[2] https://www.nature.com/articles/nbt.1665

---

## **8. Sentiment Abstracts**
### **File**
[8.Sentiment_abstract.ipynb](https://github.com/MPKuchciak/PubMedResearch/blob/main/Notebooks/8.Sentiment_abstract.ipynb) 

### **Purpose**
In this notebook, we investigate the sentiment present in article abstracts.

### **Conclusions**
1. On average abstracts, as expected, are neutral.
2. Sentiment in abstracts does not change significantly over time. There is only a slight decrease in negative sentiment from 2010 onwards.
3. Any month in a year is not associated with negative sentiment in abstracts. For all of the months, sentiment stays more or less the same.

---
