# Objective: store information regarding every Steam game in a dictionary.
#
# Input:
#
# - a text file, copied from SteamDB, named "top_rated_games_on_steam.txt"
input_filename = "top_rated_games_on_steam.txt"
# NB: To download & copy the content of input_filename by yourself, you need to log in using your own Steam account on
#     https://steamdb.info/stats/gameratings/?all and then select to show all in the dropdown menu.
#
# - a json file, downloaded from SteamSpy, named "steamspy.json"
json_filename = "steamspy.json"
# NB: To download & copy the content of json_filename by yourself, you need to use the API of SteamSpy on:
#     http://steamspy.com/api.php?request=all and then click on the "Save" button.
#
# Output:
#
# a dictionary stored in a text file named "dict_top_rated_games_on_steam.txt"
output_filename = "dict_top_rated_games_on_steam.txt"

import json

D = dict()

verbose = False

with open(json_filename, 'r', encoding="utf8") as in_json_file:
    data = json.load(in_json_file)

with open(input_filename, 'r', encoding="utf8") as infile:
    for line in infile:

        items = line.strip().split("\t")
        stripped_items = list(map(str.strip, items))

        appid = stripped_items[1]
        name = stripped_items[2]
        wilson_score_str = stripped_items[-2]

        wilson_score = float(wilson_score_str.strip("%"))/100

        try:
            num_owners = data[appid]['owners']
            num_players = data[appid]['players_forever']
            median_time = data[appid]['median_forever']

            stats_save = [name, wilson_score, num_owners, num_players, median_time]
            D[appid] = stats_save

        except KeyError:
            if verbose:
                print("\nAppID:" + appid + "\tWilson score:" + str(wilson_score) + "\tName:" + name)
            continue

# First line of the text file containing the output dictionary
leading_comment = "# Dictionary with key=appid and value=list of name, Wilson score, #owners, #players, median playtime"

# Save the dictionary to a text file
with open(output_filename, 'w', encoding="utf8") as outfile:
    print(leading_comment, file=outfile)
    print(D, file=outfile)
