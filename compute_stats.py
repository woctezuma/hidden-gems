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

base_steam_store_url = "http://store.steampowered.com/app/"

use_playtime_as_popularity_measure = False

# Import the dictionary from the input file
with open(input_filename, 'r', encoding="utf8") as infile:
    lines = infile.readlines()
    # The dictionary is on the second line
    D = eval(lines[1])

def computeScoreGeneric(tuple, alpha):
    # Objective: compute a score for one Steam game.
    #
    # Input:    - a tuple is a list consisting of all retrieved information regarding one game
    #           - alpha is the only parameter of the ranking, and could be chosen up to one's tastes, or optimized
    # Output:   game score

    game_name = tuple[0]
    wilson_score = tuple[1]
    num_owners = tuple[2]
    num_players = tuple[3]
    median_playtime = tuple[4]
    average_playtime = tuple[5]

    num_owners = float(num_owners)
    num_players = float(num_players)
    median_playtime = float(median_playtime)
    average_playtime = float(average_playtime)

    quality_measure = wilson_score
    popularity_measure = num_players

    if use_playtime_as_popularity_measure:
        popularity_measure = average_playtime

    # Decreasing function
    decreasing_fun = lambda x: alpha / (alpha + x)

    score = quality_measure * decreasing_fun(popularity_measure)

    return score

# Goal: find the optimal values for alpha by maximizing the rank of the game "Contradiction"

def functionToMinimize(alpha, verbose=False):
    # Objective: rank all the Steam games, given a parameter alpha.
    #
    # Input:    - alpha is the only parameter of the ranking, and could be chosen up to one's tastes, or optimized
    #           - optional verbosity boolean
    # Output:   rank of the game called "Contradiction"

    computeScore = lambda x: computeScoreGeneric(x, alpha)

    # Rank all the Steam games
    sortedValues = sorted(D.values(), key=computeScore, reverse=True)

    sortedGameNames = list(map(lambda x: x[0], sortedValues))

    # Display the ranking in a format parsable by Github Gist
    if verbose:
        for i in range(len(sortedGameNames)):
            game_name = sortedGameNames[i]
            appid = [k for k, v in D.items() if v[0] == game_name][0]
            store_url = base_steam_store_url + appid

            width = 40
            store_url_fixed_width = f'{store_url: <{width}}'

            # Append the ranking to the output text file
            with open(output_filename, 'a', encoding="utf8") as outfile:
                print('{:05}'.format(i + 1) + ".\t[" + game_name + "](" + store_url_fixed_width + ")", file=outfile)

    # Find the rank of the game called Contradiction
    appidContradiction = "373390"
    nameContradiction = D[appidContradiction][0]
    rankContradiction = sortedGameNames.index(nameContradiction) + 1

    return rankContradiction

# Optimization procedure of the parameter alpha
upper_search_bound = pow(10, 10) # maximal possible value of alpha is 10 billion people

if use_playtime_as_popularity_measure:
    upper_search_bound = 1.5 * pow(10, 6) # maximal possible value of alpha is 25000 hours

res = differential_evolution(functionToMinimize, bounds=[(1, upper_search_bound)])
alphaOptim = res.x

# Quick print in order to check that the upper search bound is not too close to our optimal alpha
# Otherwise, it could indicate the search has been biased the search by a poor choice of the upper search bound.
print(alphaOptim / upper_search_bound)

functionToMinimize(alphaOptim, True)
