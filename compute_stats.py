# Objective: compute a score for each Steam game and then rank all the games while favoring hidden gems.

from appids import appidContradiction

def computeScoreGeneric(tuple, parameter_list, language = None):
    # Objective: compute a score for one Steam game.
    #
    # Input:    - a tuple is a list consisting of all retrieved information regarding one game
    #           - parameter_list is a list of parameters to calibrate the ranking.
    #             Currently, there is only one parameter, alpha, which could be chosen up to one's tastes, or optimized.
    #           - optional language to allow to compute regional rankings of hidden gems. cf. steam-reviews repository
    # Output:   game score

    alpha = parameter_list[0]

    if language is None:

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

    else:

        wilson_score = tuple[language]['wilson_score']
        num_players = tuple[language]['num_players']
        num_reviews = tuple[language]['num_reviews']

    quality_measure = wilson_score
    popularity_measure = num_players

    # Decreasing function
    decreasing_fun = lambda x: alpha / (alpha + x)

    score = quality_measure * decreasing_fun(popularity_measure)

    return score

def rankGames(D, parameter_list, verbose = False, appid_reference_set = {appidContradiction},
              language = None,
              num_top_games_to_print = 1000, filtered_appIDs_to_show = set(), filtered_appIDs_to_hide = set()):
    # Objective: rank all the Steam games, given a parameter alpha.
    #
    # Input:    - local dictionary of data extracted from SteamSpy
    #           - parameter_list is a list of parameters to calibrate the ranking.
    #           - optional verbosity boolean
    #           - optional set of appID of games chosen as references of a "hidden gem". By default, only "Contradiction".
    #           - optional language to allow to compute regional rankings of hidden gems. cf. steam-reviews repository
    #           - optional number of top games to print if the ranking is only partially displayed
    #             By default, only the top 1000 games are displayed.
    #             If set to None, the ranking will be fully displayed.
    #           - optional set of appID of games to show (and only these games are shown).
    #             Typically used to focus on appIDs for specific genres or tags.
    #             If set to None, the behavior is unintuitive yet exceptional: every game is shown, there is no filtering-in of appIDs.
    #           - optional set of appID of games to hide.
    #             Typically used to exclude appIDs for specific genres or tags.
    #             If set to None, the behavior is intuitive: no game is specifically hidden, there is no filtering-out of appIDs.
    # Output:   a 2-tuple consisting of:
    #           - a scalar value summarizing ranks of games used as references of "hidden gems"
    #           - the ranking to be ultimately displayed. A list of 3-tuple: (rank, game_name, appid).
    #             If verbose was set to None, the returned ranking is empty.

    import numpy as np

    # Boolean to decide whether printing the ranking of the top 1000 games, rather than the ranking of the whole Steam
    # catalog. It makes the script finish faster, and usually, we are only interested in the top games anyway.
    print_subset_of_top_games = bool( not(num_top_games_to_print is None) )

    # Boolean to decide whether there is a filtering-in of appIDs (typically to filter-in genres or tags).
    print_filtered_appIDs_only = bool( not(filtered_appIDs_to_show is None) and not(len(filtered_appIDs_to_show)==0) )

    # Boolean to decide whether there is a filtering-out of appIDs (typically to filter-out genres or tags).
    hide_filtered_appIDs_only = bool( not(filtered_appIDs_to_hide is None) and not(len(filtered_appIDs_to_hide)==0) )

    computeScore = lambda x: computeScoreGeneric(x, parameter_list, language)

    # Rank all the Steam games
    sortedValues = sorted(D.values(), key=computeScore, reverse=True)

    if language is None:
        name_index = 0
    else:
        name_index = 'name'

    sortedGameNames = list(map(lambda x: x[name_index], sortedValues))

    reference_dict = {}
    for appid_reference in appid_reference_set:
        try:
            # Find the rank of this game used as a reference of a "hidden gem"
            nameGameUsedAsReferenceForHiddenGem = D[appid_reference][name_index]
            rankGameUsedAsReferenceForHiddenGem = sortedGameNames.index(nameGameUsedAsReferenceForHiddenGem) + 1

            # Find whether the reference game should appear in the ranking (it might not due to tag filters)
            if language is None:
                boolReferenceGameShouldAppearInRanking = D[appid_reference][-1]
            else:
                boolReferenceGameShouldAppearInRanking = True

            reference_dict[appid_reference] = [rankGameUsedAsReferenceForHiddenGem, boolReferenceGameShouldAppearInRanking]
        except KeyError:
            continue

    ranks_of_reference_hidden_gems = [v[0] for k, v in reference_dict.items()]
    summarizing_function = lambda x : np.average(x)
    scalar_summarizing_ranks_of_reference_hidden_gems = summarizing_function(ranks_of_reference_hidden_gems)

    # Save the ranking for later display
    ranking_list = []
    if verbose:
        print('Objective function to minimize:\t', scalar_summarizing_ranks_of_reference_hidden_gems)

        # Populate the variable ranking_list
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
            appid = [k for k, v in D.items() if v[name_index] == game_name][0]

            current_rank = i + 1

            if appid in reference_dict.keys():
                rankGameUsedAsReferenceForHiddenGem = reference_dict[appid][0]
                boolReferenceGameShouldAppearInRanking = reference_dict[appid][1]
                if (not boolReferenceGameShouldAppearInRanking):
                    assert( current_rank == rankGameUsedAsReferenceForHiddenGem )
                    rank_decrease += 1
                    continue

            current_rank -= rank_decrease

            if not(print_filtered_appIDs_only) or bool(appid in filtered_appIDs_to_show):
                if not(hide_filtered_appIDs_only) or bool(not(appid in filtered_appIDs_to_hide)):
                    # Append the ranking info
                    ranking_list.append([current_rank, game_name, appid])

    return (scalar_summarizing_ranks_of_reference_hidden_gems, ranking_list)

