# Getting the 'StudyTimeTracker' Notion Database to a JSON and CSV
# Tony Sandoval
# 05-24-2024

import json
import csv
from datetime import datetime
from notion_client import Client

# Load the API token and the database id from the secret file
try:
    with open("SECRET.json") as file:
        file_contents = file.read()
        data_json = json.loads(file_contents)
        token = data_json["id"]
        database = data_json["database"]
except FileNotFoundError:
    print("Error: The file 'SECRET.json' was not found.")
    exit(1)
except json.JSONDecodeError:
    print("Error: The file 'SECRET.json' contains invalid JSON.")
    exit(1)

# Initialize the Notion client
notion = Client(auth=token)


# Utility function to safely get nested properties
def safe_get(data, dot_chained_keys):
    keys = dot_chained_keys.split(".")
    for key in keys:
        try:
            if isinstance(data, list):
                data = data[int(key)]
            else:
                data = data[key]
        except (KeyError, TypeError, IndexError):
            return None
    return data


# Function to fetch data from Notion
def get_pages():
    response = notion.databases.query(database_id=database)
    return response["results"]


# Main function to process the data and save it as CSV and JSON
def main():
    # Fetch data from Notion
    db_rows = get_pages()

    simple_rows = []

    for row in db_rows:
        title = safe_get(row, "properties.Title.title.0.plain_text")
        date = safe_get(row, "properties.Date.date.start")
        week = safe_get(row, "properties.Week.select.name")
        month = safe_get(row, "properties.Month.select.name")
        week_day = safe_get(row, "properties.Week Day.select.name")
        start_time = safe_get(row, "properties.Start Time.created_time")
        end_time = safe_get(row, "properties.End Time.last_edited_time")
        total_minutes = safe_get(row, "properties.Total Minutes.formula.number")
        energy_level = safe_get(row, "properties.Energy Level.select.name")
        feeling = safe_get(row, "properties.Feeling.select.name")
        comments = safe_get(row, "properties.Comments.rich_text.0.plain_text")

        simple_rows.append(
            {
                "title": title,
                "date": date,
                "week": week,
                "month": month,
                "week_day": week_day,
                "start_time": start_time,
                "end_time": end_time,
                "total_minutes": total_minutes,
                "energy_level": energy_level,
                "feeling": feeling,
                "comments": comments,
            }
        )

    # Create filenames based on the current date
    date_str = datetime.now().strftime("%Y-%m-%d")
    csv_file_name = f"notion_backup_{date_str}.csv"
    json_file_name = f"notion_backup_{date_str}.json"

    # Save the results to a CSV file
    with open(csv_file_name, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=simple_rows[0].keys())
        writer.writeheader()
        writer.writerows(simple_rows)

    # Save the results to a JSON file
    with open(json_file_name, mode="w", encoding="utf-8") as file:
        json.dump(simple_rows, file, indent=4)


if __name__ == "__main__":
    main()
