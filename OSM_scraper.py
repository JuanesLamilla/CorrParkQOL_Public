from geopy.geocoders import Nominatim
from area import area
import pandas as pd
import requests
from osmtogeojson import osmtogeojson
from datetime import datetime

# Timer
# ----------------------------------------------------------------------------
timer = 0
start_time = datetime.now()
print("Program start at {}".format(start_time))
# ----------------------------------------------------------------------------

url = "http://overpass-api.de/api/interpreter"

df = pd.read_csv('Cities_QOL.csv')

# Geocoding request through Nominatim
geolocator = Nominatim(user_agent="Enter_User_Agent_Here")

# Iterate through each city -> geocode for location -> request parking data from OSM
for index, row in df.iterrows():
    city_name = row['Origin']

    # Timer
    # ----------------------------------------------------------------------------
    if timer % 25 == 0:
        print(str(timer / 2.5) + "%")
        print("Time Elapsed: {}".format(datetime.now()-start_time))
    timer += 1
    # ----------------------------------------------------------------------------

    geo_results = geolocator.geocode(city_name, exactly_one=False, limit=3, timeout=None)

    if geo_results == None:
        print("Unable to find city: " + str(city_name))
        continue

    # Search for relation in result set
    for r in geo_results:
        if r.raw.get("osm_type") == "relation":
            city = r
            break

    # Calculate city id
    area_id = int(city.raw.get("osm_id")) + 3600000000

    # Excecuting overpass calls through 'requests'
    query_way = """
        [out:json];
        area(%s)->.searchArea;
        (
        way["amenity"="parking"](area.searchArea);
        );
        (._;>;);
        out body;
        """ % area_id

    query_relation = """
        [out:json];
        area(%s)->.searchArea;
        (
        relation["amenity"="parking"](area.searchArea);
        );
        (._;>;);
        out body;
        """ % area_id

    r_way = requests.get(url, params={'data': query_way})
    r_relation = requests.get(url, params={'data': query_relation})

    # Convert JSON to GEOJSON for easy area calculation
    result_way = osmtogeojson.process_osm_json(r_way.json())
    result_relation = osmtogeojson.process_osm_json(r_relation.json())

    # Calculate total parking area using 'area'
    total_area = 0
    for feature in result_way['features']:
        total_area += area(feature['geometry'])

    for feature in result_relation['features']:
        total_area += area(feature['geometry'])

    # Add city parking area to dataframe
    df.at[index, "Total_Parking_Area"] = total_area

# Save dataframe to CSV
df.to_csv('Cities_QOL.csv', index=False)
print("All finished. Final time: {}".format(datetime.now()-start_time))