def optimizeForAlpha(D, verbose = True, appid_reference_set = {appidContradiction},
                        language = None,
                        lower_search_bound = 1, # minimal possible value of alpha is 1 people
                        upper_search_bound = pow(10, 8) # maximal possible value of alpha is 8 billion people
                     ):
    # Objective: find the optimal value of the parameter alpha
    #
    # Input:    - local dictionary of data extracted from SteamSpy
    #           - optional verbosity boolean
    #           - optional set of appID of games chosen as references of a "hidden gem". By default, only "Contradiction".
    #           - optional language to allow to compute regional rankings of hidden gems. cf. steam-reviews repository
    #           - optional lower bound for the optimization procedure of the parameter alpha
    #           - optional upper bound for the optimization procedure of the parameter alpha
    # Output:   list of optimal parameters (by default, only one parameter is optimized: alpha)

    from math import log10
    from scipy.optimize import differential_evolution

    # Goal: find the optimal value for alpha by minimizing the rank of games chosen as references of "hidden gems"
    functionToMinimize = lambda x: rankGames(D, [x], False, appid_reference_set, language)[0]

    # Bounds for the optimization procedure of the parameter alpha
    my_bounds = [(lower_search_bound, upper_search_bound)]

    res = differential_evolution(functionToMinimize, bounds=my_bounds)

    if len(res.x) == 1:
        optimal_parameters = [res.x]
    else:
        optimal_parameters = res.x
        if verbose:
            print(optimal_parameters)

    if verbose:
        # Quick print in order to check that the upper search bound is not too close to our optimal alpha
        # Otherwise, it could indicate the search has been biased by a poor choice of the upper search bound.
        alphaOptim = optimal_parameters[0]
        print("alpha = 10^%.2f" % log10(alphaOptim))

    return optimal_parameters

