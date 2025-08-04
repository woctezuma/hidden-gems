import unittest
from pathlib import Path

import compute_regional_stats
import compute_stats
import create_dict_using_json
from src import appids, compute_bayesian_rating, compute_wilson_score


class TestAppidsMethods(unittest.TestCase):
    def test_main(self) -> None:
        assert appids.main()


class TestComputeWilsonScoreMethods(unittest.TestCase):
    def test_compute_wilson_score(self) -> None:
        wilson_score_value = compute_wilson_score.compute_wilson_score(
            num_pos=90,
            num_neg=10,
            confidence=0.975,
        )
        assert wilson_score_value > 0

    def test_main(self) -> None:
        assert compute_wilson_score.main()


class TestComputeBayesianRatingMethods(unittest.TestCase):
    def test_choose_prior(self) -> None:
        observations = {
            "Blockbuster": {"score": 0.85, "num_votes": 1000},
            "Average game": {"score": 0.75, "num_votes": 100},
            "Hidden gem": {"score": 0.95, "num_votes": 10},
        }
        bayes_prior = compute_bayesian_rating.choose_prior(observations, verbose=True)
        self.assertDictEqual(bayes_prior, {"score": 0.85, "num_votes": 100})

    def test_main(self) -> None:
        assert compute_bayesian_rating.main()


class TestCreateDictUsingJsonMethods(unittest.TestCase):
    def test_main(self) -> None:
        assert create_dict_using_json.main()


