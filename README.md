# hidden-gems
Ranking of Steam games to favor "hidden gems".

This repository contains the code to compute a ranking of Steam games, based on a score intended to favor "hidden gems".

A "hidden gem" is defined as a high-quality game (hence the "gem") which only got little attention (hence "hidden").

Therefore, the score of a game is defined as the product of a quality measure (its Wilson score) and a decreasing function of a popularity measure (its players total forever).

The quality measure comes from [SteamDB](https://steamdb.info/stats/gameratings/) and the popularity measure comes from [SteamSpy API](http://steamspy.com/api.php).

Finally, here is a reference to [the NeoGAF post](http://www.neogaf.com/forum/showpost.php?p=241218621&postcount=5840) explaining the method, and [the NeoGAF post](http://www.neogaf.com/forum/showpost.php?p=241224894&postcount=5869) explaining the idea behind the optimization of the only free parameter.
