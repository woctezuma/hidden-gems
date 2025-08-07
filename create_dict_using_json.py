# Objective: store information regarding every Steam game in a dictionary.

import json
from dataclasses import asdict
from pathlib import Path

import steamspypi

from src.appids import APP_ID_CONTRADICTION, appid_hidden_gems_reference_set
from src.compute_bayesian_rating import choose_prior, compute_bayesian_score
from src.compute_wilson_score import compute_wilson_score
from src.game import Game


def get_mid_of_interval(interval_as_str: str) -> float:
    interval_as_str_formatted = [
        s.replace(",", "") for s in interval_as_str.split("..")
    ]
    lower_bound = float(interval_as_str_formatted[0])
    upper_bound = float(interval_as_str_formatted[1])
    return (lower_bound + upper_bound) / 2


def get_leading_comment() -> str:
    # First line of the text file containing the output dictionary
    return (
        "# Dictionary with key=appid and value=list of name, Wilson score, Bayesian rating, #owners, "
        "#players, median playtime, average playtime, #positive reviews, #negative reviews, boolean "
        "whether to include the game in the ranking"
    )


def _compute_prior(data: dict) -> dict:
    # Construct observation structure used to compute a prior for the inference of a Bayesian rating
    observations = {}
    for appid, app_data in data.items():
        num_positive_reviews = app_data["positive"]
        num_negative_reviews = app_data["negative"]
        num_votes = num_positive_reviews + num_negative_reviews
        if num_votes > 0:
            observations[appid] = {
                "score": num_positive_reviews / num_votes,
                "num_votes": num_votes,
            }
    prior = choose_prior(observations)
    print(f"Prior: {prior}")
    return prior


def _create_game_from_steamspy_data(
    appid: str,
    app_data: dict,
    prior: dict,
    quantile_for_our_wilson_score: float,
) -> Game | None:
    num_positive_reviews = app_data["positive"]
    num_negative_reviews = app_data["negative"]

    wilson_score = compute_wilson_score(
        num_positive_reviews,
        num_negative_reviews,
        quantile_for_our_wilson_score,
    )

    num_votes = num_positive_reviews + num_negative_reviews
    if num_votes > 0:
        # Construct game structure used to compute Bayesian rating
        game_for_bayesian = {
            "score": num_positive_reviews / num_votes,
            "num_votes": num_votes,
        }
        bayesian_rating = compute_bayesian_score(game_for_bayesian, prior)
    else:
        bayesian_rating = None

    if wilson_score is None or bayesian_rating is None:
        print(f"Game with no review:\t{app_data['name']}\t(appID={appid})")
        return None

    num_owners = app_data["owners"]
    try:
        num_owners = float(num_owners)
    except ValueError:
        num_owners = get_mid_of_interval(num_owners)

    return Game(
        appid=appid,
        name=app_data["name"],
        wilson_score=wilson_score,
        bayesian_rating=bayesian_rating,
        num_owners=num_owners,
        num_players=app_data.get("players_forever"),
        median_playtime=app_data["median_forever"],
        average_playtime=app_data["average_forever"],
        num_positive_reviews=num_positive_reviews,
        num_negative_reviews=num_negative_reviews,
    )


def _save_games_to_json(games: dict[str, Game], output_filename: str | Path) -> None:
    with Path(output_filename).open("w", encoding="utf8") as f:
        json.dump({appid: asdict(game) for appid, game in games.items()}, f, indent=4)


def create_games_dictionary(
    data: dict,
    output_filename: str | Path,
    appid_reference_set: set[str] | None = None,
    quantile_for_our_wilson_score: float = 0.95,
) -> None:
    if appid_reference_set is None:
        appid_reference_set = {APP_ID_CONTRADICTION}

    prior = _compute_prior(data)

    games = {}
    for appid, app_data in data.items():
        game = _create_game_from_steamspy_data(
            appid,
            app_data,
            prior,
            quantile_for_our_wilson_score,
        )

        # Make sure the output dictionary includes the game which will be chosen as a reference of a "hidden gem"
        if appid in appid_reference_set:
            if game:
                print(
                    f"Game used as a reference:\t{game.name}\t(appID={game.appid})",
                )
            else:
                raise AssertionError

        if game:
            games[appid] = game

    # Save the dictionary to a JSON file
    _save_games_to_json(games, output_filename)


def main() -> bool:
    # SteamSpy's data in JSON format
    data = steamspypi.load()

    # A dictionary will be stored in the following JSON file
    output_filename = "dict_top_rated_games_on_steam.json"

    create_games_dictionary(
        data,
        output_filename,
        appid_hidden_gems_reference_set,
    )
    return True


if __name__ == "__main__":
    main()
