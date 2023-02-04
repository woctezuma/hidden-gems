# References:
#   https://github.com/woctezuma/steam-reviews/blob/master/download_reviews.py
#   https://github.com/woctezuma/steam-reviews/blob/master/analyze_language.py

import ast
import pathlib
from pathlib import Path

import iso639
import steamreviews
import steamspypi
from langdetect import DetectorFactory, detect, lang_detect_exception

from compute_bayesian_rating import choose_prior, compute_bayesian_score
from compute_stats import compute_ranking, save_ranking_to_file
from compute_wilson_score import compute_wilson_score
from create_dict_using_json import get_mid_of_interval


def get_review_language_dictionary(app_id, previously_detected_languages_dict=None):
    # Returns dictionary: reviewID -> dictionary with (tagged language, detected language)

    review_data = steamreviews.load_review_dict(app_id)

    print('\nAppID: ' + app_id)

    reviews = list(review_data['reviews'].values())

    language_dict = {}

    if previously_detected_languages_dict is None:
        previously_detected_languages_dict = {}

    if app_id not in previously_detected_languages_dict.keys():
        previously_detected_languages_dict[app_id] = {}

    for review in reviews:
        # Review ID
        review_id = review["recommendationid"]

        # Review polarity tag, i.e. either "recommended" or "not recommended"
        is_a_positive_review = review['voted_up']

        # Review text
        review_content = review['review']

        # Review language tag
        review_language_tag = review['language']

        # Review's automatically detected language
        if review_id in previously_detected_languages_dict[app_id]:
            detected_language = previously_detected_languages_dict[app_id][review_id]
        else:
            try:
                DetectorFactory.seed = 0
                detected_language = detect(review_content)
            except lang_detect_exception.LangDetectException:
                detected_language = 'unknown'
            previously_detected_languages_dict[app_id][review_id] = detected_language
            previously_detected_languages_dict['has_changed'] = True

        language_dict[review_id] = {}
        language_dict[review_id]['tag'] = review_language_tag
        language_dict[review_id]['detected'] = detected_language
        language_dict[review_id]['voted_up'] = is_a_positive_review

    return language_dict, previously_detected_languages_dict


# noinspection PyPep8Naming
def most_common(L):
    # Reference: https://stackoverflow.com/a/1518632

    import itertools
    import operator

    # get an iterable of (item, iterable) pairs
    # noinspection PyPep8Naming
    SL = sorted((x, i) for i, x in enumerate(L))
    groups = itertools.groupby(SL, key=operator.itemgetter(0))

    # auxiliary function to get "quality" for an item
    def _auxfun(g):
        _, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        return count, -min_index

    # pick the highest-count/earliest item
    return max(groups, key=_auxfun)[0]


def convert_review_language_dictionary_to_iso(language_dict):
    language_iso_dict = {}

    languages = {r['tag'] for r in language_dict.values()}

    for language in languages:
        try:
            language_iso = iso639.to_iso639_1(language)

        except iso639.NonExistentLanguageError:
            if language == 'schinese' or language == 'tchinese':
                language_iso = 'zh-cn'
            elif language == 'brazilian':
                language_iso = 'pt'
            elif language == 'koreana':
                language_iso = 'ko'
            else:
                print('Missing language:' + language)

                detected_languages = [
                    r['detected']
                    for r in language_dict.values()
                    if r['tag'] == language
                ]
                print(detected_languages)

                language_iso = most_common(detected_languages)
                print('Most common match among detected languages: ' + language_iso)

        language_iso_dict[language] = language_iso

    return language_iso_dict


def summarize_review_language_dictionary(language_dict):
    # Returns dictionary: language -> review stats including:
    #                                 - number of reviews for which tagged language coincides with detected language
    #                                 - number of such reviews which are "Recommended"
    #                                 - number of such reviews which are "Not Recommended"

    summary_dict = {}

    language_iso_dict = convert_review_language_dictionary_to_iso(language_dict)

    for language_iso in set(language_iso_dict.values()):
        reviews_with_matching_languages = [
            r for r in language_dict.values() if r['detected'] == language_iso
        ]
        num_votes = len(reviews_with_matching_languages)
        positive_reviews_with_matching_languages = [
            r for r in reviews_with_matching_languages if bool(r['voted_up'])
        ]
        num_upvotes = len(positive_reviews_with_matching_languages)
        num_downvotes = num_votes - num_upvotes

        summary_dict[language_iso] = {}
        summary_dict[language_iso]['voted'] = num_votes
        summary_dict[language_iso]['voted_up'] = num_upvotes
        summary_dict[language_iso]['voted_down'] = num_downvotes

    return summary_dict


