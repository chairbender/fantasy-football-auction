# fantasy-football-auction

Python library simulating a fantasy football auction. Intended to be
used for AI, but you should be able to use this for other purposes as well. 
This task assumes that each draftable player has a specific value 
(for example, looking at the ratings from FantasyPros). 

# Usage

````
from fantasy_football_auction.auction import Auction
from fantasy_football_auction.position import RosterSlot
from fantasy_football_auction.player import players_from_fantasypros_cheatsheet

# define a roster each owner will have to fill
roster = [RosterSlot.QB, RosterSlot.RB, RosterSlot.RB, RosterSlot.WR, RosterSlot.WR, RosterSlot.WRRBTE,
            RosterSlot.TE, RosterSlot.K, RosterSlot.DST, RosterSlot.BN, RosterSlot.BN, RosterSlot.BN, RosterSlot.BN,
            RosterSlot.BN, RosterSlot.BN]

# load players from a CSV file
players = players_from_fantasypros_cheatsheet('cheatsheet.csv')

# start an auction with 3 owners, 200 dollars each, using that roster and those players
auction = Auction(players, 3, 200, roster)
````