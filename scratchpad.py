"""
Just holds stuff being used for developer testing
"""

from fantasy_football_auction.demo import default_auction

a = default_auction("cheatsheet.csv")

a.nominate(0, 0, 10)
a.tick()
a.place_bid(1, 11)
a.place_bid(2, 12)
a.tick()
a.tick()