def get_all_review_language_summaries(
    previously_detected_languages_filename=None,
    delta_n_reviews_between_temp_saves=10,
):
    from appids import appid_hidden_gems_reference_set

    with Path('idlist.txt').open() as f:
        d = f.readlines()

    app_id_list = [x.strip() for x in d]

    app_id_list = list(set(app_id_list).union(appid_hidden_gems_reference_set))

    game_feature_dict = {}
    all_languages = set()

    # Load the result of language detection for each review
    try:
        previously_detected_languages = load_content_from_disk(
            previously_detected_languages_filename,
        )
    except FileNotFoundError:
        previously_detected_languages = {}

    previously_detected_languages['has_changed'] = False

    for count, appID in enumerate(app_id_list):
        (language_dict, previously_detected_languages) = get_review_language_dictionary(
            appID,
            previously_detected_languages,
        )

        summary_dict = summarize_review_language_dictionary(language_dict)

        game_feature_dict[appID] = summary_dict
        all_languages = all_languages.union(summary_dict.keys())

        if delta_n_reviews_between_temp_saves > 0:
            flush_to_file_now = bool(count % delta_n_reviews_between_temp_saves == 0)
        else:
            flush_to_file_now = bool(count == len(app_id_list) - 1)

        # Export the result of language detection for each review, so as to avoid repeating intensive computations.
        if (
            previously_detected_languages_filename is not None
            and flush_to_file_now
            and previously_detected_languages['has_changed']
        ):
            write_content_to_disk(
                previously_detected_languages,
                previously_detected_languages_filename,
            )
            previously_detected_languages['has_changed'] = False

        print('AppID ' + str(count + 1) + '/' + str(len(app_id_list)) + ' done.')

    all_languages = sorted(all_languages)

    return game_feature_dict, all_languages


def load_content_from_disk(filename):
    with Path(filename).open(encoding="utf8") as f:
        lines = f.readlines()
        # The content is on the first line
        content = ast.literal_eval(lines[0])

    return content


def write_content_to_disk(content_to_write, filename):
    # Export the content to a text file

    with Path(filename).open('w', encoding="utf8") as f:
        print(content_to_write, file=f)

    return


def compute_review_language_distribution(game_feature_dict, all_languages):
    # Compute the distribution of review languages among reviewers

    review_language_distribution = {}

    for appID in game_feature_dict:
        data_for_current_game = game_feature_dict[appID]

        num_reviews = sum(
            [
                data_for_current_game[language]['voted']
                for language in data_for_current_game
            ],
        )

        review_language_distribution[appID] = {}
        review_language_distribution[appID]['num_reviews'] = num_reviews
        review_language_distribution[appID]['distribution'] = {}
        for language in all_languages:
            try:
                review_language_distribution[appID]['distribution'][language] = (
                    data_for_current_game[language]['voted'] / num_reviews
                )
            except KeyError:
                review_language_distribution[appID]['distribution'][language] = 0

    return review_language_distribution


def print_prior(prior, all_languages=None):
    if all_languages is None:
        print(repr(prior))
    else:
        for language in all_languages:
            print(f'{language} : {repr(prior[language])}')

    return


def choose_language_independent_prior_based_on_whole_steam_catalog(
    steam_spy_dict,
    all_languages,
    verbose=False,
):
    # Construct observation structure used to compute a prior for the inference of a Bayesian rating
    observations = {}
    for appid in steam_spy_dict:
        num_positive_reviews = steam_spy_dict[appid]['positive']
        num_negative_reviews = steam_spy_dict[appid]['negative']

        num_votes = num_positive_reviews + num_negative_reviews

        if num_votes > 0:
            observations[appid] = {}
            observations[appid]['num_votes'] = num_votes
            observations[appid]['score'] = num_positive_reviews / num_votes

    common_prior = choose_prior(observations)

    if verbose:
        print_prior(common_prior)

    # For each language, compute the prior to be used for the inference of a Bayesian rating

    language_independent_prior = {}

    for language in all_languages:
        language_independent_prior[language] = common_prior

    return language_independent_prior


def choose_language_independent_prior_based_on_hidden_gems(
    game_feature_dict,
    all_languages,
    verbose=False,
):
    # Construct observation structure used to compute a prior for the inference of a Bayesian rating
    observations = {}
    for appid in game_feature_dict:
        num_positive_reviews = 0
        num_negative_reviews = 0

        for language in all_languages:
            try:
                num_positive_reviews += game_feature_dict[appid][language]['voted_up']
                num_negative_reviews += game_feature_dict[appid][language]['voted_down']
            except KeyError:
                continue

        num_votes = num_positive_reviews + num_negative_reviews

        if num_votes > 0:
            observations[appid] = {}
            observations[appid]['num_votes'] = num_votes
            observations[appid]['score'] = num_positive_reviews / num_votes

    common_prior = choose_prior(observations)

    if verbose:
        print_prior(common_prior)

    # For each language, compute the prior to be used for the inference of a Bayesian rating

    language_independent_prior = {}

    for language in all_languages:
        language_independent_prior[language] = common_prior

    return language_independent_prior


