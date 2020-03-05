import datetime
import requests

# url for usgs
api_url = "https://earthquake.usgs.gov/fdsnws/event/1/"

# metadata / info about the data
data_format = "geojson"
eventtype = "earthquake"

# for checking the total earthquakes acquired
total_earthquakes = 0

class Earthquake:
    label = ""
    time = ""
    lat = ""
    lon = ""
    depth = ""
    
    def __init__(self, mag, place, time, lat, lon, depth):
        self.label = f"M{mag} {place}"
        self.time = self.format_time(time)
        self.lat = lat
        self.lon = lon
        self.depth = depth

    def format_time(self, unformatted_time):
        dt = datetime.datetime.utcfromtimestamp(unformatted_time/1000).isoformat()
        return dt

def get_eq(count_url, data_url):
    eq_list = []

    count_json = requests.get(count_url).json()
    count = count_json["count"]

    data_json = requests.get(data_url).json()
    data = data_json["features"]

    print(f"Number of earthquakes: {count}")

    for i in range(len(data)):

        data_mag = data[i]["properties"]["mag"]
        data_place = data[i]["properties"]["place"]
        data_time = data[i]["properties"]["time"]

        # according to the USGS website, have the data of longitude before latitude
        data_lon = data[i]["geometry"]["coordinates"][0]
        data_lat = data[i]["geometry"]["coordinates"][1]
        data_depth = data[i]["geometry"]["coordinates"][2]

        eq = Earthquake(data_mag, data_place, data_time, data_lat, data_lon, data_depth)
        eq_list.append(eq)
    
    return eq_list

def parse_url(minmag, maxmag=10, starttime="", endtime=""):
    count_url = f"{api_url}count?format={data_format}&minmagnitude={minmag}&maxmagnitude={maxmag}&eventtype={eventtype}"
    data_url = f"{api_url}query?format={data_format}&minmagnitude={minmag}&maxmagnitude={maxmag}&eventtype={eventtype}"

    if starttime != "" and endtime != "":
        starttime += f"&starttime={starttime}&endtime={endtime}"
        endtime += f"&starttime={starttime}&endtime={endtime}"

    return count_url, data_url