# Objective: download and cache data from SteamSpy

from urllib.request import urlopen
import json
import pathlib

def downloadSteamSpyData(json_filename = "steamspy.json", genre = None, tag = None):

    # Data folder
    data_path = "data/"
    # Reference of the following line: https://stackoverflow.com/a/14364249
    pathlib.Path(data_path).mkdir(parents=True, exist_ok=True)

    data_filename = data_path + json_filename

    # If json_filename is missing, we will attempt to download and cache it from steamspy_url:
    steamspy_url = "http://steamspy.com/api.php?request=all"

    # Provide a possibility to download data for a given genre
    if bool(not(genre is None)):
        print("Focusing on genre " + genre)
        formatted_str = genre.replace(" ", "+")
        steamspy_url = "http://steamspy.com/api.php?request=genre&genre=" + formatted_str
    # Provide a possibility to download data for a given tag
    elif bool(not(tag is None)):
        print("Focusing on tag " + tag)
        formatted_str = tag.replace(" ", "+")
        steamspy_url = "http://steamspy.com/api.php?request=tag&tag=" + formatted_str

    try:
        with open(data_filename, 'r', encoding="utf8") as in_json_file:
            data = json.load(in_json_file)
    except FileNotFoundError:
        print("Downloading and caching data from SteamSpy")
        with urlopen(steamspy_url) as response:
            # Reference: https://stackoverflow.com/a/32169442
            raw_data = response.read()
            encoding = response.info().get_content_charset('utf8')  # JSON default
            data = json.loads(raw_data.decode(encoding))
            # Make sure the json data is using double quotes instead of single quotes
            # Reference: https://stackoverflow.com/a/8710579/
            jsonString = json.dumps(data)
            # Cache the json data to a local file
            with open(data_filename, 'w', encoding="utf8") as cache_json_file:
                print(jsonString, file=cache_json_file)

    return data

if __name__ == "__main__":
    import time

    json_filename_suffixe = "_steamspy.json"

    # Get current day as yyyymmdd format
    date_format = "%Y%m%d"
    current_date = time.strftime(date_format)

    # Database filename
    json_filename = current_date + json_filename_suffixe

    # SteamSpy's data in JSON format
    data = downloadSteamSpyData(json_filename)
