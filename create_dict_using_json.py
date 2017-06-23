import json
from pprint import pprint

filename = "top_rated_games_on_steam.txt"
json_filename = "steamspy.json"

counter = 0

D = dict()

def parsifyToInt(text):
    return int(text.replace(",", ""))

with open(json_filename, 'r', encoding="utf8") as in_json_file:
    data = json.load(in_json_file)

with open(filename, 'r', encoding="utf8") as infile:
    for line in infile:

        items = line.strip().split("\t")
        stripped_items = list(map(str.strip, items))

        appid = stripped_items[1]
        name = stripped_items[2]
        wilson_score_str = stripped_items[-2]

        wilson_score = float(wilson_score_str.strip("%"))/100

        counter += 1
        if True:
            print("\n" + name + "\t" + str(wilson_score) + "\n" + appid)

            try:
                alltime_peak = -1 # Not available
                num_owners = data[appid]['owners']
                num_players = data[appid]['players_forever']
                median_time = data[appid]['owners']

                stats_save = [name, wilson_score, alltime_peak, num_owners, num_players, median_time]

                print(stats_save)

                D[appid] = stats_save
            except KeyError:
                continue

print(D)
