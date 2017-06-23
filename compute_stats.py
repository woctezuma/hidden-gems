from scipy.optimize import differential_evolution
from math import log10

#filename = "thousand_dict_top_rated_games_on_steam.txt"
filename = "dict_top_rated_games_on_steam.txt"

base_steam_store_url = "http://store.steampowered.com/app/"

with open(filename, 'r', encoding="utf8") as infile:
    lines = infile.readlines()
    # The dictionary is on the second line
    D = eval(lines[1])

def computeScoreGeneric(tuple, alpha):
    # A tuple is a list consisting of: [game_name wilson_score all_time_peak num_owners num_players]
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
    #popularity_measure = median_playtime

    # Decreasing function
    decreasing_fun = lambda x: alpha / (alpha + x)

    score = quality_measure * decreasing_fun(popularity_measure)

    return score

# Goal: find the optimal values for alpha by maximizing the rank of the game "Contradiction"

def functionToMinimize(alpha, verbose=False):
    computeScore = lambda x: computeScoreGeneric(x, alpha)

    sortedValues = sorted(D.values(), key=computeScore, reverse=True)

    sortedGameNames = list(map(lambda x: x[0], sortedValues))
    sortedOriginalGameScores = list(map(lambda x: x[1], sortedValues))
    sortedComputedGameScores = list(map(lambda x: computeScore(x), sortedValues))

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
    if verbose:
        print("Contradiction rank:\t" + str(rankContradiction) + "\n")

    return rankContradiction

# Example of usage
alphaExample = pow(10, 6.45)
#functionToMinimize(alphaExample, True)

# Optimization
res = differential_evolution(functionToMinimize, bounds=[(1, pow(10, 10))])
alphaOptim = res.x
print( log10(alphaOptim) )

functionToMinimize(alphaOptim, True)
