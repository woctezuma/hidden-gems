# Objective: download and cache data from SteamSpy

import json
import pathlib
from pathlib import Path

import steamspypi


def download_steam_spy_data(json_filename="steamspy.json", genre=None):
    # Data folder
    data_path = "data/"
    # Reference of the following line: https://stackoverflow.com/a/14364249
    pathlib.Path(data_path).mkdir(parents=True, exist_ok=True)

    data_filename = data_path + json_filename

    try:
        with Path(data_filename).open(encoding="utf8") as in_json_file:
            data = json.load(in_json_file)
    except FileNotFoundError:
        print("Downloading and caching data from SteamSpy")

        if genre is None:
            data = steamspypi.load()
        else:
            data_request = {}
            data_request['request'] = 'genre'
            data_request['genre'] = genre

            data = steamspypi.download(data_request)

        steamspypi.print_data(data, data_filename)

    return data


def get_appid_by_keyword(keyword):
    import time

    json_filename_suffixe = "_steamspy.json"

    # Get current day as yyyymmdd format
    date_format = "%Y%m%d"
    current_date = time.strftime(date_format)

    # Database filename
    json_filename = current_date + json_filename_suffixe

    # Download data which meta-data includes this keyword as genre
    data_genre = download_steam_spy_data(
        "genre_" + keyword + "_" + json_filename,
        keyword,
    )

    app_ids = set(data_genre.keys())

    return app_ids


def get_appid_by_keyword_list_to_include(keyword_list):
    app_ids = None  # This variable will be initialized during the first iteration.
    is_first_iteration = True

    for keyword in keyword_list:
        current_app_ids = get_appid_by_keyword(keyword)
        if len(current_app_ids) == 0:
            print("The keyword " + keyword + " does not return any appID.")
        if is_first_iteration:
            app_ids = current_app_ids
            is_first_iteration = False
        else:
            # Intersection of appIDs so that the result are appIDs which correspond to every keyword
            app_ids = app_ids.intersection(current_app_ids)

    return app_ids


def get_appid_by_keyword_list_to_exclude(keyword_list):
    app_ids = set()  # This is the true initialization of this variable.

    for keyword in keyword_list:
        current_app_ids = get_appid_by_keyword(keyword)
        if len(current_app_ids) == 0:
            print("The keyword " + keyword + " does not return any appID.")
        # Union of appIDs so that the result are appIDs which correspond to at least one keyword
        app_ids = app_ids.union(current_app_ids)

    return app_ids


if __name__ == "__main__":
    steamspypi.load()
