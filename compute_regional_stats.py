# References:
#   https://github.com/woctezuma/steam-reviews/blob/master/download_reviews.py
#   https://github.com/woctezuma/steam-reviews/blob/master/analyze_language.py

import itertools
import json
import operator
from pathlib import Path
from typing import Any

import iso639
import steamreviews
import steamspypi
from langdetect import DetectorFactory, detect, lang_detect_exception

from compute_stats import (
    PopularityMeasure,
    QualityMeasure,
    compute_ranking,
    save_ranking_to_file,
)
from create_dict_using_json import get_mid_of_interval
from src.appids import appid_hidden_gems_reference_set
from src.compute_bayesian_rating import choose_prior, compute_bayesian_score
from src.compute_wilson_score import compute_wilson_score


def get_review_language_dictionary(
    app_id: str,
    previously_detected_languages_dict: dict | None = None,
) -> tuple[dict, dict]:
    # Returns dictionary: reviewID -> dictionary with (tagged language, detected language)
    review_data = steamreviews.load_review_dict(app_id)
    print(f"\nAppID: {app_id}")

    reviews = list(review_data["reviews"].values())
    language_dict = {}

    if previously_detected_languages_dict is None:
        previously_detected_languages_dict = {}
    if app_id not in previously_detected_languages_dict:
        previously_detected_languages_dict[app_id] = {}

    for review in reviews:
        review_id = review["recommendationid"]
        if review_id in previously_detected_languages_dict[app_id]:
            detected_language = previously_detected_languages_dict[app_id][review_id]
        else:
            try:
                DetectorFactory.seed = 0
                detected_language = detect(review["review"])
            except lang_detect_exception.LangDetectException:
                detected_language = "unknown"
            previously_detected_languages_dict[app_id][review_id] = detected_language
            previously_detected_languages_dict["has_changed"] = True

        language_dict[review_id] = {
            "tag": review["language"],
            "detected": detected_language,
            "voted_up": review["voted_up"],
        }

    return language_dict, previously_detected_languages_dict


def most_common(lst: list) -> Any:
    # Reference: https://stackoverflow.com/a/1518632
    # get an iterable of (item, iterable) pairs
    sl = sorted((x, i) for i, x in enumerate(lst))
    groups = itertools.groupby(sl, key=operator.itemgetter(0))

    # auxiliary function to get "quality" for an item
    def _auxfun(g):
        _item, iterable = g
        count = 0
        min_index = len(lst)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        return count, -min_index

    # pick the highest-count/earliest item
    return max(groups, key=_auxfun)[0]


def convert_review_language_dictionary_to_iso(language_dict: dict) -> dict[str, str]:
    language_iso_dict = {}
    languages = {r["tag"] for r in language_dict.values()}

    for language in languages:
        try:
            language_iso = iso639.to_iso639_1(language)
        except iso639.NonExistentLanguageError:
            if language in {"schinese", "tchinese"}:
                language_iso = "zh-cn"
            elif language == "brazilian":
                language_iso = "pt"
            elif language == "koreana":
                language_iso = "ko"
            else:
                print(f"Missing language: {language}")
                detected_languages = [
                    r["detected"]
                    for r in language_dict.values()
                    if r["tag"] == language
                ]
                print(detected_languages)
                language_iso = most_common(detected_languages)
                print(f"Most common match among detected languages: {language_iso}")
        language_iso_dict[language] = language_iso

    return language_iso_dict


def summarize_review_language_dictionary(language_dict: dict) -> dict[str, dict]:
    # Returns dictionary: language -> review stats including:
    #                                 - number of reviews for which tagged language coincides with detected language
    #                                 - number of such reviews which are "Recommended"
    #                                 - number of such reviews which are "Not Recommended"
    summary_dict = {}
    language_iso_dict = convert_review_language_dictionary_to_iso(language_dict)

    for language_iso in set(language_iso_dict.values()):
        reviews = [r for r in language_dict.values() if r["detected"] == language_iso]
        num_votes = len(reviews)
        num_upvotes = len([r for r in reviews if r["voted_up"]])
        summary_dict[language_iso] = {
            "voted": num_votes,
            "voted_up": num_upvotes,
            "voted_down": num_votes - num_upvotes,
        }
    return summary_dict


