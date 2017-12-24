from unittest import TestCase, main

from fantasy_football_auction.auction import Owner, InsufficientFundsError, NoValidRosterSlotError, \
    AlreadyPurchasedError
from fantasy_football_auction.player import Player
from fantasy_football_auction.position import RosterSlot, Position


class OwnerSlotTestCase(TestCase):

    def test_buy_error(self):
        owner = Owner(20, [RosterSlot.QB, RosterSlot.QB, RosterSlot.TE], 0)
        playerQB = Player("blahQB", Position.QB, 1)
        playerTE = Player("blahTE", Position.TE, 1)
        playerWR = Player("blahWR", Position.WR, 1)

        with self.assertRaises(InsufficientFundsError):
            owner.buy(playerQB, 21)

        with self.assertRaises(NoValidRosterSlotError):
            owner.buy(playerWR, 3)

        with self.assertRaises(NoValidRosterSlotError):
            owner.buy(playerTE, 3)
            owner.buy(playerTE, 3)

        with self.assertRaises(AlreadyPurchasedError):
            owner.buy(playerQB, 3)
            playerQBDupe = Player("blahQB", Position.QB, 1)
            owner.buy(playerQBDupe, 3)

        owner = Owner(20, [RosterSlot.QB, RosterSlot.TE], 0)
        with self.assertRaises(InsufficientFundsError):
            owner.buy(playerQB, 10)
            owner.buy(playerTE, 11)


