# Objective: store information regarding every Steam game in a dictionary.
#
# Input:
#
# - a text file, manually copied from SteamDB, named "top_rated_games_on_steam.txt"
input_filename = "top_rated_games_on_steam.txt"
steamdb_url = "https://steamdb.info/stats/gameratings/?all"
# NB: To download & copy the content of input_filename by yourself, you need to log in using your own Steam account on
#     steamdb_url and then select to show all in the dropdown menu.
#
# - a json file, downloaded from SteamSpy, named "steamspy.json"
json_filename = "steamspy.json"
steamspy_url = "http://steamspy.com/api.php?request=all"
# NB: If json_filename is missing, the current script will attempt to download and cache it from steamspy_url.
#
# Output:
#
# a dictionary stored in a text file named "dict_top_rated_games_on_steam.txt"
output_filename = "dict_top_rated_games_on_steam.txt"

import urllib.request, json
from compute_wilson_score import computeWilsonScore

# Optional boolean to decide whether we want to compute the Wilson score by ourselves, instead of using SteamDB's scores
compute_our_own_wilson_score = False
# This allows to specify a different confidence, which can turn out to be interesting.
quantile_for_our_own_wilson_score = 0.95

# Booleans to decide whether we want to filter out and filter in games based on their Steam tags
filter_out_user_chosen_tags = False
filter_in_user_chosen_tags = False

# Tags to filter out
if filter_out_user_chosen_tags:
    # Any game which is tagged with the following tags will be filtered out from the dictionary (and won't appear on the ranking)
    tags_to_filter_out = set(["Visual Novel", "Anime", "VR", "Free to Play"])
else:
    # Empty set, so that no game is filered out
    tags_to_filter_out = set()

# Tags to filter in
if filter_in_user_chosen_tags:
    # Only games which are tagged with the following tags will be filtered into the dictionary (so that only such games will appear on the ranking)
    tags_to_filter_in = set(["Rogue-lite", "Rogue-like"])
else:
    # Ideally, we should use here the universal set, which would include every tag available on the Steam store.
    tags_to_filter_in = set()
    # However, there is no such set as a universal set in Python, and it is not practical to list every tag,
    # so we use the empty set instead, and rely on a little jig, far below in the code, to filter-in with if/else statements.

# This is the appID of the game called "Contradiction".
appidContradiction = "373390"
# This is the appID of the game which will be later used as a reference of a "hidden gem", so we will make sure that
# this game appears in the output dictionary, despite filter-out and filter-in.
appidGameUsedAsDefaultReferenceForHiddenGem = appidContradiction

D = dict()

verbose = False

try:
    with open(json_filename, 'r', encoding="utf8") as in_json_file:
        data = json.load(in_json_file)
except FileNotFoundError:
    print("Downloading and caching data from SteamSpy")
    # Trick to download the JSON file directly from SteamSpy, in case the file does not exist locally yet
    # Reference: https://stackoverflow.com/a/31758803/
    class AppURLopener(urllib.request.FancyURLopener):
        version = "Mozilla/5.0"
    opener = AppURLopener()
    with opener.open(steamspy_url) as response:
        data = json.load(response)
        # Make sure the json data is using double quotes instead of single quotes
        # Reference: https://stackoverflow.com/a/8710579/
        jsonString = json.dumps(data)
        # Cache the json data to a local file
        with open(json_filename, 'w', encoding="utf8") as cache_json_file:
            print(jsonString, file=cache_json_file)

with open(input_filename, 'r', encoding="utf8") as infile:
    for line in infile:

        items = line.strip().split("\t")
        stripped_items = list(map(str.strip, items))

        appid = stripped_items[1]
        name = stripped_items[2]

        toInteger = lambda str : int(str.replace(',',''))

        num_positives = toInteger(stripped_items[3])
        num_negatives = toInteger(stripped_items[4])

        toPercentage = lambda str : float(str.strip("%"))/100

        wilson_score_from_SteamDB = toPercentage(stripped_items[-2])
        steam_score = toPercentage(stripped_items[-1])

        if compute_our_own_wilson_score:
            wilson_score = computeWilsonScore(num_positives, num_negatives, quantile_for_our_own_wilson_score)
        else:
            wilson_score = wilson_score_from_SteamDB

        try:
            num_owners = data[appid]['owners']
            num_players = data[appid]['players_forever']
            median_time = data[appid]['median_forever']
            average_time = data[appid]['average_forever']
            tags_dict = data[appid]["tags"]

            stats_save = [name, wilson_score, num_owners, num_players, median_time, average_time]

            if len(tags_dict) == 0:
                tags = set()
            else:
                tags = set(tags_dict.keys())

            # Make sure the output dictionary includes the game which will be chosen as a reference of a "hidden gem"
            if appid == appidGameUsedAsDefaultReferenceForHiddenGem:
                print("Game used as a reference:\t" + name + "\t(appID=" + appid + ")")
                D[appid] = stats_save
            else:
                # For every other game, check the filter-out and filter-in tags
                if len( tags_to_filter_out.intersection(tags) ) == 0:
                    if len(tags_to_filter_in) == 0:
                        # Either there is no filter-in
                        D[appid] = stats_save
                    else:
                        if len(tags_to_filter_in.intersection(tags)) != 0:
                            # Or there is filter-in, and there is at least one of the desired tags
                            D[appid] = stats_save

        except KeyError:
            if verbose:
                print("\nAppID:" + appid + "\tWilson score:" + str(wilson_score) + "\tName:" + name)
            continue

# First line of the text file containing the output dictionary
leading_comment = "# Dictionary with key=appid and value=list of name, Wilson score, #owners, #players, median playtime, average playtime"

# Save the dictionary to a text file
with open(output_filename, 'w', encoding="utf8") as outfile:
    print(leading_comment, file=outfile)
    print(D, file=outfile)
