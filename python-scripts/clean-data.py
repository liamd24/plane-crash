# Date                  |  DateTime yyyy-mm-dd hh:mm:ss[.fffffffff] [optional]
# Time                  |  Time hh:mm:ss[.fffffffff] [optional]
# Location              |  Location
# Operator              |  Operator
# Flight #              |  Flight #
# Route                 |  From, To
# AC Type               |  Aircraft Type
# Registration          |  Registration
# cn / ln               |  Serial Number
# Aboard                |  Crew, Passengers, Total
# Fatalities            |  Crew, Passengers, Total
# Ground                |  Ground Fatalities
# Summary               |  Summary
# Source to original    |  https://www.planecrashinfo.com/year/year-instance.htm

# Changes to make:
# Change all "?" to "Unknown"
# Convert Date, Time to yyyy-mm-dd hh:mm:ss format (unknown times are set to 00:00:00)
# Remove "Near " from Location
# Change Route to two seperate columns: From, To (use string - ??? - string for start and end destinations)
# Change Aboard, Fatalities to Crew, Passengers, Total for both (total = crew + passengers; unknown = -1)
# Add source to original column with the URL of the original data
# Add lat and long coordinates for the location using Google Maps Geocoding API

import os
import json
import re
import requests
from dotenv import load_dotenv
import time as t

# Load environment variables from .env file
load_dotenv()

geocoding_api_key = os.getenv("GKEY")
print(f"API Key loaded: {geocoding_api_key is not None}")
if geocoding_api_key is None:
    print("Environment variable GKEY not found!")

start_year = 1920