def get_all_review_language_summaries(
    previously_detected_languages_filename: str | Path | None = None,
    delta_n_reviews_between_temp_saves: int = 10,
) -> tuple[dict, list[str]]:
    with Path("idlist.txt").open(encoding="utf-8") as f:
        app_id_list = [x.strip() for x in f]
    app_id_list = list(set(app_id_list).union(appid_hidden_gems_reference_set))

    game_feature_dict = {}
    all_languages = set()

    # Load the result of language detection for each review
    try:
        previously_detected_languages = load_from_json(
            previously_detected_languages_filename,
        )
    except FileNotFoundError:
        previously_detected_languages = {}
    previously_detected_languages["has_changed"] = False

    for i, app_id in enumerate(app_id_list):
        language_dict, previously_detected_languages = get_review_language_dictionary(
            app_id,
            previously_detected_languages,
        )
        summary_dict = summarize_review_language_dictionary(language_dict)
        game_feature_dict[app_id] = summary_dict
        all_languages.update(summary_dict.keys())

        # Export the result of language detection for each review, so as to avoid repeating intensive computations.
        if (
            previously_detected_languages_filename
            and (i + 1) % delta_n_reviews_between_temp_saves == 0
            and previously_detected_languages.get("has_changed")
        ):
            save_to_json(
                previously_detected_languages,
                previously_detected_languages_filename,
            )
            previously_detected_languages["has_changed"] = False

        print(f"AppID {i + 1}/{len(app_id_list)} done.")

    return game_feature_dict, sorted(all_languages)


def load_from_json(filename: str | Path) -> Any:
    with Path(filename).open(encoding="utf8") as f:
        return json.load(f)


def save_to_json(content: Any, filename: str | Path) -> None:
    with Path(filename).open("w", encoding="utf8") as f:
        json.dump(content, f, indent=4)


def compute_review_language_distribution(
    game_feature_dict: dict,
    all_languages: list[str],
) -> dict:
    # Compute the distribution of review languages among reviewers
    review_language_distribution = {}
    for app_id, data in game_feature_dict.items():
        num_reviews = sum(lang_data["voted"] for lang_data in data.values())
        distribution = {
            lang: data.get(lang, {}).get("voted", 0) / num_reviews
            for lang in all_languages
        }
        review_language_distribution[app_id] = {
            "num_reviews": num_reviews,
            "distribution": distribution,
        }
    return review_language_distribution


def _calculate_prior(observations: dict, *, verbose: bool = False) -> dict:
    prior = choose_prior(observations)
    if verbose:
        print(f"Prior: {prior!r}")
    return prior


def choose_language_independent_prior(
    steam_spy_dict: dict,
    all_languages: list[str],
    *,
    verbose: bool = False,
) -> dict[str, dict]:
    # Construct observation structure used to compute a prior for the inference of a Bayesian rating
    observations = {}
    for appid, app_data in steam_spy_dict.items():
        num_pos = app_data["positive"]
        num_neg = app_data["negative"]
        num_votes = num_pos + num_neg
        if num_votes > 0:
            observations[appid] = {
                "score": num_pos / num_votes,
                "num_votes": num_votes,
            }
    common_prior = _calculate_prior(observations, verbose=verbose)
    return dict.fromkeys(all_languages, common_prior)


def choose_language_specific_prior(
    game_feature_dict: dict,
    all_languages: list[str],
    *,
    verbose: bool = False,
) -> dict[str, dict]:
    # For each language, compute the prior to be used for the inference of a Bayesian rating
    language_specific_prior = {}
    for language in all_languages:
        observations = {}
        for appid, features in game_feature_dict.items():
            lang_features = features.get(language, {})
            num_pos = lang_features.get("voted_up", 0)
            num_neg = lang_features.get("voted_down", 0)
            num_votes = num_pos + num_neg
            if num_votes > 0:
                observations[appid] = {
                    "score": num_pos / num_votes,
                    "num_votes": num_votes,
                }
        prior = _calculate_prior(observations, verbose=verbose)
        language_specific_prior[language] = prior
        if verbose:
            print(f"{language}: {prior!r}")
    return language_specific_prior


