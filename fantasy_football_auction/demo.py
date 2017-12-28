"""
Some simple default values to help use this
"""

from fantasy_football_auction.auction import Auction
from fantasy_football_auction.position import RosterSlot
from fantasy_football_auction.player import players_from_fantasypros_cheatsheet


def default_roster():
    """
    :return list(RosterSlot): a list of RosterSlot that's pretty typical for a league -
        QB, RB, RB, WR, WR, WR/RB/TE, TE, K, DST, BN, BN, BN, BN, BN, BN
    """
    return [RosterSlot.QB, RosterSlot.RB, RosterSlot.RB, RosterSlot.WR, RosterSlot.WR, RosterSlot.WRRBTE,
            RosterSlot.TE, RosterSlot.K, RosterSlot.DST, RosterSlot.BN, RosterSlot.BN, RosterSlot.BN, RosterSlot.BN,
            RosterSlot.BN, RosterSlot.BN]


def default_auction(file):
    """

    :param File: file containing the cheatsheet csv from fantasypros, to use to set player values
    :return Auction: an 3 person Auction using the default roster and the specified values, $200 budget
    """
    return Auction(players_from_fantasypros_cheatsheet(file), 3, 200, default_roster())
