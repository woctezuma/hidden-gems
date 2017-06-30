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
    all_time_peak = tuple[2]
    num_owners = tuple[3]
    num_players = tuple[4]
    median_playtime = tuple[5]

    all_time_peak = float(all_time_peak)
    num_owners = float(num_owners)
    num_players = float(num_players)
    median_playtime = float(median_playtime)

    quality_measure = wilson_score
    popularity_measure = num_players

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

            print('{:05}'.format(i + 1) + ".\t[" + game_name + "](" + store_url_fixed_width + ")")

    # Find the rank of the game called Contradiction
    appidContradiction = "373390"
    nameContradiction = D[appidContradiction][0]
    rankContradiction = sortedGameNames.index(nameContradiction) + 1

    return rankContradiction

# Optimization procedure of the parameter alpha
res = differential_evolution(functionToMinimize, bounds=[(1, pow(10, 10))])
alphaOptim = res.x

functionToMinimize(alphaOptim, True)

# TODO save to output_filename
