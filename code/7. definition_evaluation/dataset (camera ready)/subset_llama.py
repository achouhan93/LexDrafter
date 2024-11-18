import json

# Load the JSON data from files
with open("llama_definition_combined.json", "r") as file:
    larger_data = json.load(file)

with open("vicuna_definition_combined.json", "r") as file:
    smaller_data = json.load(file)

# Convert smaller data to a set of tuples for faster lookup
smaller_data_set = {
    (item["term"], item["celex_id"])
    for item in smaller_data
    if item["generated_definition"] != "NO JSON AS AN OUTPUT OBTAINED"
}

# Select records from larger data that are also in smaller data
common_records = [
    item for item in larger_data if (item["term"], item["celex_id"]) in smaller_data_set
]

# Optionally, save the common records to a new JSON file
with open("llama_subset_records.json", "w") as file:
    json.dump(common_records, file, indent=4)

# Print the number of common records found
print(f"Number of common records: {len(common_records)}")
