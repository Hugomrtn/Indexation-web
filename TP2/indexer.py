import json
import re

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


def read_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def parse_json(json_file):
    for row in json_file:
        current = urlparse(row["url"])
    # à finir


def download_token():
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('punkt_tab')


def tokenize(stop_words, text):
    tokens = word_tokenize(text.lower())
    current_tokenized = [word for word in tokens if word not in stop_words]
    current_tokenized = [re.sub(r'[^\w\s]', '', token) for token in
                         current_tokenized if re.sub(r'[^\w\s]', '', token)]
    return current_tokenized


def create_reverse_index_title_or_description(json_file, type, filename):
    stop_words = set(stopwords.words('english'))
    index = {}

    for row in json_file:
        current_text = row[type]
        current_url = row["url"]

        current_tokenized = tokenize(stop_words, current_text)

        for token in current_tokenized:
            if token not in index:
                index[token] = set()
            index[token].add(current_url)

    for token in index:
        index[token] = list(index[token])

    save_to_json(index, filename)


def create_index_reviews(json_file, type, filename):
    index = {}

    for row in json_file:
        current_reviews = row[type]
        current_url = row["url"]
        ratings = [review["rating"] for review in current_reviews]
        number_of_ratings = len(ratings)
        rating = sum(ratings) / number_of_ratings if ratings else ""
        last_rating = ratings[-1] if ratings else ""

        index[current_url] = {"number_of_ratings": number_of_ratings,
                              "rating": rating, "last_rating": last_rating}
    save_to_json(index, filename)


def create_index_inside_features(json_file, type):
    stop_words = set(stopwords.words('english'))
    index = {}

    for row in json_file:
        current_url = row["url"]
        product_features = row.get("product_features", {})
        if not product_features or type not in product_features:
            continue
        current_text = product_features[type]
        current_tokenized = tokenize(stop_words, current_text)

        for token in current_tokenized:
            if token not in index:
                index[token] = set()
            index[token].add(current_url)

    for token in index:
        index[token] = list(index[token])
    return index


def set_features_name():
    return ["made in", "brand"]


def create_index_features(json_file, filename):
    features_list = set_features_name()
    for feature in features_list:
        index_feature = create_index_inside_features(json_file, feature)
        current_filename = ((filename+feature)+".jsonl").replace(" ", "_")
        save_to_json(index_feature, current_filename)


json_file = read_json("TP2/products.jsonl")
# create_reverse_index_title_or_description(json_file, "title", "TP2/index_title.jsonl")
# create_reverse_index_title_or_description(json_file, "description", "TP2/index_description.jsonl")
# create_index_reviews(json_file, "product_reviews", "TP2/index_reviews.jsonl")
# create_index_features(json_file, "TP2/index_features_")