with open("data/data.json", "r") as file:
    all_data = json.load(file)
    new_data = {}
    iterator = 0

    for i in range(start_year, len(all_data) + start_year):
        year = all_data[str(i)]
        new_data[str(i)] = {}
        if not year: continue

        for j in range(1, len(year) + 1):
            instance = year[str(j)]
            if not instance: continue

            # source URL for the original data
            source = f"https://www.planecrashinfo.com/{i}/{i}-{j}.htm"

            # get dates into month, day, year format
            dates_seperate = re.split("\s", instance["Date"])
            dates_seperate[1] = dates_seperate[1][:-1]
            
            # get time into hh:mm:ss format
            time = instance["Time"]
            if time == "?": time = "0000"
            time_split = f"{time[:2]}:{time[2:]}:00"
            
            # create datetime string in yyyy-mm-dd hh:mm:ss format
            datetime = f"{dates_seperate[2]}-{dates_seperate[0]}-{dates_seperate[1]} {time_split}"

            # get location without "Near " or "Off "
            if instance["Location"] == "?": location = "Unknown"
            else: location = instance["Location"].replace("Near ", "").replace("Off ", "").encode("utf-8").decode("unicode_escape")

            # get values and handle "?" cases
            # also handle unicode escape sequences
            if instance["Operator"] == "?": operator = "Unknown"
            else: operator = instance["Operator"].encode("utf-8").decode("unicode_escape")

            if instance["Flight #"] == "?": flight_number = "Unknown"
            else: flight_number = instance["Flight #"].encode("utf-8").decode("unicode_escape")

            if instance["Route"] == "?":
                route_start = "Unknown"
                route_end = "Unknown"
            else:
                route_start = instance["Route"].split("-")[0].strip().encode("utf-8").decode("unicode_escape")
                route_end = instance["Route"].split("-")[-1].strip().encode("utf-8").decode("unicode_escape")

            if instance["AC Type"] == "?": aircraft_type = "Unknown"
            else: aircraft_type = instance["AC Type"].encode("utf-8").decode("unicode_escape")

            if instance["Registration"] == "?": registration = "Unknown"
            else: registration = instance["Registration"].encode("utf-8").decode("unicode_escape")

            if instance["cn / ln"] == "?": serial_number = "Unknown"
            else: serial_number = instance["cn / ln"].encode("utf-8").decode("unicode_escape")

            if instance["Summary"] == "?": summary = "Unknown"
            else: summary = instance["Summary"].encode("utf-8").decode("unicode_escape")

            # split Aboard and Fatalities into Crew, Passengers, Total for each
            total_aboard = re.findall(r"^\S+\s", instance["Aboard"])[0]
            if total_aboard == "? ":
                total_aboard = -1
                passengers_aboard = -1
                crew_aboard = -1
            else:
                total_aboard = int(total_aboard.strip())
                
                passengers_aboard = re.findall(r"\(\S+\:\S+\s", instance["Aboard"])[0]
                colon = passengers_aboard.index(":")
                passengers_aboard = passengers_aboard[colon+1:-1].strip()

                try: passengers_aboard = int(passengers_aboard)
                except TypeError: passengers_aboard = -1
                except ValueError: passengers_aboard = -1

                crew_aboard = re.findall(r"\:\S+\)", instance["Aboard"])[0]
                crew_aboard = crew_aboard[1:-1].strip()

                try: crew_aboard = int(crew_aboard)
                except TypeError: crew_aboard = -1
                except ValueError: crew_aboard = -1

            # split Fatalities into Crew, Passengers, Total for each
            total_fatalities = re.findall(r"^\S+\s", instance["Fatalities"])[0]
            if total_fatalities == "? ":
                total_fatalities = -1
                passengers_fatalities = -1
                crew_fatalities = -1
            else:
                total_fatalities = int(total_fatalities.strip())

                passengers_fatalities = re.findall(r"\(\S+\:\S+\s", instance["Fatalities"])[0]
                colon = passengers_fatalities.index(":")
                passengers_fatalities = passengers_fatalities[colon+1:-1].strip()

                try: passengers_fatalities = int(passengers_fatalities)
                except TypeError: passengers_fatalities = -1
                except ValueError: passengers_fatalities = -1

                crew_fatalities = re.findall(r"\:\S+\)", instance["Fatalities"])[0]
                crew_fatalities = crew_fatalities[1:-1].strip()

                try: crew_fatalities = int(crew_fatalities)
                except TypeError: crew_fatalities = -1
                except ValueError: crew_fatalities = -1

            # handle ground fatalities
            if instance["Ground"] == "?": ground_fatalities = -1
            else:
                ground_fatalities = int(instance["Ground"].strip())
                total_fatalities += ground_fatalities

            # approximate lat and long for displaying on a map
            # uses Google Maps Geocoding API
            if location == "Unknown": pass
            else:
                # rate limit for Geocoding API just under actual 3000 req / minute
                iterator += 1
                if iterator > 2500:
                    print("\nGeocoding API limit reached, waiting for 120 seconds...\n")
                    t.sleep(120)
                    iterator = 0
                
                urlencoded_location = location.replace(",", "").replace(" ", "%20")
                geocoding_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urlencoded_location}&key={geocoding_api_key}"
                print(f"\nGeocoding URL: {geocoding_url}")
                response = requests.get(geocoding_url)
                if response.status_code == 200:
                    geocoding_data = response.json()
                    if geocoding_data["status"] == "OK":
                        latitude = geocoding_data["results"][0]["geometry"]["location"]["lat"]
                        longitude = geocoding_data["results"][0]["geometry"]["location"]["lng"]
                    else:
                        latitude = None
                        longitude = None
                else:
                    latitude = None
                    longitude = None
            
            new_data[str(i)][str(j)] = {
                "DateTime": datetime,
                "Location": location,
                "Operator": operator,
                "FlightNum": flight_number,
                "RouteStart": route_start,
                "RouteEnd": route_end,
                "AircraftType": aircraft_type,
                "Registration": registration,
                "SerialNumber": serial_number,
                "CrewAboard": crew_aboard,
                "PassengersAboard": passengers_aboard,
                "TotalAboard": total_aboard,
                "CrewFatalities": crew_fatalities,
                "PassengersFatalities": passengers_fatalities,
                "GroundFatalities": ground_fatalities,
                "TotalFatalities": total_fatalities,
                "Summary": summary,
                "Latitude": latitude,
                "Longitude": longitude,
                "SourceToOriginal": source
            }

            print(f"Everything has worked on {i}-{j}")
    
    with open("data/cleaned_data.json", "w") as clean_file:
        json.dump(new_data, clean_file, indent=4)
