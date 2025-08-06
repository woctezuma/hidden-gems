from dataclasses import dataclass


@dataclass
class Game:
    """A class to hold all the information for a single game."""

    appid: str
    name: str
    wilson_score: float | None
    bayesian_rating: float | None
    num_owners: float
    num_players: float | None
    median_playtime: int
    average_playtime: int
    num_positive_reviews: int
    num_negative_reviews: int
    should_appear_in_ranking: bool = True
