# Objective: compute a score for each Steam game and then rank all the games while favoring hidden gems.

import json
from dataclasses import asdict
from pathlib import Path
from typing import Literal

import numpy as np
from scipy.optimize import minimize

from src.appids import APP_ID_CONTRADICTION, appid_hidden_gems_reference_set
from src.download_json import (
    get_appid_by_keyword_list_to_exclude,
    get_appid_by_keyword_list_to_include,
)
from src.game import Game

QualityMeasure = Literal["wilson_score", "bayesian_rating"]
PopularityMeasure = Literal["num_owners", "num_reviews"]


def compute_game_score(
    game: Game | dict,
    alpha: float,
    language: str | None = None,
    popularity_measure_str: PopularityMeasure = "num_owners",
    quality_measure_str: QualityMeasure = "wilson_score",
) -> float:
    # Objective: compute a score for one Steam game.
    #
    # Input:    - a my_tuple is a list consisting of all retrieved information regarding one game
    #           - parameter_list is a list of parameters to calibrate the ranking.
    #             Currently, there is only one parameter, alpha, which could be chosen up to one's tastes, or optimized.
    #           - optional language to allow to compute regional rankings of hidden gems
    #           - optional choice of popularity measure: either 'num_owners', or 'num_reviews'
    #           - optional choice of quality measure: either 'wilson_score' or 'bayesian_rating'
    # Output:   game score
    if language is None:
        quality_measure = getattr(game, quality_measure_str)
        if popularity_measure_str == "num_reviews":
            popularity_measure = game.num_positive_reviews + game.num_negative_reviews
        else:
            popularity_measure = game.num_owners
    else:
        quality_measure = game[language][quality_measure_str]
        popularity_measure = game[language][popularity_measure_str]

    return quality_measure * decreasing_fun(popularity_measure, alpha)


def decreasing_fun(x, alpha):
    # Decreasing function
    return alpha / (alpha + x)


def rank_games(
    games: dict[str, Game | dict],
    alpha: float,
    appid_reference_set: set[str] | None = None,
    language: str | None = None,
    popularity_measure_str: PopularityMeasure = "num_owners",
    quality_measure_str: QualityMeasure = "wilson_score",
    num_top_games_to_print: int = 1000,
    filtered_app_ids_to_show: set[str] | None = None,
    filtered_app_ids_to_hide: set[str] | None = None,
    *,
    verbose: bool = False,
) -> tuple[float, list[list[int | str]]]:
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
        appid_reference_set = {APP_ID_CONTRADICTION}
    if filtered_app_ids_to_show is None:
        filtered_app_ids_to_show = set()
    if filtered_app_ids_to_hide is None:
        filtered_app_ids_to_hide = set()

    # Rank all the Steam games
    sorted_games = sorted(
        games.values(),
        key=lambda g: compute_game_score(
            g,
            alpha,
            language,
            popularity_measure_str,
            quality_measure_str,
        ),
        reverse=True,
    )

    if language is None:
        sorted_game_ids = [g.appid for g in sorted_games]
        # Find the rank of this game used as a reference of a "hidden gem"
        reference_ranks = {
            appid: sorted_game_ids.index(appid) + 1
            for appid in appid_reference_set
            if appid in games
        }
    else:
        sorted_game_ids = [g["appid"] for g in sorted_games]

        reference_ranks = {
            appid: sorted_game_ids.index(appid) + 1
            for appid in appid_reference_set
            if appid in games
        }

    objective_value = (
        np.average(list(reference_ranks.values())) if reference_ranks else float("nan")
    )

    if not verbose:
        return objective_value, []

    print(f"Objective function to minimize:\t{objective_value}")

    # Save the ranking for later display
    ranking_list = []
    rank = 1
    for game in sorted_games:
        appid = game.appid if language is None else game["appid"]
        if (
            (not filtered_app_ids_to_show or appid in filtered_app_ids_to_show)
            and (not filtered_app_ids_to_hide or appid not in filtered_app_ids_to_hide)
            and (language is not None or game.should_appear_in_ranking)
        ):
            game_name = game.name if language is None else game["name"]
            # Append the ranking info
            ranking_list.append([rank, game_name, appid])
            rank += 1

    return objective_value, ranking_list[:num_top_games_to_print]


def optimize_for_alpha(
    games: dict[str, Game | dict],
    appid_reference_set: set[str] | None = None,
    language: str | None = None,
    popularity_measure_str: PopularityMeasure = "num_owners",
    quality_measure_str: QualityMeasure = "wilson_score",
    *,
    verbose: bool = True,
) -> list[float]:
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
        appid_reference_set = {APP_ID_CONTRADICTION}

    # Goal: find the optimal value for alpha by minimizing the rank of games chosen as references of "hidden gems"
    def function_to_minimize(x):
        return rank_games(
            games,
            x[0],
            appid_reference_set,
            language,
            popularity_measure_str,
            quality_measure_str,
            verbose=False,
        )[0]

    if language is None:
        if popularity_measure_str == "num_reviews":
            vec = [
                g.num_positive_reviews + g.num_negative_reviews for g in games.values()
            ]
        else:
            vec = [g.num_owners for g in games.values()]
    else:
        vec = [g[language][popularity_measure_str] for g in games.values()]

    x0 = 1 + np.max(vec)
    res = minimize(fun=function_to_minimize, x0=[x0], method="Nelder-Mead")
    optimal_alpha = res.x[0]

    if verbose:
        try:
            optimal_power = np.log10(optimal_alpha)
            print(f"alpha = 10^{optimal_power:.2f}")
        except (ValueError, RuntimeWarning):
            print(f"alpha = {optimal_alpha:.2f}")

    return [optimal_alpha]


