# Objective: store information regarding every Steam game in a dictionary.

# This is the appID of the game called "Contradiction".
appidContradiction = "373390"
# This is a set including appID of games which will serve as references of "hidden gems", so we will make sure that
# these games appear in the output dictionary, despite filter-out and filter-in.
# Reference: http://www.neogaf.com/forum/showpost.php?p=241232835&postcount=5886
appid_default_reference_set = {appidContradiction, "320090", "363980", "561740", "333300", "329970", "323220",
                               "534290", "440880", "402040", "233980"}

def createLocalDictionary(data, output_filename, appid_default_reference_set = {appidContradiction},
                                                 quantile_for_our_own_wilson_score = 0.95):
    # Objective: compute a score for one Steam game.
    #
    # Input:    - data:                         SteamSpy's data.
    #           - output_filename:              filename to which the local dictionary will be written to.
    #           - appid_default_reference_set:  a set of appID of games which are examples of "hidden gems".
    #                                           By default, the appID of the game called "Contradiction".
    #           - quantile_for_our_own_wilson_score: this allows to specify a different confidence for the Wilson score.
    # Output:   none (the local dictionary is written to output_filename)

    from compute_wilson_score import computeWilsonScore

    D = dict()

    for appid in data.keys():
        name = data[appid]['name']
        num_owners = data[appid]['owners']
        num_players = data[appid]['players_forever']
        median_time = data[appid]['median_forever']
        average_time = data[appid]['average_forever']
        num_positive_reviews = data[appid]["positive"]
        num_negative_reviews = data[appid]["negative"]

        wilson_score = computeWilsonScore(num_positive_reviews, num_negative_reviews, quantile_for_our_own_wilson_score)

        # Make sure the output dictionary includes the game which will be chosen as a reference of a "hidden gem"
        if appid in appid_default_reference_set:
            assert( not(wilson_score is None) )
            print("Game used as a reference:\t" + name + "\t(appID=" + appid + ")")

        if wilson_score is None:
            print("Game with no review:\t" + name + "\t(appID=" + appid + ")")
        else:
            stats_save = [name, wilson_score, num_owners, num_players, median_time, average_time, num_positive_reviews,
                          num_negative_reviews]

            boolGameShouldAppearInRanking = True
            stats_save.append(boolGameShouldAppearInRanking)

            D[appid] = stats_save

    # First line of the text file containing the output dictionary
    leading_comment = "# Dictionary with key=appid and value=list of name, Wilson score, #owners, #players, median playtime, average playtime, boolean whether to include the game in the ranking"

    # Save the dictionary to a text file
    with open(output_filename, 'w', encoding="utf8") as outfile:
        print(leading_comment, file=outfile)
        print(D, file=outfile)

if __name__ == "__main__":
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

    createLocalDictionary(data, output_filename, appid_default_reference_set)