def saveRankingToFile(output_filename, ranking_list, only_show_appid = False, width = 40):
    # Save the ranking to the output text file

    base_steam_store_url = "http://store.steampowered.com/app/"

    with open(output_filename, 'w', encoding="utf8") as outfile:
        for current_ranking_info in ranking_list:
            current_rank = current_ranking_info[0]
            game_name = current_ranking_info[1]
            appid = current_ranking_info[-1]

            store_url = base_steam_store_url + appid
            store_url_fixed_width = f'{store_url: <{width}}'

            if only_show_appid:
                print(appid, file=outfile)
            else:
                print('{:05}'.format(current_rank) + ".\t[" + game_name + "](" + store_url_fixed_width + ")", file=outfile)


def computeRanking(D, num_top_games_to_print=None, keywords_to_include=list(), keywords_to_exclude=list(),
                   language = None,
                   perform_optimization_at_runtime = True):
    # Objective: compute a ranking of hidden gems
    #
    # Input:    - local dictionary of data extracted from SteamSpy
    #           - maximal length of the ranking
    #               The higher the value, the longer it takes to compute and print the ranking.
    #               If set to None, there is no limit, so the whole Steam catalog is ranked.
    #           - tags to filter-in
    #               Warning because unintuitive: to avoid filtering-in, please use an empty list.
    #           - tags to filter-out
    #           - optional language to allow to compute regional rankings of hidden gems. cf. steam-reviews repository
    #           - bool to decide whether to optimize alpha at run-time, or to rely on a hard-coded value instead
    #
    # Output:   ranking of hidden gems

    from appids import appid_hidden_gems_reference_set
    from download_json import getAppidByKeywordListToInclude, getAppidByKeywordListToExclude

    if perform_optimization_at_runtime:
        optimal_parameters = optimizeForAlpha(D, True, appid_hidden_gems_reference_set, language)
    else:
        # Optimal parameter as computed on December 18, 2018
        optimal_parameters = [ pow(10, 6.46) ]

    # Filter-in games which meta-data includes ALL the following keywords
    # Caveat: the more keywords, the fewer games are filtered-in! cf. intersection of sets in the code
    filtered_in_appIDs = getAppidByKeywordListToInclude(keywords_to_include)

    # Filter-out games which meta-data includes ANY of the following keywords
    # NB: the more keywords, the more games are excluded. cf. union of sets in the code
    filtered_out_appIDs = getAppidByKeywordListToExclude(keywords_to_exclude)

    (objective_function, ranking) = rankGames(D, optimal_parameters, True, appid_hidden_gems_reference_set, language,
                                              num_top_games_to_print, filtered_in_appIDs, filtered_out_appIDs)

    return ranking

if __name__ == "__main__":
    # A local dictionary was stored in the following text file
    input_filename = "dict_top_rated_games_on_steam.txt"

    # A ranking, in a format parsable by Github Gist, will be stored in the following text file
    output_filename = "hidden_gems.md"

    # A ranking, as a list of appids, will be stored in the following text file
    output_filename_only_appids = "idlist.txt"

    # Import the local dictionary from the input file
    with open(input_filename, 'r', encoding="utf8") as infile:
        lines = infile.readlines()
        # The dictionary is on the second line
        D = eval(lines[1])

    # Maximal length of the ranking. The higher the value, the longer it takes to compute and print the ranking.
    # If set to None, there is no limit, so the whole Steam catalog is ranked.
    num_top_games_to_print = 1000

    # Filtering-in
    # Warning because unintuitive: to avoid filtering-in, please use an empty list!
    keywords_to_include = []  # ["Rogue-Like"]

    # Filtering-out
    keywords_to_exclude = [] # ["Visual Novel", "Anime"]

    ranking = computeRanking(D, num_top_games_to_print, keywords_to_include, keywords_to_exclude)

    only_show_appid = False
    saveRankingToFile(output_filename, ranking, only_show_appid)

    only_show_appid = True
    saveRankingToFile(output_filename_only_appids, ranking, only_show_appid)
