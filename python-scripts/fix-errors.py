import json
import re

months = ["January", "February", "March", "April",
          "May", "June", "July", "August", 
          "September", "October", "November", "December"]

with open("data/cleaned_data.json", "r") as file:
    data = json.load(file)
    new_data = {}

    for i in range(1920, 1922):
        year = data[str(i)]
        if not year: continue

        new_data[str(i)] = {}

        for j in range(1, 1 + len(year)):
            instance = year[str(j)]

            datetime = instance["DateTime"]
            month = datetime.split("-")[1]

            if month in months:
                month_index = months.index(month) + 1
                month_str = str(month_index).zfill(2)
                datetime = datetime.replace(f"-{month}-", f"-{month_str}-")
            
            instance["DateTime"] = datetime
            new_data[str(i)][str(j)] = instance

with open("data/fixed-errors.json", "w") as file:
    json.dump(new_data, file, indent=4)