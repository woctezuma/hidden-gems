from dataclasses import dataclass
from typing import Optional


@dataclass
class Game:
    """A class to hold all the information for a single game."""

    appid: str
    name: str
    wilson_score: Optional[float]
    bayesian_rating: Optional[float]
    num_owners: float
    num_players: Optional[float]
    median_playtime: int
    average_playtime: int
    num_positive_reviews: int
    num_negative_reviews: int
    should_appear_in_ranking: bool = True