def choose_language_specific_prior_based_on_hidden_gems(
    game_feature_dict,
    all_languages,
    verbose=False,
):
    # For each language, compute the prior to be used for the inference of a Bayesian rating
    language_specific_prior = {}
    for language in all_languages:
        # Construct observation structure used to compute a prior for the inference of a Bayesian rating
        observations = {}
        for appid in game_feature_dict:
            try:
                num_positive_reviews = game_feature_dict[appid][language]['voted_up']
                num_negative_reviews = game_feature_dict[appid][language]['voted_down']
            except KeyError:
                num_positive_reviews = 0
                num_negative_reviews = 0

            num_votes = num_positive_reviews + num_negative_reviews

            if num_votes > 0:
                observations[appid] = {}
                observations[appid]['num_votes'] = num_votes
                observations[appid]['score'] = num_positive_reviews / num_votes

        language_specific_prior[language] = choose_prior(observations)

    if verbose:
        print_prior(language_specific_prior, all_languages)

    return language_specific_prior


def prepare_dictionary_for_ranking_of_hidden_gems(
    steam_spy_dict,
    game_feature_dict,
    all_languages,
    compute_prior_on_whole_steam_catalog=True,
    compute_language_specific_prior=False,
    verbose=False,
    quantile_for_our_own_wilson_score=0.95,
):
    # Prepare dictionary to feed to compute_stats module in hidden-gems repository

    # noinspection PyPep8Naming
    D = {}

    review_language_distribution = compute_review_language_distribution(
        game_feature_dict,
        all_languages,
    )

    if compute_prior_on_whole_steam_catalog:
        whole_catalog_prior = (
            choose_language_independent_prior_based_on_whole_steam_catalog(
                steam_spy_dict,
                all_languages,
                verbose,
            )
        )

        print(
            'Estimating prior (score and num_votes) on the whole Steam catalog ('
            + str(len(steam_spy_dict))
            + ' games.',
        )
        prior = whole_catalog_prior

    else:
        if compute_language_specific_prior:
            subset_catalog_prior = choose_language_specific_prior_based_on_hidden_gems(
                game_feature_dict,
                all_languages,
                verbose,
            )
        else:
            subset_catalog_prior = (
                choose_language_independent_prior_based_on_hidden_gems(
                    game_feature_dict,
                    all_languages,
                    verbose,
                )
            )

        print(
            'Estimating prior (score and num_votes) on a pre-computed set of '
            + str(len(game_feature_dict))
            + ' hidden gems.',
        )
        prior = subset_catalog_prior

    if verbose:
        print_prior(prior, all_languages)

    for appID in game_feature_dict:
        D[appID] = {}
        try:
            D[appID]['name'] = steam_spy_dict[appID]['name']
        except KeyError:
            D[appID]['name'] = 'Unknown ' + str(appID)

        try:
            num_owners_for_all_languages = steam_spy_dict[appID]['owners']
        except KeyError:
            num_owners_for_all_languages = 0

        try:
            num_owners_for_all_languages = float(num_owners_for_all_languages)
        except ValueError:
            num_owners_for_all_languages = get_mid_of_interval(
                num_owners_for_all_languages,
            )

        for language in all_languages:
            D[appID][language] = {}

            try:
                num_positive_reviews = game_feature_dict[appID][language]['voted_up']
                num_negative_reviews = game_feature_dict[appID][language]['voted_down']
            except KeyError:
                num_positive_reviews = 0
                num_negative_reviews = 0

            num_reviews = num_positive_reviews + num_negative_reviews

            wilson_score = compute_wilson_score(
                num_positive_reviews,
                num_negative_reviews,
                quantile_for_our_own_wilson_score,
            )

            if wilson_score is None:
                wilson_score = -1

            if num_reviews > 0:
                # Construct game structure used to compute Bayesian rating
                game = {}
                game['score'] = num_positive_reviews / num_reviews
                game['num_votes'] = num_reviews

                bayesian_rating = compute_bayesian_score(game, prior[language])
            else:
                bayesian_rating = -1

            # Assumption: for every game, owners and reviews are distributed among regions in the same proportions.
            num_owners = (
                num_owners_for_all_languages
                * review_language_distribution[appID]['distribution'][language]
            )

            if num_owners < num_reviews:
                print(
                    "[Warning] Abnormal data detected ("
                    + str(int(num_owners))
                    + " owners ; "
                    + str(num_reviews)
                    + " reviews) for language="
                    + language
                    + " and appID="
                    + appID
                    + ". Game skipped.",
                )
                wilson_score = -1
                bayesian_rating = -1

            D[appID][language]['wilson_score'] = wilson_score
            D[appID][language]['bayesian_rating'] = bayesian_rating
            D[appID][language]['num_owners'] = num_owners
            D[appID][language]['num_reviews'] = num_reviews

    return D


