import pandas as pd
import json
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")  # Update if using a remote MongoDB
db = client["kaggle_db"]  # Database name
collection = db["job_postings"]  # Collection name

# Path to CSV file (Modify as per your system)
csv_file_path = "/Users/nandithan/Downloads/postings.csv"  

# Load CSV into Pandas DataFrame
df = pd.read_csv(csv_file_path)

# Convert DataFrame to JSON format
data = df.to_dict(orient="records")  # Converts rows to list of JSON-like dictionaries

# Insert data into MongoDB
if data:
    collection.insert_many(data)  # Insert multiple job postings
    print(f"Inserted {len(data)} job postings into MongoDB!")
else:
    print("No data found in CSV file.")
