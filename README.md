# Hidden Gems

This repository contains code to compute a ranking of Steam games, based on a score intended to favor "hidden gems".

## Definition ##

A "hidden gem" is defined as a high-quality game (hence the "gem") which only got little attention (hence "hidden").

## Game scoring ##

The score of a game is defined as the product of a quality measure (its Wilson score) and a decreasing function of a popularity measure (its players total forever).

## Data source ##

The quality measure comes from [SteamDB](https://steamdb.info/stats/gameratings/) and the popularity measure comes from [SteamSpy API](http://steamspy.com/api.php).

To run the code, you will need:
* data from SteamDB: `top_rated_games_on_steam.txt` (manually pasted)
* data from SteamSpy: `steamspy.json` (automatically downloaded if the file is missing)
The data is included along the code in this repository, as downloaded on June 30th. 

## Requirements ##

This code is written in Python 3.

[SciPy](https://www.scipy.org/) is required for an optimization procedure (which can be skipped if you manually input a value for the parameter `alpha`).
To install SciPy on Windows, I suggest you download the binaries linked to the Intel® Math Kernel Library:
* [NumPy](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy)
* [SciPy](http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy).

## Usage ##
1. `create_dict_using_json.py` merges data from SteamDB and SteamSpy
2. `compute_stats.py` creates the ranking by optimizing the free parameter alpha

## Results ##
* [ranking](https://gist.github.com/woctezuma/9cea3a93fd5cba2f1b876864a0dc8854), using players total (forever) as a popularity measure.
* [updated ranking](https://gist.github.com/woctezuma/9e3005006361dbd09b7f5b416b5e6869), a week after the Steam summer sales have started.
* [updated ranking with tag filtering](https://gist.github.com/woctezuma/ed649b5ffe4d1c3d0699ddef9bec34c9), a week after the Steam summer sales have started, and filtering out a few tags (VR, Anime, Visual Novel, and Free To Play).

NB: I have computed the ranking based on playtime as well, but it does not seem like a good popularity measure a posteriori. Typically, it could be skewed by people idling for trading cards, plus the time to finish a game can differ widely between games.

## References ##
* [a NeoGAF post](http://www.neogaf.com/forum/showpost.php?p=241218621&postcount=5840) explaining the method,
* [a NeoGAF post](http://www.neogaf.com/forum/showpost.php?p=241224894&postcount=5869) explaining the idea behind the optimization of the only free parameter.
