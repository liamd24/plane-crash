import json
import re

months = ["January", "February", "March", "April",
          "May", "June", "July", "August", 
          "September", "October", "November", "December"]

start_year = 1920

with open("data/cleaned_data.json", "r") as file:
    all_data = json.load(file)
    new_data = {}
    iterator = 0

    for i in all_data.keys():
        year = all_data[i]
        new_data[i] = {}
        if not year: continue

        for j in year.keys():
            instance = year[j]
            if not instance: continue

            datetime = instance["DateTime"]
            month = datetime.split("-")[1]

            if month in months:
                month_index = months.index(month) + 1
                month_str = str(month_index).zfill(2)
                datetime = datetime.replace(f"-{month}-", f"-{month_str}-")
            
            instance["DateTime"] = datetime
            new_data[str(i)][j] = instance

with open("data/fixed-errors.json", "w") as file:
    json.dump(new_data, file, indent=4)
    print("Fixed errors and saved to data/fixed-errors.json")