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
    count_sponsored = 0
    ranks_non_sponsored = [-1] * len(PRODUCT_IDS)
    ranks_sponsored = [-1] * len(PRODUCT_IDS)
    for page_num in range(1, 6):
        # Modify 6 to change the number of pages to search
        params = get_params(query, page_num)
        search = GoogleSearch(params)
        results = search.get_dict()
        if "organic_results" not in results:
            break
        results = results["organic_results"]
        pids_non_sponsored = []
        pids_sponsored = []
        for result in results:
            if result["sponsored"]:
                pids_sponsored.append(result["us_item_id"])
            else:
                pids_non_sponsored.append(result["us_item_id"])
        for i, pid in enumerate(PRODUCT_IDS):
            pid = str(pid)
            if ranks_non_sponsored[i] == -1 and pid in pids_non_sponsored:
                ranks_non_sponsored[i] = count_non_sponsored + pids_non_sponsored.index(pid) + 1
            if ranks_sponsored[i] == -1 and pid in pids_sponsored:
                ranks_sponsored[i] = count_sponsored + pids_sponsored.index(pid) + 1
        count_non_sponsored += len(pids_non_sponsored)
        count_sponsored += len(pids_sponsored)
    return ranks_non_sponsored, ranks_sponsored


def get_ranks():
    results_non_sponsored = dict()
    results_sponsored = dict()
    for query in QUERIES:
        ranks_non_sponsored, ranks_sponsored = get_rank_by_query_and_pid(query)
        for i, rank in enumerate(ranks_non_sponsored):
            results_non_sponsored[f"{PRODUCT_IDS[i]}|{query}"] = \
                "N/A" if rank == -1 else rank
        for i, rank in enumerate(ranks_sponsored):
            results_sponsored[f"{PRODUCT_IDS[i]}|{query}"] = \
                "N/A" if rank == -1 else rank
    return results_non_sponsored, results_sponsored


def load_data():
    if exists(JSON_FILE_NAME):
        with open(JSON_FILE_NAME, "r") as infile:
            return json.loads(infile.read())
    return dict()


def save_data(data):
    with open(JSON_FILE_NAME, "w") as outfile:
        json.dump(data, outfile)


def save_csv(data, results_sponsored):
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
        header = ['product_id', 'search_term', 'latest_sponsored_rank']
        header.extend(sorted(dates))
        writer.writerow(header)
        for (pid, query) in sorted(rows.keys()):
            results = rows[(pid, query)]
            ranks = [results_sponsored[f"{pid}|{query}"]]
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
    date = str(datetime.date.today() + datetime.timedelta(days=0))
    data[date], results_sponsored = get_ranks()
    save_data(data)
    save_csv(data, results_sponsored)


if __name__ == "__main__":
    main()

# Uncomment the following lines to run the script automatically periodically
# while True:
#     main()
#     time.sleep(3 * 24 * 60 * 60)
