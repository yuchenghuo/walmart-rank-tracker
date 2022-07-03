#!/usr/bin/python3

import csv
import datetime
import json
import os
from collections import defaultdict
from serpapi import GoogleSearch
from os.path import exists

API_KEY = "CHANGE TO YOUR SERPAPI API KEY"
PRODUCT_IDS = [
    # Product IDs for Walmart
]
QUERIES = [
    # Queries for Searches
]
CSV_FILE_NAME = "ranks.csv"  # Change to customize csv file name
JSON_FILE_NAME = "ranks.json"  # Change to customize json file name


def get_params(query, page_num):
    return {
        "engine": "walmart",
        "query": query,
        "page": str(page_num),
        "device": "mobile",
        "api_key": API_KEY,
        "no_cache": "true",  # Change to "false" to use cached results
    }


def get_rank_by_query_and_pid(query):
    count_non_sponsored = 0
    ranks = [-1] * len(PRODUCT_IDS)
    for page_num in range(1, 6):
        # Modify 6 to change the number of pages to search
        params = get_params(query, page_num)
        search = GoogleSearch(params)
        results = search.get_dict()
        results = results["organic_results"]
        pids = [result["us_item_id"]
                if not result["sponsored"] else None for result in results]
        for i, pid in enumerate(PRODUCT_IDS):
            if ranks[i] == -1 and str(pid) in pids:
                ranks[i] = count_non_sponsored + pids.index(str(pid)) + 1
        count_non_sponsored += len(pids)
    return ranks


def get_ranks():
    results = dict()
    for query in QUERIES:
        ranks = get_rank_by_query_and_pid(query)
        for i, r in enumerate(ranks):
            results[f"{PRODUCT_IDS[i]}|{query}"] = "N/A" if r == -1 else r
    return results


def load_data():
    if exists(JSON_FILE_NAME):
        with open(JSON_FILE_NAME, "r") as infile:
            return json.loads(infile.read())
    return dict()


def save_data(data):
    with open(JSON_FILE_NAME, "w") as outfile:
        json.dump(data, outfile)


def save_csv(data):
    rows = defaultdict(dict)
    dates = set()
    for date, results in data.items():
        dates.add(date)
        for key, result in results.items():
            pid, query = key.split('|')
            rows[(pid, query)][date] = result

    if exists(CSV_FILE_NAME):
        os.remove(CSV_FILE_NAME)

    with open(CSV_FILE_NAME, 'w') as outfile:
        writer = csv.writer(outfile)
        header = ['product_id', 'search_term']
        header.extend(sorted(dates))
        writer.writerow(header)
        for (pid, query) in sorted(rows.keys()):
            results = rows[(pid, query)]
            ranks = []
            for d in sorted(dates):
                if d in results:
                    ranks.append(results[d])
                else:
                    ranks.append("N/A")
            row = [pid, query]
            row.extend(ranks)
            writer.writerow(row)


def main():
    data = load_data()
    data[str(datetime.date.today() + datetime.timedelta(days=2))] = get_ranks()
    save_data(data)
    save_csv(data)


if __name__ == "__main__":
    main()

# Uncomment the following lines to run the script automatically periodically
# while True:
#     main()
#     time.sleep(3 * 24 * 60 * 60)
