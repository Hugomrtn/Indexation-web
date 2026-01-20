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


def download_token():
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('punkt_tab')


def tokenize(stop_words, text):
    # tokenize the text
    tokens = word_tokenize(text.lower())
    # removing stop words
    current_tokenized = [word for word in tokens if word not in stop_words]
    # removing punctuation
    current_tokenized = [re.sub(r'[^\w\s]', '', token) for token in
                         current_tokenized if re.sub(r'[^\w\s]', '', token)]
    return current_tokenized


def create_reverse_index_title_or_description(json_file, type, filename):
    # outdated by create_reverse_index_title_or_description_with_position
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


def create_index_reviews(json_file, filename):
    index = {}

    for row in json_file:
        # extracting reviews and urls
        current_reviews = row["product_reviews"]
        current_url = row["url"]

        # calculating rating
        ratings = [review["rating"] for review in current_reviews]
        number_of_ratings = len(ratings)
        rating = sum(ratings) / number_of_ratings if ratings else ""
        last_rating = ratings[-1] if ratings else ""

        # updating the index
        index[current_url] = {"number_of_ratings": number_of_ratings,
                              "rating": rating, "last_rating": last_rating}
    save_to_json(index, filename)


def create_index_inside_features(json_file, type):
    # loading stop words for tokenization
    stop_words = set(stopwords.words('english'))
    index = {}

    for row in json_file:
        # extracting url and features
        current_url = row["url"]
        product_features = row.get("product_features", {})
        if not product_features or type not in product_features:
            continue

        # tokenizing feature text
        current_text = product_features[type]
        current_tokenized = tokenize(stop_words, current_text)

        # updating the index
        for token in current_tokenized:
            if token not in index:
                index[token] = set()
            index[token].add(current_url)

    for token in index:
        index[token] = list(index[token])
    return index


def set_features_name():
    # choosing relevant features
    return ["made in", "brand", "flavor", "colors"]


def create_index_features(json_file, filename):
    features_list = set_features_name()
    for feature in features_list:
        # creating index for each feature
        index_feature = create_index_inside_features(json_file, feature)
        # saving the indexes
        current_filename = ((filename+feature)+".jsonl").replace(" ", "_")
        save_to_json(index_feature, current_filename)


def create_reverse_index_title_or_description_with_position(json_file, type,
                                                            filename):
    # loading stop words
    stop_words = set(stopwords.words('english'))
    index = {}

    for row in json_file:
        # extracting text and url
        current_text = row[type]
        current_url = row["url"]

        # tokenizing the text
        current_tokenized = tokenize(stop_words, current_text)

        # building the index with position
        for i in range(len(current_tokenized)):
            token = current_tokenized[i]
            if token not in index:
                index[token] = {}
            if current_url not in index[token]:
                index[token][current_url] = []
            index[token][current_url].append(i)

    save_to_json(index, filename)


def create_all_indexes(filename, save_path):
    # reading the source json file
    json_file = read_json(filename)

    # creating indexes for title and description
    for name in ["title", "description"]:
        filename = save_path+"index_"+name+".jsonl"
        create_reverse_index_title_or_description_with_position(json_file,
                                                                name, filename)
    # creating index for reviews
    create_index_reviews(json_file, save_path+"index_reviews.jsonl")
    # creating indexes for features
    create_index_features(json_file, save_path+"index_features_")


def main():
    filename = "TP2/products.jsonl"
    save_path = "TP2/"
    create_all_indexes(filename, save_path)


main()