class TestComputeRegionalStatsMethods(unittest.TestCase):
    def test_run_regional_workflow_wilson_reviews(self) -> None:
        quality_measure_str = (
            "wilson_score"  # Either 'wilson_score' or 'bayesian_rating'
        )
        popularity_measure_str = "num_reviews"  # Either 'num_reviews' or 'num_owners'

        assert compute_regional_stats.run_regional_workflow(
            quality_measure_str=quality_measure_str,
            popularity_measure_str=popularity_measure_str,
            num_top_games_to_print=50,
            keywords_to_include=None,
            keywords_to_exclude=None,
            perform_optimization_at_runtime=True,
            verbose=False,
            load_from_cache=True,
            compute_prior_on_whole_steam_catalog=False,
            compute_language_specific_prior=False,
        )

    def test_run_regional_workflow_wilson_owners(self) -> None:
        quality_measure_str = (
            "wilson_score"  # Either 'wilson_score' or 'bayesian_rating'
        )
        popularity_measure_str = "num_owners"  # Either 'num_reviews' or 'num_owners'

        assert compute_regional_stats.run_regional_workflow(
            quality_measure_str=quality_measure_str,
            popularity_measure_str=popularity_measure_str,
            num_top_games_to_print=50,
            keywords_to_include=None,
            keywords_to_exclude=None,
            perform_optimization_at_runtime=True,
            verbose=False,
            load_from_cache=True,
            compute_prior_on_whole_steam_catalog=False,
            compute_language_specific_prior=False,
        )

    def test_run_regional_workflow_bayes_reviews(self) -> None:
        quality_measure_str = (
            "bayesian_rating"  # Either 'wilson_score' or 'bayesian_rating'
        )
        popularity_measure_str = "num_reviews"  # Either 'num_reviews' or 'num_owners'

        assert compute_regional_stats.run_regional_workflow(
            quality_measure_str=quality_measure_str,
            popularity_measure_str=popularity_measure_str,
            num_top_games_to_print=50,
            keywords_to_include=None,
            keywords_to_exclude=None,
            perform_optimization_at_runtime=True,
            verbose=False,
            load_from_cache=True,
            compute_prior_on_whole_steam_catalog=False,
            compute_language_specific_prior=True,
        )

    def test_run_regional_workflow_bayes_owners(self) -> None:
        quality_measure_str = (
            "bayesian_rating"  # Either 'wilson_score' or 'bayesian_rating'
        )
        popularity_measure_str = "num_owners"  # Either 'num_reviews' or 'num_owners'

        assert compute_regional_stats.run_regional_workflow(
            quality_measure_str=quality_measure_str,
            popularity_measure_str=popularity_measure_str,
            num_top_games_to_print=50,
            keywords_to_include=None,
            keywords_to_exclude=None,
            perform_optimization_at_runtime=True,
            verbose=True,
            load_from_cache=True,
            compute_prior_on_whole_steam_catalog=False,
            compute_language_specific_prior=True,
        )

    def test_run_regional_workflow_bayes_reviews_with_hidden_gem_constant_prior(
        self,
    ) -> None:
        quality_measure_str = (
            "bayesian_rating"  # Either 'wilson_score' or 'bayesian_rating'
        )
        popularity_measure_str = "num_reviews"  # Either 'num_reviews' or 'num_owners'

        assert compute_regional_stats.run_regional_workflow(
            quality_measure_str=quality_measure_str,
            popularity_measure_str=popularity_measure_str,
            num_top_games_to_print=50,
            keywords_to_include=None,
            keywords_to_exclude=None,
            perform_optimization_at_runtime=True,
            verbose=False,
            load_from_cache=True,
            compute_prior_on_whole_steam_catalog=False,
            compute_language_specific_prior=False,
        )

    def test_run_regional_workflow_bayes_owners_with_hidden_gem_constant_prior(
        self,
    ) -> None:
        quality_measure_str = (
            "bayesian_rating"  # Either 'wilson_score' or 'bayesian_rating'
        )
        popularity_measure_str = "num_owners"  # Either 'num_reviews' or 'num_owners'

        assert compute_regional_stats.run_regional_workflow(
            quality_measure_str=quality_measure_str,
            popularity_measure_str=popularity_measure_str,
            num_top_games_to_print=50,
            keywords_to_include=None,
            keywords_to_exclude=None,
            perform_optimization_at_runtime=True,
            verbose=True,
            load_from_cache=True,
            compute_prior_on_whole_steam_catalog=False,
            compute_language_specific_prior=False,
        )

    def test_run_regional_workflow_bayes_reviews_with_global_constant_prior(
        self,
    ) -> None:
        quality_measure_str = (
            "bayesian_rating"  # Either 'wilson_score' or 'bayesian_rating'
        )
        popularity_measure_str = "num_reviews"  # Either 'num_reviews' or 'num_owners'

        assert compute_regional_stats.run_regional_workflow(
            quality_measure_str=quality_measure_str,
            popularity_measure_str=popularity_measure_str,
            num_top_games_to_print=50,
            keywords_to_include=None,
            keywords_to_exclude=None,
            perform_optimization_at_runtime=True,
            verbose=False,
            load_from_cache=True,
            compute_prior_on_whole_steam_catalog=True,
            compute_language_specific_prior=False,
        )

    def test_run_regional_workflow_bayes_owners_with_global_constant_prior(
        self,
    ) -> None:
        quality_measure_str = (
            "bayesian_rating"  # Either 'wilson_score' or 'bayesian_rating'
        )
        popularity_measure_str = "num_owners"  # Either 'num_reviews' or 'num_owners'

        assert compute_regional_stats.run_regional_workflow(
            quality_measure_str=quality_measure_str,
            popularity_measure_str=popularity_measure_str,
            num_top_games_to_print=50,
            keywords_to_include=None,
            keywords_to_exclude=None,
            perform_optimization_at_runtime=True,
            verbose=True,
            load_from_cache=True,
            compute_prior_on_whole_steam_catalog=True,
            compute_language_specific_prior=False,
        )


