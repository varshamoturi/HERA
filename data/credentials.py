import csv
import json

# Initialize a list to store your results
results = []

# Path to your CSV file
csv_file_path = 'data.csv'

# Open the CSV file and read data
with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    # Read each row of the CSV file and select only 'username' and 'password'
    for row in csv_reader:
        # Extract only the username and password columns
        user_info = {
            'username': row['username'],
            'password': row['password']
        }
        results.append(user_info)

# Optionally, print results to the console
print(results)

# Write results to a JSON file
with open('credentials.json', mode='w', encoding='utf-8') as json_file:
    json.dump(results, json_file, indent=2)
