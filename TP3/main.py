import search_motor as sm


def get_list_of_queries():
    # setting the queries
    queries = [
        "box of chocolate orange",
        "italy leather",
        "no results",
        "Hiking Boots for Outdoor Adventures",
        "Chocolate from france"
    ]
    return queries


def main():
    # loading all documents
    rearranged_products = sm.read_jsonl("TP3/rearranged_products.jsonl")
    title_index = sm.read_json("TP3/title_index.json")
    description_index = sm.read_json("TP3/description_index.json")
    origin_index = sm.read_json("TP3/origin_index.json")
    origin_synonyms = sm.read_json("TP3/origin_synonyms.json")
    brand_index = sm.read_json("TP3/brand_index.json")

    # setting the saving filename
    filename = "TP3/results.json"
    # getting queries
    queries = get_list_of_queries()
    all_results = []

    # computing the results for each query
    for query in queries:
        ranking_result = sm.provide_ranking_results(query,
                                                    rearranged_products,
                                                    title_index,
                                                    description_index,
                                                    [origin_index,
                                                     brand_index],
                                                    [origin_synonyms])

        all_results.append(ranking_result)

    sm.saving_formatted_ranking_results(queries, all_results,
                                        rearranged_products,
                                        filename)


main()
