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
    if language is None:
        quality_measure = getattr(game, quality_measure_str)
        if popularity_measure_str == "num_reviews":
            popularity_measure = game.num_positive_reviews + game.num_negative_reviews
        else:
            popularity_measure = game.num_owners
    else:
        quality_measure = game[language][quality_measure_str]
        popularity_measure = game[language][popularity_measure_str]

    return quality_measure * (alpha / (alpha + popularity_measure))


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
    if appid_reference_set is None:
        appid_reference_set = {APP_ID_CONTRADICTION}
    if filtered_app_ids_to_show is None:
        filtered_app_ids_to_show = set()
    if filtered_app_ids_to_hide is None:
        filtered_app_ids_to_hide = set()

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
        sorted_game_names = [g.name for g in sorted_games]
        reference_ranks = {
            appid: sorted_game_names.index(games[appid].name) + 1
            for appid in appid_reference_set
            if appid in games
        }
    else:
        sorted_game_names = [g["name"] for g in sorted_games]
        reference_ranks = {
            appid: sorted_game_names.index(games[appid]["name"]) + 1
            for appid in appid_reference_set
            if appid in games
        }

    objective_value = (
        np.average(list(reference_ranks.values())) if reference_ranks else float("nan")
    )

    if not verbose:
        return objective_value, []

    print(f"Objective function to minimize:\t{objective_value}")

    ranking_list = []
    rank = 1
    for game in sorted_games:
        appid = game.appid if language is None else game["name"]
        if (
            (not filtered_app_ids_to_show or appid in filtered_app_ids_to_show)
            and (not filtered_app_ids_to_hide or appid not in filtered_app_ids_to_hide)
            and (language is not None or game.should_appear_in_ranking)
        ):
            game_name = game.name if language is None else game["name"]
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
    if appid_reference_set is None:
        appid_reference_set = {APP_ID_CONTRADICTION}

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
            optimal_parameters = [10**6.52]
        else:
            optimal_parameters = [10**6.63]
    elif quality_measure_str == "wilson_score":
        optimal_parameters = [10**4.83]
    else:
        optimal_parameters = [10**4.89]

    filtered_in_app_ids = get_appid_by_keyword_list_to_include(keywords_to_include)
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
    if keywords_to_include is None:
        keywords_to_include = []
    if keywords_to_exclude is None:
        keywords_to_exclude = []

    input_filename = "dict_top_rated_games_on_steam.json"
    output_filename = "hidden_gems.md"
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
