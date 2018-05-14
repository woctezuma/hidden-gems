# Objective: store information regarding every Steam game in a dictionary.

from appids import appidContradiction


def createLocalDictionary(data, output_filename, appid_reference_set={appidContradiction},
                          quantile_for_our_own_wilson_score=0.95):
    # Objective: compute a score for one Steam game.
    #
    # Input:    - data:                         SteamSpy's data.
    #           - output_filename:              filename to which the local dictionary will be written to.
    #           - appid_reference_set:  a set of appID of games which are examples of "hidden gems".
    #                                           By default, the appID of the game called "Contradiction".
    #           - quantile_for_our_own_wilson_score: this allows to specify a different confidence for the Wilson score.
    # Output:   none (the local dictionary is written to output_filename)

    from compute_wilson_score import computeWilsonScore
    from compute_bayesian_rating import choose_prior, compute_bayesian_score

    D = dict()

    # Construct observation structure used to compute a prior for the inference of a Bayesian rating
    observations = dict()

    for appid in data.keys():
        num_positive_reviews = data[appid]["positive"]
        num_negative_reviews = data[appid]["negative"]

        num_votes = num_positive_reviews + num_negative_reviews

        if num_votes > 0:
            observations[appid] = dict()
            observations[appid]['score'] = num_positive_reviews / num_votes
            observations[appid]['num_votes'] = num_votes

    prior = choose_prior(observations)
    print(prior)

    for appid in data.keys():
        name = data[appid]['name']
        num_owners = data[appid]['owners']
        try:
            num_players = data[appid]['players_forever']
        except KeyError:
            num_players = None
        median_time = data[appid]['median_forever']
        average_time = data[appid]['average_forever']
        num_positive_reviews = data[appid]["positive"]
        num_negative_reviews = data[appid]["negative"]

        wilson_score = computeWilsonScore(num_positive_reviews, num_negative_reviews, quantile_for_our_own_wilson_score)

        num_votes = num_positive_reviews + num_negative_reviews

        if num_votes > 0:

            # Construct game structure used to compute Bayesian rating
            game = dict()
            game['score'] = num_positive_reviews / num_votes
            game['num_votes'] = num_votes

            bayesian_rating = compute_bayesian_score(game, prior)

        else:
            bayesian_rating = None

        # Make sure the output dictionary includes the game which will be chosen as a reference of a "hidden gem"
        if appid in appid_reference_set:
            assert (not (wilson_score is None))
            assert (not (bayesian_rating is None))
            print("Game used as a reference:\t" + name + "\t(appID=" + appid + ")")

        if wilson_score is None or bayesian_rating is None:
            print("Game with no review:\t" + name + "\t(appID=" + appid + ")")
        else:
            stats_save = [name, wilson_score, bayesian_rating, num_owners, num_players, median_time, average_time,
                          num_positive_reviews,
                          num_negative_reviews]

            boolGameShouldAppearInRanking = True
            stats_save.append(boolGameShouldAppearInRanking)

            D[appid] = stats_save

    # First line of the text file containing the output dictionary
    leading_comment = "# Dictionary with key=appid and value=list of name, Wilson score, Bayesian rating, #owners, " \
                      "#players, median playtime, average playtime, #positive reviews, #negative reviews, boolean " \
                      "whether to include the game in the ranking"

    # Save the dictionary to a text file
    with open(output_filename, 'w', encoding="utf8") as outfile:
        print(leading_comment, file=outfile)
        print(D, file=outfile)


def main():
    from appids import appid_hidden_gems_reference_set
    from download_json import downloadSteamSpyData
    import time

    json_filename_suffixe = "_steamspy.json"

    # Get current day as yyyymmdd format
    date_format = "%Y%m%d"
    current_date = time.strftime(date_format)

    # Database filename
    json_filename = current_date + json_filename_suffixe

    # SteamSpy's data in JSON format
    data = downloadSteamSpyData(json_filename)

    # A dictionary will be stored in the following text file
    output_filename = "dict_top_rated_games_on_steam.txt"

    createLocalDictionary(data, output_filename, appid_hidden_gems_reference_set)

    return True


if __name__ == "__main__":
    main()