def get_language_features_filename():
    return "dict_review_languages.txt"


def get_all_languages_filename():
    return "list_all_languages.txt"


def get_detected_languages_filename():
    return "previously_detected_languages.txt"


def get_input_data(load_from_cache=True):
    if load_from_cache:
        game_feature_dict = load_content_from_disk(get_language_features_filename())

        all_languages = load_content_from_disk(get_all_languages_filename())

    else:
        (game_feature_dict, all_languages) = get_all_review_language_summaries(
            get_detected_languages_filename(),
        )

        write_content_to_disk(game_feature_dict, get_language_features_filename())

        write_content_to_disk(all_languages, get_all_languages_filename())

    return game_feature_dict, all_languages


def download_steam_reviews():
    from appids import appid_hidden_gems_reference_set

    # All the reference hidden-gems
    steamreviews.download_reviews_for_app_id_batch(appid_hidden_gems_reference_set)

    # All the remaining hidden-gem candidates, which app_ids are stored in idlist.txt
    steamreviews.download_reviews_for_app_id_batch()


def get_regional_data_path():
    return 'regional_rankings/'


def get_regional_ranking_filename(language):
    # Folder where regional rankings of hidden gems are saved to.
    output_folder = get_regional_data_path()

    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)

    output_filename = output_folder + "hidden_gems_" + language + ".md"

    return output_filename


def run_regional_workflow(
    quality_measure_str='wilson_score',
    popularity_measure_str='num_reviews',
    perform_optimization_at_runtime=True,
    num_top_games_to_print=250,
    verbose=False,
    keywords_to_include=None,
    keywords_to_exclude=None,
    load_from_cache=True,
    compute_prior_on_whole_steam_catalog=True,
    compute_language_specific_prior=False,
):
    if keywords_to_include is None:
        keywords_to_include = []  # ["Rogue-Like"]

    if keywords_to_exclude is None:
        keywords_to_exclude = []  # ["Visual Novel", "Anime"]

    if not load_from_cache:
        download_steam_reviews()

    (game_feature_dict, all_languages) = get_input_data(load_from_cache)

    # noinspection PyPep8Naming
    D = prepare_dictionary_for_ranking_of_hidden_gems(
        steamspypi.load(),
        game_feature_dict,
        all_languages,
        compute_prior_on_whole_steam_catalog,
        compute_language_specific_prior,
        verbose=verbose,
    )

    for language in all_languages:
        ranking = compute_ranking(
            D,
            num_top_games_to_print,
            keywords_to_include,
            keywords_to_exclude,
            language,
            perform_optimization_at_runtime,
            popularity_measure_str,
            quality_measure_str,
        )

        save_ranking_to_file(
            get_regional_ranking_filename(language),
            ranking,
            only_show_appid=False,
            verbose=verbose,
        )

    return True


if __name__ == "__main__":
    load_precomputed_review_language_stats = False

    # Whether to compute a prior for Bayesian rating with the whole Steam catalog,
    # or with a pre-computed set of top-ranked hidden gems
    use_global_constant_prior = False

    # Whether to compute a prior for Bayesian rating for each language independently
    use_language_specific_prior = True
    # NB: This bool is only relevant if the prior is NOT based on the whole Steam catalog. Indeed, language-specific
    #     computation is impossible for the whole catalog since we don't have access to language data for every game.
    if use_global_constant_prior and use_language_specific_prior:
        raise AssertionError

    run_regional_workflow(
        quality_measure_str='bayesian_rating',  # Either 'wilson_score' or 'bayesian_rating'
        popularity_measure_str='num_owners',  # Either 'num_reviews' or 'num_owners'
        perform_optimization_at_runtime=True,
        num_top_games_to_print=50,
        verbose=False,
        keywords_to_include=None,
        keywords_to_exclude=None,
        load_from_cache=load_precomputed_review_language_stats,
        compute_prior_on_whole_steam_catalog=use_global_constant_prior,
        compute_language_specific_prior=use_language_specific_prior,
    )
