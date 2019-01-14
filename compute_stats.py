# Objective: compute a score for each Steam game and then rank all the games while favoring hidden gems.

import ast

import numpy as np

from appids import appidContradiction


def compute_score_generic(my_tuple, parameter_list, language=None,
                          popularity_measure_str=None, quality_measure_str=None):
    # Objective: compute a score for one Steam game.
    #
    # Input:    - a my_tuple is a list consisting of all retrieved information regarding one game
    #           - parameter_list is a list of parameters to calibrate the ranking.
    #             Currently, there is only one parameter, alpha, which could be chosen up to one's tastes, or optimized.
    #           - optional language to allow to compute regional rankings of hidden gems
    #           - optional choice of popularity measure: either 'num_owners', or 'num_reviews'
    #           - optional choice of quality measure: either 'wilson_score' or 'bayesian_rating'
    # Output:   game score

    alpha = parameter_list[0]

    if language is None:

        # noinspection PyUnusedLocal
        # game_name = my_tuple[0]
        wilson_score = my_tuple[1]
        bayesian_rating = my_tuple[2]
        num_owners = my_tuple[3]
        num_players = my_tuple[4]
        median_playtime = my_tuple[5]
        average_playtime = my_tuple[6]
        num_positive_reviews = my_tuple[7]
        num_negative_reviews = my_tuple[8]

        # noinspection PyUnusedLocal
        # bool_game_should_appear_in_ranking = my_tuple[-1]

        num_owners = float(num_owners)
        try:
            # noinspection PyUnusedLocal
            num_players = float(num_players)
        except TypeError:
            # noinspection PyUnusedLocal
            num_players = None
        # noinspection PyUnusedLocal
        median_playtime = float(median_playtime)
        # noinspection PyUnusedLocal
        average_playtime = float(average_playtime)
        num_positive_reviews = float(num_positive_reviews)
        num_negative_reviews = float(num_negative_reviews)

        num_reviews = num_positive_reviews + num_negative_reviews

    else:

        wilson_score = my_tuple[language]['wilson_score']
        bayesian_rating = my_tuple[language]['bayesian_rating']
        num_owners = my_tuple[language]['num_owners']
        num_reviews = my_tuple[language]['num_reviews']

    if quality_measure_str is None or quality_measure_str == 'wilson_score':
        quality_measure = wilson_score
    else:
        quality_measure = bayesian_rating

    if popularity_measure_str is None or popularity_measure_str == 'num_owners':
        popularity_measure = num_owners
    else:
        popularity_measure = num_reviews

    def decreasing_fun(x):
        # Decreasing function
        return alpha / (alpha + x)

    score = quality_measure * decreasing_fun(popularity_measure)

    return score


