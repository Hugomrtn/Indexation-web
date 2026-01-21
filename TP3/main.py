import search_motor as sm


def get_list_of_queries():
    queries = [
        "box of chocolate orange",
        "italy leather",
    ]
    return queries


def main():
    rearranged_products = sm.read_jsonl("TP3/rearranged_products.jsonl")
    title_index = sm.read_json("TP3/title_index.json")
    description_index = sm.read_json("TP3/description_index.json")
    origin_index = sm.read_json("TP3/origin_index.json")
    origin_synonyms = sm.read_json("TP3/origin_synonyms.json")
    brand_index = sm.read_json("TP3/brand_index.json")

    queries = get_list_of_queries()

    for query in queries:
        print(query, ":")
        ranking_result = sm.provide_ranking_results(query,
                                                    rearranged_products,
                                                    title_index,
                                                    description_index,
                                                    [origin_index,
                                                     brand_index],
                                                    [origin_synonyms])
        print(ranking_result[:10])
        print("\n-----\n")


main()
