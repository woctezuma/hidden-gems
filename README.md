# Hidden Gems [![Build status][Build image]][Build] [![Updates][Dependency image]][PyUp] [![Python 3][Python3 image]][PyUp] [![Code coverage][Codecov image]][Codecov]

  [Build]: https://travis-ci.org/woctezuma/hidden-gems
  [Build image]: https://travis-ci.org/woctezuma/hidden-gems.svg?branch=master

  [PyUp]: https://pyup.io/repos/github/woctezuma/hidden-gems/
  [Dependency image]: https://pyup.io/repos/github/woctezuma/hidden-gems/shield.svg
  [Python3 image]: https://pyup.io/repos/github/woctezuma/hidden-gems/python-3-shield.svg

  [Codecov]: https://codecov.io/gh/woctezuma/hidden-gems
  [Codecov image]: https://codecov.io/gh/woctezuma/hidden-gems/branch/master/graph/badge.svg

This repository contains code to compute a ranking of Steam games, based on a score intended to favor "hidden gems".

## Definition ##

A "hidden gem" is defined as a high-quality game (hence the "gem") which only got little attention (hence "hidden").

## Game scoring ##

The score of a game is defined as the product of a quality measure (its Wilson score) and a decreasing function of a popularity measure (its players total forever).

## Requirements ##

- Install the latest version of [Python 3.X](https://www.python.org/downloads/).

- Install the required packages:

```bash
pip install -r requirements.txt
```

- In case you wanted to manually install [NumPy](http://www.numpy.org/) and [SciPy](https://www.scipy.org/) on Windows, 
you could also download these binaries linked to the Intel® Math Kernel Library:
* [NumPy](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy)
* [SciPy](http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy)

## Usage ##

- First, call the Python script `create_dict_using_json.py`, which will download data through [SteamSpy API](https://steamspy.com/api.php).
A file ending with `_steamspy.json` will be automatically created at runtime if the file is missing for the current day.

```bash
python create_dict_using_json.py
```

- Then, call the Python script `compute_stats.py` to build the ranking by optimizing the free parameter alpha.

```bash
python compute_stats.py
```

- Finally, call the Python script `compute_regional_stats.py` to build regional rankings, one per language. In order to 
estimate the number of players in each region, Steam reviews have to be downloaded through Steam API. Depending on the 
number of hidden gems displayed in the global ranking, and depending on the number of reviews for each hidden gem, this
process may require a decent amount of time. 

```bash
python compute_regional_stats.py
```

## Results ##

The most recent results are shown [on a wiki](https://github.com/woctezuma/Steam-Bayesian-Average/wiki).

Few past results are listed below:
* [original ranking](https://gist.github.com/woctezuma/9cea3a93fd5cba2f1b876864a0dc8854), featured on PC Gamer, based on pre-sales data, using players total as a popularity measure.
* [updated ranking](https://gist.github.com/woctezuma/9e3005006361dbd09b7f5b416b5e6869), using data from June 30, a week after the Steam summer sales have started.
* [updated ranking with tag filtering-out](https://gist.github.com/woctezuma/ed649b5ffe4d1c3d0699ddef9bec34c9), filtering out a few tags (VR, Anime, Visual Novel, and Free To Play),
* [updated ranking with tag filtering-in](https://gist.github.com/woctezuma/b3081eff4f1e215c3deb1e1f3b707eff), constraining the ranking to the Rogue-like/lite genre (filtering in, so to say).
* [updated ranking with tag filtering-out and 80% confidence Wilson score](https://gist.github.com/woctezuma/20c4b30dce9ca82d3efa9b944ab92932), filtering out tags (VR, Anime, Visual Novel, F2P).
* [ranking of card games](https://gist.github.com/woctezuma/3ef6465180e3d28e9167bce03507b721), filtering out F2P, Early Access, etc.
* [alternative updated ranking with tag filtering-in](https://gist.github.com/woctezuma/fd2fc2b766e7e94605e4be5cf7de03ad), intended to favor hidden gems among "hidden gems", so hidden² gems,
* [updated rankings for the 2017 Halloween sale](https://gist.github.com/woctezuma/b5954f2d31989fdaf71eef53027f3cac).

## Perspectives ##

The ranking of hidden gems is favorably biased towards high-quality games which have not been translated to many languages. To be insensitive to this bias, there are [regional rankings](https://github.com/woctezuma/steam-reviews/tree/master/regional_rankings) of hidden gems. The core of the method is the same, but the data is processed differently so that both the quality and popularity measures are constrained to players who speak the same language. For the quality measure, every review is downloaded, the language tag assigned to the review is taken into account, and the review language is also assessed with an external tool to confirm that the language tag is correct. For the popularity measure, we assume that for any given game, the distribution of players and reviewers is the same with respect to languages. 

## References ##
* [a NeoGAF post](http://www.neogaf.com/forum/showpost.php?p=241218621&postcount=5840) explaining the method,
* [a NeoGAF post](http://www.neogaf.com/forum/showpost.php?p=241224894&postcount=5869) explaining the idea behind the optimization of the only free parameter.
* [the PC Gamer article](http://www.pcgamer.com/this-algorithm-picks-out-steams-best-hidden-gems/) which provides nice insights regarding our approach.
* [my PyPI package to download Steam reviews](https://github.com/woctezuma/download-steam-reviews)
* [my original repository for regional rankings of hidden gems](https://github.com/woctezuma/steam-reviews)
* [a pre-downloaded database of Steam reviews](https://github.com/woctezuma/steam-reviews-data)