# noinspection PyPep8Naming
def rank_games(D, parameter_list, verbose=False, appid_reference_set=None,
               language=None,
               popularity_measure_str=None,
               quality_measure_str=None,
               num_top_games_to_print=1000, filtered_app_ids_to_show=None, filtered_app_ids_to_hide=None):
    # Objective: rank all the Steam games, given a parameter alpha.
    #
    # Input:    - local dictionary of data extracted from SteamSpy
    #           - parameter_list is a list of parameters to calibrate the ranking.
    #           - optional verbosity boolean
    #           - optional set of appID of games chosen as references of hidden gems. By default, only "Contradiction".
    #           - optional language to allow to compute regional rankings of hidden gems. cf. compute_regional_stats.py
    #           - optional choice of popularity measure: either 'num_owners', or 'num_reviews'
    #           - optional choice of quality measure: either 'wilson_score' or 'bayesian_rating'
    #           - optional number of top games to print if the ranking is only partially displayed
    #             By default, only the top 1000 games are displayed.
    #             If set to None, the ranking will be fully displayed.
    #           - optional set of appID of games to show (and only these games are shown).
    #             Typically used to focus on appIDs for specific genres or tags.
    #             If None, behavior is unintuitive yet exceptional: every game is shown, appIDs are not filtered-in.
    #           - optional set of appID of games to hide.
    #             Typically used to exclude appIDs for specific genres or tags.
    #             If None, the behavior is intuitive: no game is specifically hidden, appIDs are not filtered-out.
    # Output:   a 2-tuple consisting of:
    #           - a scalar value summarizing ranks of games used as references of "hidden gems"
    #           - the ranking to be ultimately displayed. A list of 3-tuple: (rank, game_name, appid).
    #             If verbose was set to None, the returned ranking is empty.

    if appid_reference_set is None:
        appid_reference_set = {appidContradiction}

    if filtered_app_ids_to_show is None:
        filtered_app_ids_to_show = set()

    if filtered_app_ids_to_hide is None:
        filtered_app_ids_to_hide = set()

    # Boolean to decide whether printing the ranking of the top 1000 games, rather than the ranking of the whole Steam
    # catalog. It makes the script finish faster, and usually, we are only interested in the top games anyway.
    print_subset_of_top_games = bool(not (num_top_games_to_print is None))

    # Boolean to decide whether there is a filtering-in of appIDs (typically to filter-in genres or tags).
    print_filtered_app_ids_only = bool(not (filtered_app_ids_to_show is None)
                                       and not (len(filtered_app_ids_to_show) == 0))

    # Boolean to decide whether there is a filtering-out of appIDs (typically to filter-out genres or tags).
    hide_filtered_app_ids_only = bool(not (filtered_app_ids_to_hide is None)
                                      and not (len(filtered_app_ids_to_hide) == 0))

    def compute_score(x):
        return compute_score_generic(x, parameter_list, language, popularity_measure_str, quality_measure_str)

    # Rank all the Steam games
    sorted_values = sorted(D.values(), key=compute_score, reverse=True)

    if language is None:
        name_index = 0
    else:
        name_index = 'name'

    sorted_game_names = list(map(lambda x: x[name_index], sorted_values))

    reference_dict = {}
    for appid_reference in appid_reference_set:

        # Find the rank of this game used as a reference of a "hidden gem"
        name_game_ref_for_hidden_gem = D[appid_reference][name_index]
        rank_game_used_as_reference_for_hidden_gem = sorted_game_names.index(name_game_ref_for_hidden_gem) + 1

        # Find whether the reference game should appear in the ranking (it might not due to tag filters)
        if language is None:
            bool_reference_game_should_appear_in_ranking = D[appid_reference][-1]
        else:
            bool_reference_game_should_appear_in_ranking = True

        reference_dict[appid_reference] = [rank_game_used_as_reference_for_hidden_gem,
                                           bool_reference_game_should_appear_in_ranking]

    ranks_of_reference_hidden_gems = [v[0] for k, v in reference_dict.items()]

    def summarizing_function(x):
        return np.average(x)

    scalar_summarizing_ranks_of_reference_hidden_gems = summarizing_function(ranks_of_reference_hidden_gems)

    # Save the ranking for later display
    ranking_list = []
    if verbose:
        print('Objective function to minimize:\t', scalar_summarizing_ranks_of_reference_hidden_gems)

        # Populate the variable ranking_list
        num_games_to_print = len(sorted_game_names)
        if print_subset_of_top_games:
            num_games_to_print = min(num_top_games_to_print, num_games_to_print)

        for appid_reference in reference_dict.keys():
            rank_game_used_as_reference_for_hidden_gem = reference_dict[appid_reference][0]
            bool_reference_game_should_appear_in_ranking = reference_dict[appid_reference][1]
            if (not bool_reference_game_should_appear_in_ranking) and bool(
                    rank_game_used_as_reference_for_hidden_gem <= num_games_to_print):
                num_games_to_print += 1

        # Check
        num_games_to_print = min(len(sorted_game_names), num_games_to_print)

        rank_decrease = 0

        for i in range(num_games_to_print):
            game_name = sorted_game_names[i]
            appid = [k for k, v in D.items() if v[name_index] == game_name][0]

            current_rank = i + 1

            if appid in reference_dict.keys():
                rank_game_used_as_reference_for_hidden_gem = reference_dict[appid][0]
                bool_reference_game_should_appear_in_ranking = reference_dict[appid][1]
                if not bool_reference_game_should_appear_in_ranking:
                    assert (current_rank == rank_game_used_as_reference_for_hidden_gem)
                    rank_decrease += 1
                    continue

            current_rank -= rank_decrease

            if not print_filtered_app_ids_only or bool(appid in filtered_app_ids_to_show):
                if not hide_filtered_app_ids_only or bool(not (appid in filtered_app_ids_to_hide)):
                    # Append the ranking info
                    ranking_list.append([current_rank, game_name, appid])

    return scalar_summarizing_ranks_of_reference_hidden_gems, ranking_list