class TestComputeStatsMethods(unittest.TestCase):
    def test_run_workflow_wilson_reviews(self) -> None:
        create_dict_using_json.main()

        assert compute_stats.run_workflow(
            quality_measure_str="wilson_score",
            popularity_measure_str="num_reviews",
            perform_optimization_at_runtime=False,
            num_top_games_to_print=50,
            verbose=True,
        )

    def test_run_workflow_wilson_owners(self) -> None:
        create_dict_using_json.main()

        assert compute_stats.run_workflow(
            quality_measure_str="wilson_score",
            popularity_measure_str="num_owners",
            perform_optimization_at_runtime=False,
            num_top_games_to_print=50,
            verbose=True,
        )

    def test_run_workflow_bayes_reviews(self) -> None:
        create_dict_using_json.main()

        assert compute_stats.run_workflow(
            quality_measure_str="bayesian_rating",
            popularity_measure_str="num_reviews",
            perform_optimization_at_runtime=False,
            num_top_games_to_print=50,
            verbose=True,
        )

    def test_run_workflow_bayes_owners(self) -> None:
        create_dict_using_json.main()

        assert compute_stats.run_workflow(
            quality_measure_str="bayesian_rating",
            popularity_measure_str="num_owners",
            perform_optimization_at_runtime=False,
            num_top_games_to_print=50,
            verbose=True,
        )

    def test_run_workflow_filtering_in(self) -> None:
        create_dict_using_json.main()

        assert compute_stats.run_workflow(
            quality_measure_str="wilson_score",
            popularity_measure_str="num_reviews",
            perform_optimization_at_runtime=False,
            num_top_games_to_print=50,
            verbose=True,
            language=None,
            keywords_to_include=["Early Access", "Free To Play"],
            keywords_to_exclude=None,
        )

    def test_run_workflow_while_removing_reference_hidden_gems(self) -> None:
        create_dict_using_json.main()

        # A dictionary will be stored in the following text file
        dict_filename = "dict_top_rated_games_on_steam.txt"

        d = compute_stats.load_dict_top_rated_games(dict_filename)

        for appid in appids.appid_hidden_gems_reference_set:
            print(
                f"Ensuring reference {d[appid][0]} (appID={appid}) does not appear in the final ranking.",
            )
            d[appid][-1] = False
            # If True, UnEpic should end up about rank 1828. Otherwise, UnEpic should not appear on there.

        # Save the dictionary to a text file
        with Path(dict_filename).open("w", encoding="utf8") as outfile:
            print(create_dict_using_json.get_leading_comment(), file=outfile)
            print(d, file=outfile)

        assert compute_stats.run_workflow(
            quality_measure_str="wilson_score",
            popularity_measure_str="num_reviews",
            perform_optimization_at_runtime=False,
            num_top_games_to_print=2000,
            verbose=True,
            language=None,
            keywords_to_include=["Action", "Indie", "RPG"],
            keywords_to_exclude=None,
        )

    def test_run_workflow_filtering_in_unknown_tag(self) -> None:
        create_dict_using_json.main()

        assert compute_stats.run_workflow(
            quality_measure_str="wilson_score",
            popularity_measure_str="num_reviews",
            perform_optimization_at_runtime=False,
            num_top_games_to_print=50,
            verbose=False,
            language=None,
            keywords_to_include=["Rogue-Like"],
            keywords_to_exclude=None,
        )

    def test_run_workflow_filtering_out(self) -> None:
        create_dict_using_json.main()

        assert compute_stats.run_workflow(
            quality_measure_str="wilson_score",
            popularity_measure_str="num_reviews",
            perform_optimization_at_runtime=False,
            num_top_games_to_print=50,
            verbose=False,
            language=None,
            keywords_to_include=None,
            keywords_to_exclude=["Visual Novel", "Anime"],
        )

    def test_run_workflow_wilson_owners_optimized_at_runtime(self) -> None:
        create_dict_using_json.main()

        assert compute_stats.run_workflow(
            quality_measure_str="wilson_score",
            popularity_measure_str="num_owners",
            perform_optimization_at_runtime=True,
            num_top_games_to_print=50,
            verbose=False,
        )

    def test_main(self) -> None:
        create_dict_using_json.main()

        assert compute_stats.main()


if __name__ == "__main__":
    unittest.main()