def save_ranking_to_file(
    output_filename: str | Path,
    ranking_list: list[list[int | str]],
    width: int = 40,
    *,
    only_show_appid: bool = False,
    verbose: bool = False,
) -> None:
    # Objective: save the ranking to the output text file
    base_steam_store_url = "https://store.steampowered.com/app/"
    with Path(output_filename).open("w", encoding="utf8") as outfile:
        for rank, game_name, appid in ranking_list:
            if only_show_appid:
                line = str(appid)
            else:
                store_url = f"{base_steam_store_url}{appid}"
                line = f"{rank:05}.\t[{game_name}]({store_url: <{width}})"
            print(line, file=outfile)
            if verbose:
                print(line)


def compute_ranking(
    games: dict[str, Game | dict],
    num_top_games_to_print: int | None = None,
    keywords_to_include: list[str] | None = None,
    keywords_to_exclude: list[str] | None = None,
    language: str | None = None,
    popularity_measure_str: PopularityMeasure = "num_owners",
    quality_measure_str: QualityMeasure = "wilson_score",
    *,
    perform_optimization_at_runtime: bool = True,
) -> list[list[int | str]]:
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
        keywords_to_include = []
    if keywords_to_exclude is None:
        keywords_to_exclude = []

    if perform_optimization_at_runtime:
        optimal_parameters = optimize_for_alpha(
            games,
            appid_hidden_gems_reference_set,
            language,
            popularity_measure_str,
            quality_measure_str,
            verbose=True,
        )
    # Hardcoded values from the original script
    elif popularity_measure_str == "num_owners":
        if quality_measure_str == "wilson_score":
            # Optimal parameter as computed on May 19, 2018
            # Objective function to minimize:	 2156.36
            optimal_parameters = [10**6.52]
        else:
            # Optimal parameter as computed on May 19, 2018
            # Objective function to minimize:	 1900.00
            optimal_parameters = [10**6.63]
    elif quality_measure_str == "wilson_score":
        # Optimal parameter as computed on May 19, 2018
        # Objective function to minimize:	 2372.90
        optimal_parameters = [10**4.83]
    else:
        # Optimal parameter as computed on May 19, 2018
        # Objective function to minimize:	 2094.00
        optimal_parameters = [10**4.89]
    # Filter-in games which meta-data includes ALL the following keywords
    # Caveat: the more keywords, the fewer games are filtered-in! cf. intersection of sets in the code
    filtered_in_app_ids = get_appid_by_keyword_list_to_include(keywords_to_include)
    # Filter-out games which meta-data includes ANY of the following keywords
    # NB: the more keywords, the more games are excluded. cf. union of sets in the code
    filtered_out_app_ids = get_appid_by_keyword_list_to_exclude(keywords_to_exclude)

    _, ranking = rank_games(
        games,
        optimal_parameters[0],
        appid_hidden_gems_reference_set,
        language,
        popularity_measure_str,
        quality_measure_str,
        num_top_games_to_print,
        filtered_in_app_ids,
        filtered_out_app_ids,
        verbose=True,
    )

    return ranking


def load_games_from_json(input_filename: str | Path) -> dict[str, Game]:
    with Path(input_filename).open(encoding="utf8") as f:
        data = json.load(f)
    return {appid: Game(**game_data) for appid, game_data in data.items()}


def save_games_to_json(games: dict[str, Game], output_filename: str | Path) -> None:
    with Path(output_filename).open("w", encoding="utf8") as f:
        json.dump({appid: asdict(game) for appid, game in games.items()}, f, indent=4)


def run_workflow(
    quality_measure_str: QualityMeasure = "wilson_score",
    popularity_measure_str: PopularityMeasure = "num_reviews",
    *,
    perform_optimization_at_runtime: bool = True,
    num_top_games_to_print: int = 250,
    verbose: bool = False,
    language: str | None = None,
    keywords_to_include: list[str] | None = None,
    keywords_to_exclude: list[str] | None = None,
) -> bool:
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
        keywords_to_include = []
    if keywords_to_exclude is None:
        keywords_to_exclude = []

    # A local dictionary was stored in the following json file
    input_filename = "dict_top_rated_games_on_steam.json"
    # A ranking, in a format parsable by Github Gist, will be stored in the following text file
    output_filename = "hidden_gems.md"
    # A ranking, as a list of appids, will be stored in the following text file
    output_filename_only_appids = "idlist.txt"

    games = load_games_from_json(input_filename)

    ranking = compute_ranking(
        games,
        num_top_games_to_print,
        keywords_to_include,
        keywords_to_exclude,
        language,
        popularity_measure_str,
        quality_measure_str,
        perform_optimization_at_runtime=perform_optimization_at_runtime,
    )

    save_ranking_to_file(
        output_filename,
        ranking,
        only_show_appid=False,
        verbose=verbose,
    )
    save_ranking_to_file(
        output_filename_only_appids,
        ranking,
        only_show_appid=True,
        verbose=verbose,
    )

    return True


def main() -> bool:
    run_workflow(
        quality_measure_str="wilson_score",
        popularity_measure_str="num_reviews",
        perform_optimization_at_runtime=True,
        num_top_games_to_print=1000,
        verbose=False,
        language=None,
        keywords_to_include=None,
        keywords_to_exclude=None,
    )
    return True


if __name__ == "__main__":
    main()
