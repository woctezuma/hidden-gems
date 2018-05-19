import unittest

import appids
import compute_bayesian_rating
import compute_stats
import compute_wilson_score
import create_dict_using_json
import download_json


class TestAppidsMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(appids.main())


class TestDownloadJsonMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(download_json.main())


class TestComputeWilsonScoreMethods(unittest.TestCase):

    def test_compute_wilson_score(self):
        wilson_score_value = compute_wilson_score.compute_wilson_score(num_pos=90, num_neg=10, confidence=0.975)
        self.assertGreater(wilson_score_value, 0)

    def test_main(self):
        self.assertTrue(compute_wilson_score.main())


class TestComputeBayesianRatingMethods(unittest.TestCase):

    def test_choose_prior(self):
        observations = {'Blockbuster': {'score': 0.85, 'num_votes': 1000},
                        'Average game': {'score': 0.75, 'num_votes': 100},
                        'Hidden gem': {'score': 0.95, 'num_votes': 10}}
        bayes_prior = compute_bayesian_rating.choose_prior(observations, verbose=True)
        self.assertDictEqual(bayes_prior, {'score': 0.85, 'num_votes': 100})

    def test_main(self):
        self.assertTrue(compute_bayesian_rating.main())


class TestCreateDictUsingJsonMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(create_dict_using_json.main())


class TestComputeStatsMethods(unittest.TestCase):

    def test_run_workflow_wilson_reviews(self):
        create_dict_using_json.main()

        self.assertTrue(compute_stats.run_workflow(quality_measure_str='wilson_score',
                                                   popularity_measure_str='num_reviews',
                                                   perform_optimization_at_runtime=False,
                                                   num_top_games_to_print=50))

    def test_run_workflow_wilson_owners(self):
        create_dict_using_json.main()

        self.assertTrue(compute_stats.run_workflow(quality_measure_str='wilson_score',
                                                   popularity_measure_str='num_owners',
                                                   perform_optimization_at_runtime=False,
                                                   num_top_games_to_print=50))

    def test_run_workflow_bayes_reviews(self):
        create_dict_using_json.main()

        self.assertTrue(compute_stats.run_workflow(quality_measure_str='bayesian_rating',
                                                   popularity_measure_str='num_reviews',
                                                   perform_optimization_at_runtime=False,
                                                   num_top_games_to_print=50))

    def test_run_workflow_bayes_owners(self):
        create_dict_using_json.main()

        self.assertTrue(compute_stats.run_workflow(quality_measure_str='bayesian_rating',
                                                   popularity_measure_str='num_owners',
                                                   perform_optimization_at_runtime=False,
                                                   num_top_games_to_print=50))

    # TODO
    # def test_run_workflow_language(self):
    #     create_dict_using_json.main()
    #
    #     self.assertTrue(compute_stats.run_workflow(quality_measure_str='wilson_score',
    #                                                popularity_measure_str='num_reviews',
    #                                                perform_optimization_at_runtime=False,
    #                                                num_top_games_to_print=50,
    #                                                language='french'))

    def test_run_workflow_filtering_in(self):
        create_dict_using_json.main()

        self.assertTrue(compute_stats.run_workflow(quality_measure_str='wilson_score',
                                                   popularity_measure_str='num_reviews',
                                                   perform_optimization_at_runtime=False,
                                                   num_top_games_to_print=50,
                                                   language=None,
                                                   keywords_to_include=["Early Access", "Free To Play"],
                                                   keywords_to_exclude=None))

    def test_run_workflow_filtering_in_unknown_tag(self):
        create_dict_using_json.main()

        self.assertTrue(compute_stats.run_workflow(quality_measure_str='wilson_score',
                                                   popularity_measure_str='num_reviews',
                                                   perform_optimization_at_runtime=False,
                                                   num_top_games_to_print=50,
                                                   language=None,
                                                   keywords_to_include=["Rogue-Like"],
                                                   keywords_to_exclude=None))

    def test_run_workflow_filtering_out(self):
        create_dict_using_json.main()

        self.assertTrue(compute_stats.run_workflow(quality_measure_str='wilson_score',
                                                   popularity_measure_str='num_reviews',
                                                   perform_optimization_at_runtime=False,
                                                   num_top_games_to_print=50,
                                                   language=None,
                                                   keywords_to_include=None,
                                                   keywords_to_exclude=["Visual Novel", "Anime"]))

    def test_main(self):
        create_dict_using_json.main()

        self.assertTrue(compute_stats.main())


if __name__ == '__main__':
    unittest.main()
