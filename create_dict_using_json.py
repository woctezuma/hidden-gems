# Objective: store information regarding every Steam game in a dictionary.

import urllib.request, json
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

# Boolean to switch between hidden gems and hidden hidden gems (yes, twice hidden)
use_hidden_squared_gems_as_examples = False
max_num_reviews_for_hidden_squared_gems = 150

# This allows to specify a different confidence, which can turn out to be interesting.
quantile_for_our_own_wilson_score = 0.95

if use_hidden_squared_gems_as_examples:
    # Lower the confidence so that Wilson score is less punitive towards games with few reviews
    quantile_for_our_own_wilson_score = 0.8

# Booleans to decide whether we want to filter out and filter in games based on their Steam tags
filter_out_user_chosen_tags = False
filter_in_user_chosen_tags = False

# Tags to filter out
if filter_out_user_chosen_tags:
    # Any game which is tagged with the following tags will be filtered out from the dictionary (and won't appear on the ranking)
    tags_to_filter_out = set(["Visual Novel", "Anime", "VR", "Free to Play",
                              "Match 3", "Hidden Object", "Text-Based", "Touch-Friendly", "Agriculture", "Otome"])
    # A set of tags to better suit the tastes of someone who provided feedback: accept Anime but not Early Access and VR
    # Reference: http://www.neogaf.com/forum/showpost.php?p=241227942&postcount=5880
    # tags_to_filter_out = set(["Early Access", "VR", "Free to Play"])
else:
    # Empty set, so that no game is filered out
    tags_to_filter_out = set()

# This is the appID of the game called "Contradiction".
appidContradiction = "373390"
# This is a set including appID of games which will serve as references of "hidden gems", so we will make sure that
# these games appear in the output dictionary, despite filter-out and filter-in.
# Reference: http://www.neogaf.com/forum/showpost.php?p=241232835&postcount=5886
appid_default_reference_set = {appidContradiction, "320090", "363980", "561740", "333300", "329970", "323220",
                               "534290", "440880", "402040", "233980"}

# Tags to filter in
if filter_in_user_chosen_tags:
    # Only games which are tagged with the following tags will be filtered into the dictionary (so that only such games will appear on the ranking)
    tags_to_filter_in = set(["Rogue-lite", "Rogue-like"])
    # A set of appID to use several games as references of "hidden gems" for the rogue-lite/rogue-like tags
    # Reference: http://www.neogaf.com/forum/showpost.php?p=242425098&postcount=6922
    appid_default_reference_set = {"561740", "333300", "329970", "323220"}
else:
    # Ideally, we should use here the universal set, which would include every tag available on the Steam store.
    tags_to_filter_in = set()
    # However, there is no such set as a universal set in Python, and it is not practical to list every tag,
    # so we use the empty set instead, and rely on a little jig, far below in the code, to filter-in with if/else statements.

D = dict()

verbose = False

for appid in data.keys():
    try:
        name = data[appid]['name']
        num_owners = data[appid]['owners']
        num_players = data[appid]['players_forever']
        median_time = data[appid]['median_forever']
        average_time = data[appid]['average_forever']
        num_positive_reviews = data[appid]["positive"]
        num_negative_reviews = data[appid]["negative"]
        tags_dict = data[appid]["tags"] #TODO remove as tags are not available anymore

        wilson_score = computeWilsonScore(num_positive_reviews, num_negative_reviews, quantile_for_our_own_wilson_score)

        stats_save = [name, wilson_score, num_owners, num_players, median_time, average_time, num_positive_reviews, num_negative_reviews]

        if len(tags_dict) == 0:
            tags = set()
        else:
            tags = set(tags_dict.keys())

        # Check filter-out
        boolPassFilterOut = bool(len(tags_to_filter_out.intersection(tags)) == 0)
        # Check filter-in: either there is no filter-in, or there is filter-in and at least one of the desired tags
        boolPassFilterIn = bool(len(tags_to_filter_in) == 0) or bool(len(tags_to_filter_in.intersection(tags)) != 0)
        boolGameShouldAppearInRanking = (boolPassFilterOut and boolPassFilterIn)
        # We save the boolean due to the presence of a reference game, which we have to include in the dictionary,
        # but which may not appear in the final ranking due to the tag filters.
        stats_save.append(boolGameShouldAppearInRanking)

        # Make sure the output dictionary includes the game which will be chosen as a reference of a "hidden gem"
        if appid in appid_default_reference_set:
            # If we look for hidden squared gems, then we don't want to use examples with many reviews,
            # because these games would be examples of hidden gems, but not examples of "hidden hidden" gems.
            num_reviews = num_positive_reviews + num_negative_reviews
            if not(use_hidden_squared_gems_as_examples) or (num_reviews <= max_num_reviews_for_hidden_squared_gems):
                print("Game used as a reference:\t" + name + "\t(appID=" + appid + ")")
                # If a game is the reference game, we have include it in the dictionary
                D[appid] = stats_save

        else:
            # If a game is not the reference game, then it may only appear in the ranking if it passes the tag filters.
            if boolGameShouldAppearInRanking:
                D[appid] = stats_save

    except KeyError:
        if verbose:
            print("\nAppID:" + appid + "\tWilson score:" + str(wilson_score) + "\tName:" + name)
        continue

# First line of the text file containing the output dictionary
leading_comment = "# Dictionary with key=appid and value=list of name, Wilson score, #owners, #players, median playtime, average playtime, boolean whether to include the game in the ranking"

# Save the dictionary to a text file
with open(output_filename, 'w', encoding="utf8") as outfile:
    print(leading_comment, file=outfile)
    print(D, file=outfile)
