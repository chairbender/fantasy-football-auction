from unittest import TestCase, main

from fantasy_football_auction.auction import Owner, InsufficientFundsError, NoValidRosterSlotError, \
    AlreadyPurchasedError
from fantasy_football_auction.player import Player
from fantasy_football_auction.position import RosterSlot, Position


class OwnerSlotTestCase(TestCase):

    def test_buy_error(self):
        owner = Owner(20, [RosterSlot.QB, RosterSlot.QB, RosterSlot.TE], 0)
        player_qb = Player("blahQB", Position.QB, 1)
        player_te = Player("blahTE", Position.TE, 1)
        player_wr = Player("blahWR", Position.WR, 1)

        with self.assertRaises(InsufficientFundsError):
            owner.buy(player_qb, 21)

        with self.assertRaises(NoValidRosterSlotError):
            owner.buy(player_wr, 3)

        with self.assertRaises(NoValidRosterSlotError):
            owner.buy(player_te, 3)
            owner.buy(player_te, 3)

        with self.assertRaises(AlreadyPurchasedError):
            owner.buy(player_qb, 3)
            playerQBDupe = Player("blahQB", Position.QB, 1)
            owner.buy(playerQBDupe, 3)

        owner = Owner(20, [RosterSlot.QB, RosterSlot.TE], 0)
        with self.assertRaises(InsufficientFundsError):
            owner.buy(player_qb, 10)
            owner.buy(player_te, 11)

    def test_buy(self):
        owner = Owner(20, [RosterSlot.QB, RosterSlot.QB, RosterSlot.TE], 0)
        player_qb = Player("blahQB", Position.QB, 1)
        player_qb2 = Player("blahQB2", Position.QB, 1)
        player_te = Player("blahTE", Position.TE, 1)

        owner.buy(player_qb, 5)

        self.assertEqual(15, owner.money)
        purchase_qb = owner.purchases[0]
        self.assertEqual(player_qb, purchase_qb.player)
        self.assertEqual(5, purchase_qb.cost)
        self.assertEqual(RosterSlot.QB, purchase_qb.roster_slot)

        self.assertTrue(RosterSlot.QB in owner.roster)
        owner.buy(player_qb2, 5)
        self.assertTrue(RosterSlot.QB not in owner.roster)
        self.assertEqual(10, owner.money)

        self.assertTrue(RosterSlot.TE in owner.roster)
        owner.buy(player_te, 5)
        self.assertTrue(RosterSlot.TE not in owner.roster)
        self.assertEqual(5, owner.money)

