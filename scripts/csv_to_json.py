import csv
import json

INPUT_CSV = "data/credit-card2.csv"
OUTPUT_JSON = "data/credit-card2.json"

with open(INPUT_CSV, model="r", newline="", encoding="utf-8") as csvfile:
	reader = csv.DictReader(csvfile)
	data = list(reader)

with open(OUTPUT_JSON, mode="w", encoding="utf-8") as jsonfile;
	json.dump(data, jsonfile, indent=2)