# noinspection PyPep8Naming
def optimize_for_alpha(D, verbose=True, appid_reference_set=None,
                       language=None,
                       popularity_measure_str=None,
                       quality_measure_str=None
                       ):
    # Objective: find the optimal value of the parameter alpha
    #
    # Input:    - local dictionary of data extracted from SteamSpy
    #           - optional verbosity boolean
    #           - optional set of appID of games chosen as references of hidden gems. By default, only "Contradiction".
    #           - optional language to allow to compute regional rankings of hidden gems. cf. compute_regional_stats.py
    #           - optional choice of popularity measure: either 'num_owners', or 'num_reviews'
    #           - optional choice of quality measure: either 'wilson_score' or 'bayesian_rating'
    # Output:   list of optimal parameters (by default, only one parameter is optimized: alpha)

    if appid_reference_set is None:
        appid_reference_set = {appidContradiction}

    from math import log10
    from scipy.optimize import minimize

    # Goal: find the optimal value for alpha by minimizing the rank of games chosen as references of "hidden gems"
    def function_to_minimize(x):
        return rank_games(D, [x], False, appid_reference_set, language, popularity_measure_str, quality_measure_str)[0]

    if language is None:
        if popularity_measure_str is None or popularity_measure_str == 'num_owners':
            vec = [float(game[get_index_num_owners()]) for game in D.values()]
        else:
            assert (popularity_measure_str == 'num_reviews')
            vec = [get_num_reviews(game) for game in D.values()]

    else:
        vec = [game[language][popularity_measure_str] for game in D.values()]

    def choose_x0(data_vec):
        x0 = 1 + np.max(data_vec)
        return x0

    res = minimize(fun=function_to_minimize, x0=choose_x0(vec), method='Nelder-Mead')

    optimal_parameters = [res.x]

    try:
        optimal_power = log10(optimal_parameters[0])
        if verbose:
            print("alpha = 10^%.2f" % optimal_power)
    except ValueError:
        if verbose:
            print("alpha = %.2f" % optimal_parameters[0])

    return optimal_parameters


def save_ranking_to_file(output_filename, ranking_list, only_show_appid=False, verbose=False, width=40):
    # Objective: save the ranking to the output text file

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
                if verbose:
                    print(appid)
            else:
                sentence = '{:05}'.format(current_rank) + ".\t[" + game_name + "](" + store_url_fixed_width + ")"
                print(sentence, file=outfile)
                if verbose:
                    print(sentence)


def get_index_num_owners():
    return 3


def get_index_num_positive_reviews():
    return 7


def get_index_num_negative_reviews():
    return 8


def get_num_reviews(game):
    return int(game[get_index_num_positive_reviews()]) + int(game[get_index_num_negative_reviews()])


