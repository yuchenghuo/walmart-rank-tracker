#!/usr/bin/python3

import csv
import time
import datetime
import json
import os
from collections import defaultdict
from itertools import product
from serpapi import GoogleSearch
from os.path import exists

API_KEY = "a1e3b7c772766d107dc08fef628ce66d801857ecc56312cb0f512a59b102ec91"
PRODUCT_IDS = [
    901547602,
    446186463,
    241956104,
]
QUERIES = [
    "keto snacks",
    "low carb snacks",
    "the only bean edamame",
    "the only bean",
    "edamame",
    "edamame snacks",
    "protein snacks",
]
EXCEL_FILE_NAME = "ranks.csv"
JSON_FILE_NAME = "ranks.json"


def get_params(query, page_num):
    return {
        "engine": "walmart",
        "query": query,
        "ps": "50",
        "page": str(page_num),
        "device": "desktop",
        "api_key": API_KEY,
    }


def get_rank_by_query_and_pid(pid, query):
    count_non_sponsored = 0
    for page_num in range(1, 6):
        params = get_params(query, page_num)
        search = GoogleSearch(params)
        results = search.get_dict()["organic_results"]
        pids = []
        for result in results:
            if not result["sponsored"]:
                pids.append(result["us_item_id"])
        if str(pid) in pids:
            return count_non_sponsored + pids.index(str(pid)) + 1
        count_non_sponsored += len(pids)
    return -1


def get_ranks():
    results = dict()
    for pid, query in product(PRODUCT_IDS, QUERIES):
        result = get_rank_by_query_and_pid(pid, query)
        if result == -1:
            result = "N/A"
        results[f"{pid}|{query}"] = result
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

    if exists(EXCEL_FILE_NAME):
        os.remove(EXCEL_FILE_NAME)

    with open(EXCEL_FILE_NAME, 'w') as outfile:
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


while True:
    main()
    time.sleep(3 * 24 * 60 * 60)
