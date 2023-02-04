# Objective: store information regarding every Steam game in a dictionary.

from pathlib import Path

import steamspypi

from src.appids import APP_ID_CONTRADICTION


def get_mid_of_interval(interval_as_str):
    interval_as_str_formatted = [
        s.replace(",", "") for s in interval_as_str.split("..")
    ]
    lower_bound = float(interval_as_str_formatted[0])
    upper_bound = float(interval_as_str_formatted[1])
    mid_value = (lower_bound + upper_bound) / 2

    return mid_value


def get_leading_comment():
    # First line of the text file containing the output dictionary
    leading_comment = (
        "# Dictionary with key=appid and value=list of name, Wilson score, Bayesian rating, #owners, "
        "#players, median playtime, average playtime, #positive reviews, #negative reviews, boolean "
        "whether to include the game in the ranking"
    )
    return leading_comment


def create_local_dictionary(
    data,
    output_filename,
    appid_reference_set=None,
    quantile_for_our_wilson_score=0.95,
):
    # Objective: compute a score for one Steam game.
    #
    # Input:    - data:                         SteamSpy's data.
    #           - output_filename:              filename to which the local dictionary will be written to.
    #           - appid_reference_set:  a set of appID of games which are examples of "hidden gems".
    #                                           By default, the appID of the game called "Contradiction".
    #           - quantile_for_our_wilson_score: this allows to specify a different confidence for the Wilson score.
    # Output:   none (the local dictionary is written to output_filename)

    if appid_reference_set is None:
        appid_reference_set = {APP_ID_CONTRADICTION}

    from src.compute_bayesian_rating import choose_prior, compute_bayesian_score
    from src.compute_wilson_score import compute_wilson_score

    # noinspection PyPep8Naming
    d = {}

    # Construct observation structure used to compute a prior for the inference of a Bayesian rating
    observations = {}

    for appid in data:
        num_positive_reviews = data[appid]["positive"]
        num_negative_reviews = data[appid]["negative"]

        num_votes = num_positive_reviews + num_negative_reviews

        if num_votes > 0:
            observations[appid] = {}
            observations[appid]["score"] = num_positive_reviews / num_votes
            observations[appid]["num_votes"] = num_votes

    prior = choose_prior(observations)
    print(prior)

    for appid in data:
        name = data[appid]["name"]
        num_owners = data[appid]["owners"]
        try:
            num_owners = float(num_owners)
        except ValueError:
            num_owners = get_mid_of_interval(num_owners)
        try:
            num_players = data[appid]["players_forever"]
        except KeyError:
            num_players = None
        median_time = data[appid]["median_forever"]
        average_time = data[appid]["average_forever"]
        num_positive_reviews = data[appid]["positive"]
        num_negative_reviews = data[appid]["negative"]

        wilson_score = compute_wilson_score(
            num_positive_reviews,
            num_negative_reviews,
            quantile_for_our_wilson_score,
        )

        num_votes = num_positive_reviews + num_negative_reviews

        if num_votes > 0:
            # Construct game structure used to compute Bayesian rating
            game = {}
            game["score"] = num_positive_reviews / num_votes
            game["num_votes"] = num_votes

            bayesian_rating = compute_bayesian_score(game, prior)

        else:
            bayesian_rating = None

        # Make sure the output dictionary includes the game which will be chosen as a reference of a "hidden gem"
        if appid in appid_reference_set:
            if wilson_score is None:
                raise AssertionError
            if bayesian_rating is None:
                raise AssertionError
            print("Game used as a reference:\t" + name + "\t(appID=" + appid + ")")

        if wilson_score is None or bayesian_rating is None:
            print("Game with no review:\t" + name + "\t(appID=" + appid + ")")
        else:
            stats_save = [
                name,
                wilson_score,
                bayesian_rating,
                num_owners,
                num_players,
                median_time,
                average_time,
                num_positive_reviews,
                num_negative_reviews,
            ]

            bool_game_should_appear_in_ranking = True
            stats_save.append(bool_game_should_appear_in_ranking)

            d[appid] = stats_save

    # Save the dictionary to a text file
    with Path(output_filename).open("w", encoding="utf8") as outfile:
        print(get_leading_comment(), file=outfile)
        print(d, file=outfile)


def main():
    from src.appids import appid_hidden_gems_reference_set

    # SteamSpy's data in JSON format
    data = steamspypi.load()

    # A dictionary will be stored in the following text file
    output_filename = "dict_top_rated_games_on_steam.txt"

    create_local_dictionary(data, output_filename, appid_hidden_gems_reference_set)

    return True


if __name__ == "__main__":
    main()
