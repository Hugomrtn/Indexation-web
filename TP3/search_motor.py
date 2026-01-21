import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import json
import re
import numpy as np


# JSON READ AND SAVE

def read_jsonl(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def read_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# TOKENIZING TEXT

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


def replace_with_synonyms(request_tokens, synonyms_index):
    new_tokens = []
    for token in request_tokens:
        replaced = False
        for original, synonyms in synonyms_index.items():
            if token in synonyms:
                new_tokens.append(original)
                replaced = True
                break
        if not replaced:
            new_tokens.append(token)
    return new_tokens


def transform_request(request, list_of_synonyms_indexes):
    stop_words = set(stopwords.words('english'))
    request_tokens = tokenize(stop_words, request)
    for synonyms_index in list_of_synonyms_indexes:
        current_tokens = replace_with_synonyms(request_tokens, synonyms_index)
    return current_tokens


# FILTRATION

def find_token_from_index(token, index):
    # return a list of links where the token appears
    result = index.get(token)
    if isinstance(result, list):
        return result
    return list(result.keys()) if result else []


def find_token_from_all_indexes(token, indexes):
    result = []
    for index in indexes:
        current_result = find_token_from_index(token, index)
        result.extend(current_result)
    return list(set(result))


def find_tokens_from_index(tokens, index):
    result = []
    for token in tokens:
        current_result = find_token_from_index(token, index)
        result.extend(current_result)
    return list(set(result))


def find_tokens_from_all_indexes(tokens, indexes):
    result = []
    intersect_result = find_token_from_all_indexes(tokens[0], indexes)
    for token in tokens:
        current_result = find_token_from_all_indexes(token, indexes)
        result.extend(current_result)
        intersect_result = list(set(current_result) & set(intersect_result))
    return list(set(result)), intersect_result


def verify_tokens_presence(result, intersect_result):
    at_least_one = True if result else False
    all_tokens = True if intersect_result else False
    return at_least_one, all_tokens


def get_filtered_file(list_of_urls, json_file):
    filtered_file = []
    for row in json_file:
        if row.get("url") in list_of_urls:
            filtered_file.append(row)
    return filtered_file


# DOCUMENTS TOKENIZATION AND OPERATIONS

def get_important_features():
    return ["brand", "made in", "flavor", "colors"]


def get_list_of_doc_tokens_per_type(filtered_file, list_of_synonyms_indexes):
    features_names = get_important_features()
    title_doc = []
    description_doc = []
    features_doc = []
    for row in filtered_file:
        url = row["url"]
        title = row["title"]
        description = row["description"]
        features = ""
        for features_name in features_names:
            current_feature = row["product_features"].get(features_name) or ""
            features += " " + current_feature

        title = transform_request(title, list_of_synonyms_indexes)
        description = transform_request(description, list_of_synonyms_indexes)
        features = transform_request(features, list_of_synonyms_indexes)

        title_doc.append({"url": url, "tokens": title})
        description_doc.append({"url": url, "tokens": description})
        features_doc.append({"url": url, "tokens": features})
    return title_doc, description_doc, features_doc


def merge_list_of_doc_tokens(title_doc, description_doc, features_doc):
    merged_list = []
    for i in range(len(title_doc)):
        tokens = title_doc[i]["tokens"] + description_doc[i]["tokens"] + \
            features_doc[i]["tokens"]
        merged_list.append({"url": title_doc[i]["url"], "tokens": tokens})
    return merged_list


def get_token_frequence_in_doc_tokens(token, doc_tokens):
    tokens = doc_tokens["tokens"]
    return tokens.count(token)


def get_token_frequence_in_list_of_doc_tokens(token, list_of_doc_tokens):
    count = 0
    for doc_tokens in list_of_doc_tokens:
        count += get_token_frequence_in_doc_tokens(token, doc_tokens)
    return count


def get_match_count(request_tokens, tokens_list):
    count = 0
    for token in request_tokens:
        count += tokens_list.count(token)
    return count


# RANKING

def compute_bm25(request_tokens, list_of_doc_tokens, current_doc_tokens,
                 b=0.75, k=1.2):
    result = 0
    field_len = len(current_doc_tokens["tokens"])
    avg_field_len = np.mean([len(doc_tokens['tokens']) for doc_tokens in
                             list_of_doc_tokens])
    for token in request_tokens:
        f = get_token_frequence_in_doc_tokens(token, current_doc_tokens)
        idf = get_token_frequence_in_list_of_doc_tokens(token,
                                                        list_of_doc_tokens)
        numerator = f * (k+1)
        denominator = f + k * (1 - b + b * (field_len/avg_field_len))
        result = idf * numerator / denominator
    return result


def compute_linear_ranking(request_tokens, list_of_merged_docs,
                           current_doc_tokens, current_title_tokens,
                           current_description_tokens,
                           current_features_tokens):

    w_bm25 = 1.0
    w_title = 3.0
    w_description = 0.5
    w_features = 2.0

    bm25_score = compute_bm25(request_tokens, list_of_merged_docs,
                              current_doc_tokens, b=0.75, k=1.2)

    title_matches = get_match_count(request_tokens,
                                    current_title_tokens["tokens"])
    features_matches = get_match_count(request_tokens,
                                       current_description_tokens["tokens"])
    desc_matches = get_match_count(request_tokens,
                                   current_features_tokens["tokens"])

    linear_ranking = (bm25_score * w_bm25) + \
                     (title_matches * w_title) + \
                     (desc_matches * w_description) + \
                     (features_matches * w_features)

    return linear_ranking


def compute_ranking_for_all_entries(request_tokens, list_of_doc_tokens,
                                    title_tokens, description_tokens,
                                    features_tokens):
    ranking_result = []
    for i in range(len(list_of_doc_tokens)):
        current_doc_tokens = list_of_doc_tokens[i]
        current_title_tokens = title_tokens[i]
        current_description_tokens = description_tokens[i]
        current_features_tokens = features_tokens[i]

        url = current_doc_tokens["url"]
        score = compute_linear_ranking(request_tokens, list_of_doc_tokens,
                                       current_doc_tokens,
                                       current_title_tokens,
                                       current_description_tokens,
                                       current_features_tokens)

        ranking_result.append({"url": url, "score": score})
    return ranking_result


def get_ordered_results(ranking_result):
    # url, score
    sorted_results = sorted(ranking_result, key=lambda x: x['score'],
                            reverse=True)
    return [item['url'] for item in sorted_results]


# FINAL PIPELINE

def provide_ranking_results(request, document, title_index, description_index,
                            list_of_features_indexes,
                            list_of_synonyms_indexes):

    request_tokens = transform_request(request, list_of_synonyms_indexes)

    all_indexes = [title_index, description_index]
    for feature_list in list_of_features_indexes:
        all_indexes.append(feature_list)

    res_urls, intersect_urls = find_tokens_from_all_indexes(request_tokens,
                                                            all_indexes)

    if len(intersect_urls) >= 5:
        urls = intersect_urls
    else:
        urls = res_urls

    filtered_file = get_filtered_file(urls, document)

    title_tokens, description_tokens, features_tokens = \
        get_list_of_doc_tokens_per_type(filtered_file,
                                        list_of_synonyms_indexes)

    merged_tokens = merge_list_of_doc_tokens(title_tokens, description_tokens,
                                             features_tokens)

    ranking_result = compute_ranking_for_all_entries(request_tokens,
                                                     merged_tokens,
                                                     title_tokens,
                                                     description_tokens,
                                                     features_tokens)

    return get_ordered_results(ranking_result)