# noinspection PyPep8Naming
def compute_ranking(D, num_top_games_to_print=None, keywords_to_include=None, keywords_to_exclude=None,
                    language=None,
                    perform_optimization_at_runtime=True,
                    popularity_measure_str=None,
                    quality_measure_str=None):
    # Objective: compute a ranking of hidden gems
    #
    # Input:    - local dictionary of data extracted from SteamSpy
    #           - maximal length of the ranking
    #               The higher the value, the longer it takes to compute and print the ranking.
    #               If set to None, there is no limit, so the whole Steam catalog is ranked.
    #           - tags to filter-in
    #               Warning because unintuitive: to avoid filtering-in, please use an empty list.
    #           - tags to filter-out
    #           - optional language to allow to compute regional rankings of hidden gems. cf. compute_regional_stats.py
    #           - bool to decide whether to optimize alpha at run-time, or to rely on a hard-coded value instead
    #           - optional choice of popularity measure: either 'num_owners', or 'num_reviews'
    #           - optional choice of quality measure: either 'wilson_score' or 'bayesian_rating'
    #
    # Output:   ranking of hidden gems

    if keywords_to_include is None:
        keywords_to_include = list()

    if keywords_to_exclude is None:
        keywords_to_exclude = list()

    from appids import appid_hidden_gems_reference_set
    from download_json import get_appid_by_keyword_list_to_include, get_appid_by_keyword_list_to_exclude

    if perform_optimization_at_runtime:
        optimal_parameters = optimize_for_alpha(D, True, appid_hidden_gems_reference_set, language,
                                                popularity_measure_str, quality_measure_str)
    else:
        if popularity_measure_str is None or popularity_measure_str == 'num_owners':
            if quality_measure_str is None or quality_measure_str == 'wilson_score':
                # Optimal parameter as computed on May 19, 2018
                # Objective function to minimize:	 2156.36
                optimal_parameters = [pow(10, 6.52)]
            else:
                assert (quality_measure_str == 'bayesian_rating')
                # Optimal parameter as computed on May 19, 2018
                # Objective function to minimize:	 1900.00
                optimal_parameters = [pow(10, 6.63)]
        else:
            assert (popularity_measure_str == 'num_reviews')
            if quality_measure_str is None or quality_measure_str == 'wilson_score':
                # Optimal parameter as computed on May 19, 2018
                # Objective function to minimize:	 2372.90
                optimal_parameters = [pow(10, 4.83)]
            else:
                assert (quality_measure_str == 'bayesian_rating')
                # Optimal parameter as computed on May 19, 2018
                # Objective function to minimize:	 2094.00
                optimal_parameters = [pow(10, 4.89)]

    # Filter-in games which meta-data includes ALL the following keywords
    # Caveat: the more keywords, the fewer games are filtered-in! cf. intersection of sets in the code
    filtered_in_app_ids = get_appid_by_keyword_list_to_include(keywords_to_include)

    # Filter-out games which meta-data includes ANY of the following keywords
    # NB: the more keywords, the more games are excluded. cf. union of sets in the code
    filtered_out_app_ids = get_appid_by_keyword_list_to_exclude(keywords_to_exclude)

    (_, ranking) = rank_games(D, optimal_parameters, True, appid_hidden_gems_reference_set, language,
                              popularity_measure_str,
                              quality_measure_str,
                              num_top_games_to_print, filtered_in_app_ids, filtered_out_app_ids)

    return ranking


def run_workflow(quality_measure_str='wilson_score',
                 popularity_measure_str='num_reviews',
                 perform_optimization_at_runtime=True,
                 num_top_games_to_print=250,
                 verbose=False,
                 language=None,
                 keywords_to_include=None,
                 keywords_to_exclude=None):
    # Objective: save to disk a ranking of hidden gems.
    #
    # Input:
    #           - optional choice of quality measure: either 'wilson_score' or 'bayesian_rating'
    #           - optional choice of popularity measure: either 'num_owners', or 'num_reviews'
    #           - bool to decide whether to optimize alpha at run-time, or to rely on a hard-coded value instead
    #           - maximal length of the ranking
    #               The higher the value, the longer it takes to compute and print the ranking.
    #               If set to None, there is no limit, so the whole Steam catalog is ranked.
    #           - optional language to allow to compute regional rankings of hidden gems
    #           - tags to filter-in
    #               Warning because unintuitive: to avoid filtering-in, please use an empty list.
    #           - tags to filter-out
    #
    # Output:   ranking of hidden gems, printed to screen, and printed to file 'hidden_gems.md'

    if keywords_to_include is None:
        keywords_to_include = []  # ["Rogue-Like"]

    if keywords_to_exclude is None:
        keywords_to_exclude = []  # ["Visual Novel", "Anime"]

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
        # noinspection PyPep8Naming
        D = ast.literal_eval(lines[1])

    ranking = compute_ranking(D, num_top_games_to_print, keywords_to_include, keywords_to_exclude,
                              language, perform_optimization_at_runtime, popularity_measure_str, quality_measure_str)

    save_ranking_to_file(output_filename, ranking, only_show_appid=False, verbose=verbose)
    # NB: verbose is set to True, so that I can check the results even with Travis integration on Github.

    save_ranking_to_file(output_filename_only_appids, ranking, only_show_appid=True, verbose=verbose)

    return True


def main():
    run_workflow(quality_measure_str='wilson_score',  # Either 'wilson_score' or 'bayesian_rating'
                 popularity_measure_str='num_reviews',  # Either 'num_reviews' or 'num_owners'
                 perform_optimization_at_runtime=True,
                 num_top_games_to_print=1000,
                 verbose=False,
                 language=None,
                 keywords_to_include=None,
                 keywords_to_exclude=None)

    return True


if __name__ == "__main__":
    main()
