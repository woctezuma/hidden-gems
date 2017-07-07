# Objective: compute a score for each Steam game and then rank all the games while favoring hidden gems.
#
# Input:
#
# a dictionary stored in a text file named "dict_top_rated_games_on_steam.txt"
input_filename = "dict_top_rated_games_on_steam.txt"
#
# Output:
#
# a ranking in a text file named "hidden_gems.txt"
output_filename = "hidden_gems.txt"

from scipy.optimize import differential_evolution
from math import log10
import numpy as np
# Import a variable (and execute create_dict_using_json.py, maybe because I have not embedded the code in functions)
from create_dict_using_json import appid_default_reference_set

base_steam_store_url = "http://store.steampowered.com/app/"

# Boolean to decide whether printing the ranking of the top 1000 games, rather than the ranking of the whole Steam
# catalog. It makes the script finish faster, and usually, we are only interested in the top games anyway.
print_subset_of_top_games = True
num_top_games_to_print = 1000

# Boolean to switch the scoring method to any alternative which you might want to test.
use_alternative_scoring_method = True

# Import the dictionary from the input file
with open(input_filename, 'r', encoding="utf8") as infile:
    lines = infile.readlines()
    # The dictionary is on the second line
    D = eval(lines[1])

def computeScoreGeneric(tuple, parameter_list):
    # Objective: compute a score for one Steam game.
    #
    # Input:    - a tuple is a list consisting of all retrieved information regarding one game
    #           - parameter_list is a list of parameters to calibrate the ranking.
    #             Currently, there is only one parameter, alpha, which could be chosen up to one's tastes, or optimized.
    # Output:   game score

    alpha = parameter_list[0]

    # Expected minimal playtime for a hidden gem.
    if len(parameter_list) < 2:
        expected_minimal_playtime_in_hours = 10
    else:
        expected_minimal_playtime_in_hours = parameter_list[1]

    # Expected maximal number of reviews for a hidden gem.
    if len(parameter_list) < 3:
        expected_maximal_num_reviews = 50
    else:
        expected_maximal_num_reviews = parameter_list[2]

    # Expected maximal playtime difference for a hidden gem.
    if len(parameter_list) < 4:
        expected_maximal_playtime_difference_in_hours = 10
    else:
        expected_maximal_playtime_difference_in_hours = parameter_list[3]

    game_name = tuple[0]
    wilson_score = tuple[1]
    num_owners = tuple[2]
    num_players = tuple[3]
    median_playtime = tuple[4]
    average_playtime = tuple[5]
    num_positive_reviews = tuple[6]
    num_negative_reviews = tuple[7]

    boolGameShouldAppearInRanking = tuple[-1]

    num_owners = float(num_owners)
    num_players = float(num_players)
    median_playtime = float(median_playtime)
    average_playtime = float(average_playtime)
    num_positive_reviews = float(num_positive_reviews)
    num_negative_reviews = float(num_negative_reviews)

    num_reviews = num_positive_reviews + num_negative_reviews

    quality_measure = wilson_score
    popularity_measure = num_players

    if use_alternative_scoring_method:
        # Convert from minutes to hours
        avg_playtime_hours = average_playtime/60
        median_playtime_hours = median_playtime/ 60
        # Compute ratio between 0 and 1
        if (avg_playtime_hours > expected_minimal_playtime_in_hours)\
                and (num_reviews <= expected_maximal_num_reviews)\
                and (np.abs(median_playtime_hours-avg_playtime_hours) <= expected_maximal_playtime_difference_in_hours):
            quality_measure = wilson_score
        else:
            quality_measure = 0

    # Decreasing function
    decreasing_fun = lambda x: alpha / (alpha + x)

    score = quality_measure * decreasing_fun(popularity_measure)

    return score

# Goal: find the optimal value for alpha by minimizing the rank of games chosen as references of "hidden gems"

