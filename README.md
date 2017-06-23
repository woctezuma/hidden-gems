# Hidden Gems

This repository contains code to compute a ranking of Steam games, based on a score intended to favor "hidden gems".

Definition:
A "hidden gem" is defined as a high-quality game (hence the "gem") which only got little attention (hence "hidden").

Game scoring:
The score of a game is defined as the product of a quality measure (its Wilson score) and a decreasing function of a popularity measure (its players total forever).

Data source:
The quality measure comes from [SteamDB](https://steamdb.info/stats/gameratings/) and the popularity measure comes from [SteamSpy API](http://steamspy.com/api.php).

Original posts:
* [a NeoGAF post](http://www.neogaf.com/forum/showpost.php?p=241218621&postcount=5840) explaining the method,
* [a NeoGAF post](http://www.neogaf.com/forum/showpost.php?p=241224894&postcount=5869) explaining the idea behind the optimization of the only free parameter.