def prepare_dictionary_for_ranking_of_hidden_gems(
    steam_spy_dict: dict,
    game_feature_dict: dict,
    all_languages: list[str],
    quantile_for_our_own_wilson_score: float = 0.95,
    *,
    compute_prior_on_whole_steam_catalog: bool = True,
    compute_language_specific_prior: bool = False,
    verbose: bool = False,
) -> dict:
    # Prepare dictionary to feed to compute_stats module in hidden-gems repository
    games = {}
    review_language_distribution = compute_review_language_distribution(
        game_feature_dict,
        all_languages,
    )

    if compute_prior_on_whole_steam_catalog:
        print(
            f"Estimating prior on the whole Steam catalog ({len(steam_spy_dict)} games).",
        )
        prior = choose_language_independent_prior(
            steam_spy_dict,
            all_languages,
            verbose=verbose,
        )
    else:
        print(
            f"Estimating prior on a pre-computed set of {len(game_feature_dict)} hidden gems.",
        )
        prior = choose_language_specific_prior(
            game_feature_dict,
            all_languages,
            verbose=verbose,
        )

    for app_id, features in game_feature_dict.items():
        games[app_id] = {
            "appid": app_id,
            "name": steam_spy_dict.get(app_id, {}).get("name", f"Unknown {app_id}"),
        }
        try:
            owners_str = steam_spy_dict[app_id]["owners"]
            num_owners_for_all_languages = float(owners_str)
        except (KeyError, ValueError):
            num_owners_for_all_languages = (
                get_mid_of_interval(owners_str)
                if "owners" in steam_spy_dict.get(app_id, {})
                else 0
            )

        for language in all_languages:
            lang_features = features.get(language, {})
            num_pos = lang_features.get("voted_up", 0)
            num_neg = lang_features.get("voted_down", 0)
            num_reviews = num_pos + num_neg

            wilson_score = (
                compute_wilson_score(
                    num_pos,
                    num_neg,
                    quantile_for_our_own_wilson_score,
                )
                or -1
            )

            if num_reviews > 0:
                # Construct game structure used to compute Bayesian rating
                game_for_bayesian = {
                    "score": num_pos / num_reviews,
                    "num_votes": num_reviews,
                }
                bayesian_rating = compute_bayesian_score(
                    game_for_bayesian,
                    prior[language],
                )
            else:
                bayesian_rating = -1

            # Assumption: for every game, owners and reviews are distributed among regions in the same proportions.
            num_owners = (
                num_owners_for_all_languages
                * review_language_distribution[app_id]["distribution"][language]
            )

            if num_owners < num_reviews:
                print(
                    f"[Warning] Abnormal data detected ({int(num_owners)} owners; "
                    f"{num_reviews} reviews) for language={language} and appID={app_id}. "
                    "Game skipped.",
                )
                wilson_score = bayesian_rating = -1

            games[app_id][language] = {
                "wilson_score": wilson_score,
                "bayesian_rating": bayesian_rating,
                "num_owners": num_owners,
                "num_reviews": num_reviews,
            }

    return games


def get_language_features_filename() -> str:
    return "dict_review_languages.json"


def get_all_languages_filename() -> str:
    return "list_all_languages.json"


def get_detected_languages_filename() -> str:
    return "previously_detected_languages.json"


def get_input_data(*, load_from_cache: bool = True) -> tuple[dict, list[str]]:
    if load_from_cache:
        try:
            game_feature_dict = load_from_json(get_language_features_filename())
            all_languages = load_from_json(get_all_languages_filename())
        except FileNotFoundError:
            print("Cache files not found. Falling back to downloading.")
        else:
            return game_feature_dict, all_languages

    game_feature_dict, all_languages = get_all_review_language_summaries(
        get_detected_languages_filename(),
    )
    save_to_json(game_feature_dict, get_language_features_filename())
    save_to_json(all_languages, get_all_languages_filename())
    return game_feature_dict, all_languages


def download_steam_reviews() -> None:
    # All the reference hidden-gems
    steamreviews.download_reviews_for_app_id_batch(appid_hidden_gems_reference_set)
    # All the remaining hidden-gem candidates, which app_ids are stored in idlist.txt
    steamreviews.download_reviews_for_app_id_batch()


def get_regional_data_path() -> Path:
    path = Path("regional_rankings/")
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_regional_ranking_filename(language: str) -> Path:
    # Folder where regional rankings of hidden gems are saved to.
    return get_regional_data_path() / f"hidden_gems_{language}.md"


def run_regional_workflow(
    quality_measure_str: QualityMeasure = "wilson_score",
    popularity_measure_str: PopularityMeasure = "num_reviews",
    num_top_games_to_print: int = 250,
    keywords_to_include: list[str] | None = None,
    keywords_to_exclude: list[str] | None = None,
    *,
    perform_optimization_at_runtime: bool = True,
    verbose: bool = False,
    load_from_cache: bool = True,
    compute_prior_on_whole_steam_catalog: bool = True,
    compute_language_specific_prior: bool = False,
) -> bool:
    if not load_from_cache:
        download_steam_reviews()

    game_feature_dict, all_languages = get_input_data(load_from_cache=load_from_cache)

    games = prepare_dictionary_for_ranking_of_hidden_gems(
        steamspypi.load(),
        game_feature_dict,
        all_languages,
        compute_prior_on_whole_steam_catalog=compute_prior_on_whole_steam_catalog,
        compute_language_specific_prior=compute_language_specific_prior,
        verbose=verbose,
    )

    for language in all_languages:
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
        msg = "Language-specific prior cannot be computed on the whole catalog."
        raise AssertionError(
            msg,
        )

    run_regional_workflow(
        quality_measure_str="bayesian_rating",
        popularity_measure_str="num_owners",
        perform_optimization_at_runtime=True,
        num_top_games_to_print=50,
        verbose=False,
        keywords_to_include=None,
        keywords_to_exclude=None,
        load_from_cache=load_precomputed_review_language_stats,
        compute_prior_on_whole_steam_catalog=use_global_constant_prior,
        compute_language_specific_prior=use_language_specific_prior,
    )
