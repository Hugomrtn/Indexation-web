# Web Indexing Project

This repository contains all the works for the Web Indexing course. The project is divided into three parts: crawling, indexing, and searching.

## Author
**Hugo Martin**

## Dependencies installation

```bash
pip install beautifulsoup4 nltk numpy
```

## TP1: Crawler

### Structure
*   **Input**: A root URL and a maximum number of pages to visit.
*   **Process**: The crawler navigates from link to link following a FIFO logic.
*   **Output**: `output.jsonl`. Each line contains a JSON object representing a page (URL, title, first paragraph, links).

### How to launch ?
```bash
python TP1/crawler.py
```

---

## TP2: Indexer

### Index Structure
The script generates several JSON files to index informations:
*   `index_title.jsonl` and `index_description.jsonl`: Inverted indexes associating each word with the URLs where it appears.
*   `index_features_(feature).jsonl`: Specific indexes for attributes (brand, colors, flavors, origin).
*   `index_reviews.jsonl`: Stores rating metadata for each product.

### Implementation Choices
*   **Tokenization**: Uses `NLTK` to tokenize the text.
*   **Normalization**: Conversion to lowercase, punctuation removal, and removal of stop words.

### Bonus Features
*   **Dynamic Feature Extraction**: Specific fields present in `product_features` can be indexed (for example "made in", "flavor").
*   **Aggregate Calculation**: For reviews, the indexer calculates the average rating.

### How to launch ?
```bash
python TP2/indexer.py
```

## TP3: Search Engine

### Structure
*   `main.py`: File that executes a list of queries.
*   `search_motor.py`: Contains query processing, filtering, and ranking.
*   Data: Uses indexes generated in TP2.

### Implementation Choices
*   **Query Processing**: The user query undergoes the same processing as documents (tokenization, cleaning).
*   **Filtering**: Searches for documents containing all terms (intersection) or at least one term (union).
*   **Ranking**: Sorts relevant documents to present the best results first. The ranking formula is
     ```
    score = w_bm25 * bm25 + w_title * match_title + w_description * match_description + w_features * match_features
    ```
### Features
*   **Synonym Management**: Query terms are replaced by their synonyms using `origin_synonyms.json`.

### Example
The `main.py` file contains a list of test queries that can be modified.

This is an example of query: `box of chocolate orange`.

Results are saved in `results.json`.

### How to launch ?
```bash
python TP3/main.py
```
