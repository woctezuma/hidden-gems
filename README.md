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

The data is included along the code in this repository, as downloaded on October 28, 2017.

## Requirements ##

This code is written in Python 3.

[NumPy](http://www.numpy.org/) and [SciPy](https://www.scipy.org/) is required for an optimization procedure (which can be skipped if you manually input a value for the parameter `alpha`).
To install these on Windows, I suggest you download the binaries linked to the Intel® Math Kernel Library:
* [NumPy](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy)
* [SciPy](http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy)

## Usage ##
1. `create_dict_using_json.py` merges data from SteamDB and SteamSpy
2. `compute_stats.py` creates the ranking by optimizing the free parameter alpha

## Results ##
* [original ranking](https://gist.github.com/woctezuma/9cea3a93fd5cba2f1b876864a0dc8854), featured on PC Gamer, based on pre-sales data, using players total as a popularity measure.
* [updated ranking](https://gist.github.com/woctezuma/9e3005006361dbd09b7f5b416b5e6869), using data from June 30, a week after the Steam summer sales have started.
* [updated ranking with tag filtering-out](https://gist.github.com/woctezuma/ed649b5ffe4d1c3d0699ddef9bec34c9), filtering out a few tags (VR, Anime, Visual Novel, and Free To Play),
* [updated ranking with tag filtering-in](https://gist.github.com/woctezuma/b3081eff4f1e215c3deb1e1f3b707eff), constraining the ranking to the Rogue-like/lite genre (filtering in, so to say).
* [updated ranking with tag filtering-out and 80% confidence Wilson score](https://gist.github.com/woctezuma/20c4b30dce9ca82d3efa9b944ab92932), filtering out tags (VR, Anime, Visual Novel, F2P).
* [ranking of card games](https://gist.github.com/woctezuma/3ef6465180e3d28e9167bce03507b721), filtering out F2P, Early Access, etc.
* [alternative updated ranking with tag filtering-in](https://gist.github.com/woctezuma/fd2fc2b766e7e94605e4be5cf7de03ad), intended to favor hidden gems among "hidden gems", so hidden² gems.
* [updated rankings for the 2017 Halloween sale](https://gist.github.com/woctezuma/b5954f2d31989fdaf71eef53027f3cac)

## References ##
* [a NeoGAF post](http://www.neogaf.com/forum/showpost.php?p=241218621&postcount=5840) explaining the method,
* [a NeoGAF post](http://www.neogaf.com/forum/showpost.php?p=241224894&postcount=5869) explaining the idea behind the optimization of the only free parameter.
* [the PC Gamer article](http://www.pcgamer.com/this-algorithm-picks-out-steams-best-hidden-gems/) which provides nice insights regarding our approach.

