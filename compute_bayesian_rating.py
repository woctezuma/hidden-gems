# Objective: choose a prior and compute a Bayesian rating

import numpy as np


def choose_prior(observations, verbose=False):
    bayes_prior = {}

    scores = [
        game_entry["score"]
        for game_entry in observations.values()
        if game_entry["score"] is not None
    ]
    votes = [
        game_entry["num_votes"]
        for game_entry in observations.values()
        if game_entry["num_votes"] is not None
    ]

    # Data visualization to help choose a good prior
    if verbose:
        import matplotlib as mpl

        # For Travis integration:
        mpl.use("Agg")

        import matplotlib.pyplot as plt

        score_max = np.max(scores)
        vote_max = np.max(votes)

        print("Highest average score:")
        print(
            [
                game_name
                for game_name in observations
                if observations[game_name]["score"] >= score_max
            ],
        )

        print("Highest number of votes:")
        print(
            [
                game_name
                for game_name in observations
                if observations[game_name]["num_votes"] >= vote_max
            ],
        )

        plt.figure()
        plt.scatter(scores, votes)
        plt.xlabel("Average Score")
        plt.ylabel("Number of votes")
        plt.show()

    # TODO: Important choices below. How do you choose a good prior? Median? Average?
    bayes_prior["score"] = np.average(scores)
    bayes_prior["num_votes"] = np.median(votes)

    return bayes_prior


def compute_bayesian_score(game_entry, bayes_prior):
    bayesian_score = (
        bayes_prior["num_votes"] * bayes_prior["score"]
        + game_entry["num_votes"] * game_entry["score"]
    ) / (bayes_prior["num_votes"] + game_entry["num_votes"])

    return bayesian_score


def main():
    prior = {}
    prior["score"] = 0.7
    prior["num_votes"] = pow(10, 3)

    # Loop over the number of reviews
    for num_reviews in [pow(10, n) for n in range(5)]:
        # Display the Bayesian rating of a game with as many positive and negative reviews
        game = {}
        game["score"] = 0.5
        game["num_votes"] = num_reviews

        bayesian_rating = compute_bayesian_score(game, prior)
        print(
            "#reviews = {:6} \t Bayesian rating = {:.4f}".format(
                num_reviews,
                bayesian_rating,
            ),
        )

    return True


if __name__ == "__main__":
    main()
