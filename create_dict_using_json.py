# Objective: store information regarding every Steam game in a dictionary.

from download_json import downloadSteamSpyData
from compute_wilson_score import computeWilsonScore

#
# Input:
#
# - SteamSpy's data in JSON format
json_filename = "steamspy.json"
data = downloadSteamSpyData(json_filename)
#
# Output:
#
# a dictionary stored in a text file named "dict_top_rated_games_on_steam.txt"
output_filename = "dict_top_rated_games_on_steam.txt"

# This allows to specify a different confidence, which can turn out to be interesting.
quantile_for_our_own_wilson_score = 0.95

# This is the appID of the game called "Contradiction".
appidContradiction = "373390"
# This is a set including appID of games which will serve as references of "hidden gems", so we will make sure that
# these games appear in the output dictionary, despite filter-out and filter-in.
# Reference: http://www.neogaf.com/forum/showpost.php?p=241232835&postcount=5886
appid_default_reference_set = {appidContradiction, "320090", "363980", "561740", "333300", "329970", "323220",
                               "534290", "440880", "402040", "233980"}

D = dict()

for appid in data.keys():
    name = data[appid]['name']
    num_owners = data[appid]['owners']
    num_players = data[appid]['players_forever']
    median_time = data[appid]['median_forever']
    average_time = data[appid]['average_forever']
    num_positive_reviews = data[appid]["positive"]
    num_negative_reviews = data[appid]["negative"]

    wilson_score = computeWilsonScore(num_positive_reviews, num_negative_reviews, quantile_for_our_own_wilson_score)

    # Make sure the output dictionary includes the game which will be chosen as a reference of a "hidden gem"
    if appid in appid_default_reference_set:
        assert( not(wilson_score is None) )
        print("Game used as a reference:\t" + name + "\t(appID=" + appid + ")")

    if wilson_score is None:
        print("Game with no review:\t" + name + "\t(appID=" + appid + ")")
    else:
        stats_save = [name, wilson_score, num_owners, num_players, median_time, average_time, num_positive_reviews,
                      num_negative_reviews]
        D[appid] = stats_save

# First line of the text file containing the output dictionary
leading_comment = "# Dictionary with key=appid and value=list of name, Wilson score, #owners, #players, median playtime, average playtime, boolean whether to include the game in the ranking"

# Save the dictionary to a text file
with open(output_filename, 'w', encoding="utf8") as outfile:
    print(leading_comment, file=outfile)
    print(D, file=outfile)
