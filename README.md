# Hidden Gems

[![Build status][Build image]][Build]
[![Code coverage][Codecov image]][Codecov]
[![Code Quality][codacy image]][codacy]

This repository contains code to compute a ranking of Steam games, based on a score intended to favor "hidden gems".

![Ranking of hidden gems at Steam250](https://github.com/woctezuma/hidden-gems/wiki/img/2019_04_07_banner_hidden_gems.png)

## Definition ##

A "hidden gem" is defined as a high-quality game (hence the "gem") which only got little attention (hence "hidden").

## Game scoring ##

The score of a game is defined as the product of a quality measure (its Wilson score) and a decreasing function of a popularity measure (its players total forever).

## Regional specifity

The popularity of game genres varies wildly with geography, which leads to different appreciations of a ranking of 
hidden gems. A statistical analysis of the reviewers' language could allow to personalize rankings of hidden gems with a
better account of regional specificity. Our try at building regional rankings appears in `compute_regional_stats.py`.

## Requirements ##

- Install the latest version of [Python 3.X](https://www.python.org/downloads/).

- Install the required packages:

```bash
pip install -r requirements.txt
```

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

The most recent results are shown [on a wiki](https://github.com/woctezuma/hidden-gems/wiki).

Few past results are listed below:
* [original ranking](https://gist.github.com/woctezuma/9cea3a93fd5cba2f1b876864a0dc8854), featured on PC Gamer, based on pre-sales data, using players total as a popularity measure.
* [updated ranking](https://gist.github.com/woctezuma/9e3005006361dbd09b7f5b416b5e6869), using data from June 30, a week after the Steam summer sales have started.

## Perspectives ##

The ranking of hidden gems is favorably biased towards high-quality games which have not been translated to many languages. To be insensitive to this bias, there are [regional rankings](https://github.com/woctezuma/steam-reviews/tree/master/regional_rankings) of hidden gems. The core of the method is the same, but the data is processed differently so that both the quality and popularity measures are constrained to players who speak the same language. For the quality measure, every review is downloaded, the language tag assigned to the review is taken into account, and the review language is also assessed with an external tool to confirm that the language tag is correct. For the popularity measure, we assume that for any given game, the distribution of players and reviewers is the same with respect to languages. 

## References ##
* [a NeoGAF post](http://www.neogaf.com/forum/showpost.php?p=241218621&postcount=5840) explaining the method,
* [a NeoGAF post](http://www.neogaf.com/forum/showpost.php?p=241224894&postcount=5869) explaining the idea behind the optimization of the only free parameter.
* [the PC Gamer article](http://www.pcgamer.com/this-algorithm-picks-out-steams-best-hidden-gems/) which provides nice insights regarding our approach.
* [the Steam250 website](https://steam250.com/contributors) which updates rankings every day.
* [Steam Labs: Interactive Recommender](https://store.steampowered.com/recommender/) released by Valve on July 11, 2019.
* [my PyPI package to download Steam reviews](https://github.com/woctezuma/download-steam-reviews)
* [my original repository for regional rankings of hidden gems](https://github.com/woctezuma/steam-reviews)
* [a pre-downloaded database of Steam reviews](https://github.com/woctezuma/steam-reviews-data)

<!-- Definitions -->

  [Build]: <https://github.com/woctezuma/hidden-gems/actions>
  [Build image]: <https://github.com/woctezuma/hidden-gems/workflows/Python application/badge.svg?branch=master>

  [PyUp]: https://pyup.io/repos/github/woctezuma/hidden-gems/
  [Dependency image]: https://pyup.io/repos/github/woctezuma/hidden-gems/shield.svg
  [Python3 image]: https://pyup.io/repos/github/woctezuma/hidden-gems/python-3-shield.svg

  [Codecov]: https://codecov.io/gh/woctezuma/hidden-gems
  [Codecov image]: https://codecov.io/gh/woctezuma/hidden-gems/branch/master/graph/badge.svg

  [codacy]: https://www.codacy.com/app/woctezuma/hidden-gems
  [codacy image]: https://api.codacy.com/project/badge/Grade/78cb31aae3514de8b792760bf3fa814f

