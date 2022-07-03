# Walmart Rank Tracker
Automatically track the rank of Walmart products in Walmart search using product ids.
Results are generated in a csv file and can be viewed in a spreadsheet program.
Past results are stored in a json file for easier access.

# How to Use
1. Generate a list of product ids and search queries.
2. Modify PRODUCT_IDS and QUERIES in search.py file.
3. Get an SERPAPI API key from [here](https://serpapi.com/api-key). They only allow 100 free searches per week. Please consider upgrading to their premium subscription if more searches are going to be used. Then update the API_KEY variable in search.py file.
4. [Optional] Uncomment the code at the end to automatically run the program periodically.
