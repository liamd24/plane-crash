import requests
from bs4 import BeautifulSoup
import json

all_data = {}
year = 1920
end_year = 2024
instance = 1
json_file = "data/data.json"

while year < end_year:
    # url constructor
    url = f"https://www.planecrashinfo.com/{year}/{year}-{instance}.htm"
    response = requests.get(url)

    # update year and instance when no more data is found for the year
    if response.status_code != 200:
        year += 1
        instance = 1

        # break if year > 2024
        if year > end_year:
            break

        # else retry
        continue
    
    # parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # get table of accident
    rows = soup.find_all('tr')

    # get all rows from table
    current_data = {}
    for i in range(1, len(rows)):
        # skip table header and get columns
        row_columns = rows[i].find_all('td')
        info = row_columns[0].find('b').text.strip()[:-1].replace("\n        ", " ")
        data = row_columns[1].find('font').text.strip().replace("\u00a0 ", " ")

        current_data = current_data | {info: data}
    
    # add data to all_data dictionary
    if str(year) not in all_data:
        all_data[str(year)] = {}
        if str(instance) not in all_data[str(year)]:
            all_data[str(year)][str(instance)] = {}
    
    if current_data:
        all_data[str(year)][str(instance)] = current_data
        print(f"Succesfully scraped data for {year}-{instance}.")
    
    # increment instance for next row of year
    instance += 1


# save data to JSON file
with open(json_file, 'w') as file:
    json.dump(all_data, file, indent=4)

# print completion message
print(f"Data scraping completed. Data saved to {json_file}.")