from math import sqrt

# Quantiles of the normal distribution
# Reference: https://en.wikipedia.org/wiki/Normal_distribution
quantile_normal_dist_dict = {
    0.80        :   1.281551565545,
    0.90        :	1.644853626951,
    0.95        :	1.959963984540,
    0.98        :	2.326347874041,
    0.99        :	2.575829303549,
    0.995       :	2.807033768344,
    0.998       :	3.090232306168,
    0.999 	    :   3.290526731492,
    0.9999 	    :   3.890591886413,
    0.99999 	:   4.417173413469,
    0.999999 	:   4.891638475699,
    0.9999999 	:   5.326723886384,
    0.99999999 	:   5.730728868236,
    0.999999999 :	6.109410204869
}

def computeWilsonScore(num_pos, num_neg, confidence=0.95):
    # Reference: https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval#Wilson_score_interval

    if confidence in quantile_normal_dist_dict.keys():
        tabulated_confidence = confidence
    else:
        tabulated_confidence_list = list(quantile_normal_dist_dict.keys())
        sorted(tabulated_confidence_list)
        diff_list = [(c-confidence) for c in tabulated_confidence_list]
        index = min(i for i in range(len(diff_list)) if diff_list[i]>=0)
        tabulated_confidence = tabulated_confidence_list[index]
        print(tabulated_confidence)

    z_quantile = quantile_normal_dist_dict[tabulated_confidence]

    z2 = pow(z_quantile, 2)
    den = num_pos + num_neg + z2

    mean = (num_pos + z2/2) / den

    inside_sqrt = num_pos*num_neg/(num_pos+num_neg) + z2/4
    delta = (z_quantile * sqrt(inside_sqrt)) / den

    wilson_score = mean - delta
    return wilson_score

if __name__ == "__main__":
    # Loop over the number of reviews
    for num_reviews in [pow(10, n) for n in range(5)]:
        # Display the Wilson score of a game with as many positive and negative reviews
        wilson_score = computeWilsonScore(num_reviews/2, num_reviews/2, 0.95)
        print("#reviews = " + str(num_reviews) + "\tWilson score = " + str(wilson_score))
