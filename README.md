# Hidden Gems

This repository contains code to compute a ranking of Steam games, based on a score intended to favor "hidden gems".

Definition:

A "hidden gem" is defined as a high-quality game (hence the "gem") which only got little attention (hence "hidden").

Game scoring:

The score of a game is defined as the product of a quality measure (its Wilson score) and a decreasing function of a popularity measure (its players total forever).

Data source:

The quality measure comes from [SteamDB](https://steamdb.info/stats/gameratings/) and the popularity measure comes from [SteamSpy API](http://steamspy.com/api.php).

Usage:
i)  create_dict_using_json.py merges data from SteamDB and SteamSpy
ii) compute_stats.py creates the ranking by optimizing the free parameter alpha

Results:
* [ranking](https://gist.github.com/woctezuma/9cea3a93fd5cba2f1b876864a0dc8854), using players total (forever) as a popularity measure,
* [ranking](https://gist.github.com/woctezuma/b14187941c95114a769556fa052bfefc), using median playtime (forever) as a popularity measure.

References:
* [a NeoGAF post](http://www.neogaf.com/forum/showpost.php?p=241218621&postcount=5840) explaining the method,
* [a NeoGAF post](http://www.neogaf.com/forum/showpost.php?p=241224894&postcount=5869) explaining the idea behind the optimization of the only free parameter.