def rankGames(parameter_list, verbose = False, appid_reference_set = {373390}):
    # Objective: rank all the Steam games, given a parameter alpha.
    #
    # Input:    - parameter_list is a list of parameters to calibrate the ranking.
    #           - optional verbosity boolean
    #           - optional set of appID of games chosen as references of a "hidden gem".
    #             By default, this is set containing only one game called "Contradiction" (appID=373390).
    # Output:   scalar value summarizing ranks of games used as references of "hidden gems"

    computeScore = lambda x: computeScoreGeneric(x, parameter_list)

    # Rank all the Steam games
    sortedValues = sorted(D.values(), key=computeScore, reverse=True)

    sortedGameNames = list(map(lambda x: x[0], sortedValues))

    reference_dict = {}
    for appid_reference in appid_reference_set:
        # Find the rank of this game used as a reference of a "hidden gem"
        nameGameUsedAsReferenceForHiddenGem = D[appid_reference][0]
        rankGameUsedAsReferenceForHiddenGem = sortedGameNames.index(nameGameUsedAsReferenceForHiddenGem) + 1

        # Find whether the reference game should appear in the ranking (it might not due to tag filters)
        boolReferenceGameShouldAppearInRanking = D[appid_reference][-1]

        reference_dict[appid_reference] = [rankGameUsedAsReferenceForHiddenGem, boolReferenceGameShouldAppearInRanking]

    # Display the ranking in a format parsable by Github Gist
    if verbose:
        num_games_to_print = len(sortedGameNames)
        if print_subset_of_top_games:
            num_games_to_print = min(num_top_games_to_print, num_games_to_print)

        for appid_reference in reference_dict.keys():
            rankGameUsedAsReferenceForHiddenGem = reference_dict[appid_reference][0]
            boolReferenceGameShouldAppearInRanking = reference_dict[appid_reference][1]
            if (not boolReferenceGameShouldAppearInRanking) and bool(rankGameUsedAsReferenceForHiddenGem <= num_games_to_print):
                num_games_to_print += 1

        # Check
        num_games_to_print = min(len(sortedGameNames), num_games_to_print)

        rank_decrease = 0

        for i in range(num_games_to_print):
            game_name = sortedGameNames[i]
            appid = [k for k, v in D.items() if v[0] == game_name][0]
            store_url = base_steam_store_url + appid

            width = 40
            store_url_fixed_width = f'{store_url: <{width}}'

            current_rank = i + 1

            if appid in reference_dict.keys():
                rankGameUsedAsReferenceForHiddenGem = reference_dict[appid][0]
                boolReferenceGameShouldAppearInRanking = reference_dict[appid][1]
                if (not boolReferenceGameShouldAppearInRanking):
                    assert( current_rank == rankGameUsedAsReferenceForHiddenGem )
                    rank_decrease += 1
                    continue

            current_rank -= rank_decrease

            # Append the ranking to the output text file
            with open(output_filename, 'a', encoding="utf8") as outfile:
                print('{:05}'.format(current_rank) + ".\t[" + game_name + "](" + store_url_fixed_width + ")", file=outfile)

    ranks_of_reference_hidden_gems = [v[0] for k, v in reference_dict.items()]
    summarizing_function = lambda x : np.average(x)
    scalar_summarizing_ranks_of_reference_hidden_gems = summarizing_function(ranks_of_reference_hidden_gems)

    if verbose:
        print('Objective function to minimize:\t', scalar_summarizing_ranks_of_reference_hidden_gems)

    return scalar_summarizing_ranks_of_reference_hidden_gems

# Bounds for the optimization procedure of the parameter alpha
lower_search_bound = 1  # minimal possible value of alpha is 1 people
upper_search_bound = pow(10, 8)  # maximal possible value of alpha is 8 billion people

functionToMinimize = lambda x : rankGames([x], False, appid_default_reference_set)
my_bounds = [(lower_search_bound, upper_search_bound)]

if use_alternative_scoring_method:
    functionToMinimize = lambda x_list: rankGames(x_list, False, appid_default_reference_set)
    my_bounds = [(lower_search_bound, upper_search_bound), (2, 10), (50, 200), (2, 10)]

res = differential_evolution(functionToMinimize, bounds=my_bounds)

if len(res.x) == 1:
    optimal_parameters = [ res.x ]
else:
    optimal_parameters = res.x
    print(optimal_parameters)

# Quick print in order to check that the upper search bound is not too close to our optimal alpha
# Otherwise, it could indicate the search has been biased by a poor choice of the upper search bound.
alphaOptim = optimal_parameters[0]
print("alpha = 10^%.2f" % log10(alphaOptim))

with open(output_filename, 'w', encoding="utf8") as outfile:
    rankGames(optimal_parameters, True, appid_default_reference_set)
