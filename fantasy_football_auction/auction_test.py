from unittest import TestCase, main

from fantasy_football_auction.auction import Owner, InsufficientFundsError, NoValidRosterSlotError, \
    AlreadyPurchasedError
from fantasy_football_auction.player import Player
from fantasy_football_auction.position import RosterSlot, Position


class OwnerTestCase(TestCase):

    def test_buy_error(self):
        owner = Owner(20, [RosterSlot.QB, RosterSlot.QB, RosterSlot.TE], 0)
        player_qb = Player("blahQB", Position.QB, 1)
        player_te = Player("blahTE", Position.TE, 1)
        player_te2 = Player("blahTE2", Position.TE, 2)
        player_wr = Player("blahWR", Position.WR, 1)

        with self.assertRaises(InsufficientFundsError):
            owner.buy(player_qb, 21)

        with self.assertRaises(NoValidRosterSlotError):
            owner.buy(player_wr, 3)

        with self.assertRaises(NoValidRosterSlotError):
            owner.buy(player_te, 3)
            owner.buy(player_te2, 3)

        with self.assertRaises(AlreadyPurchasedError):
            owner.buy(player_qb, 3)
            playerQBDupe = Player("blahQB", Position.QB, 1)
            owner.buy(playerQBDupe, 3)

        owner = Owner(20, [RosterSlot.QB, RosterSlot.TE], 0)
        with self.assertRaises(InsufficientFundsError):
            owner.buy(player_qb, 10)
            owner.buy(player_te, 11)

    def test_buy(self):
        owner = Owner(20, [RosterSlot.WR, RosterSlot.WRRBTE, RosterSlot.BN], 0)
        player_wr = Player("blahWR", Position.WR, 1)
        player_wr2 = Player("blahWR2", Position.WR, 2)
        player_te = Player("blahTE", Position.TE, 3)

        owner.buy(player_wr, 5)

        self.assertEqual(15, owner.money)
        self.assertEqual(player_wr, owner.roster[0].occupant)

        owner.buy(player_wr2, 5)
        # higher value WR should replace the existing qb
        self.assertEqual(player_wr2, owner.roster[0].occupant)
        self.assertEqual(player_wr, owner.roster[1].occupant)
        self.assertEqual(10, owner.money)

        owner.buy(player_te, 5)
        self.assertEqual(5, owner.money)
        # this should displace the WRRBTE slot, leaving the low-value wr in the bench slot
        self.assertEqual(player_wr2, owner.roster[0].occupant)
        self.assertEqual(player_te, owner.roster[1].occupant)
        self.assertEqual(player_wr, owner.roster[2].occupant)
        self.assertEqual(5, owner.money)

        # we should still get the same outcome even if we do it in a different order
        owner = Owner(20, [RosterSlot.WR, RosterSlot.WRRBTE, RosterSlot.BN], 0)
        owner.buy(player_te, 5)
        owner.buy(player_wr2, 5)
        owner.buy(player_wr, 5)
        self.assertEqual(player_wr2, owner.roster[0].occupant)
        self.assertEqual(player_te, owner.roster[1].occupant)
        self.assertEqual(player_wr, owner.roster[2].occupant)
        self.assertEqual(5, owner.money)

    def test_can_buy(self):
        owner = Owner(20, [RosterSlot.QB, RosterSlot.QB, RosterSlot.TE], 0)
        player_qb = Player("blahQB", Position.QB, 1)
        player_te = Player("blahTE", Position.TE, 1)
        player_wr = Player("blahWR", Position.WR, 1)

        self.assertFalse(owner.can_buy(player_qb, 21))

        self.assertFalse(owner.can_buy(player_wr, 3))

        owner.buy(player_te, 3)
        self.assertFalse(owner.can_buy(player_te, 3))

        owner.buy(player_qb, 3)
        playerQBDupe = Player("blahQB", Position.QB, 1)
        self.assertFalse(owner.can_buy(playerQBDupe, 1))

        owner = Owner(20, [RosterSlot.QB, RosterSlot.TE], 0)
        owner.buy(player_qb, 10)
        self.assertFalse(owner.can_buy(player_te, 11))

    def test_max_bid(self):
        owner = Owner(20, [RosterSlot.QB, RosterSlot.QB, RosterSlot.TE], 0)
        player_qb = Player("blahQB", Position.QB, 1)
        player_qb2 = Player("blahQB2", Position.QB, 1)

        self.assertEqual(18, owner.max_bid())

        owner.buy(player_qb, 5)
        self.assertEqual(14, owner.max_bid())

        owner.buy(player_qb2, 5)
        self.assertEqual(10, owner.max_bid())

    def test_scoring_value(self):
        owner = Owner(20, [RosterSlot.WR, RosterSlot.WRRBTE, RosterSlot.BN], 0)
        player_wr = Player("blahWR", Position.WR, 1)
        player_wr2 = Player("blahWR2", Position.WR, 2)
        player_te = Player("blahTE", Position.TE, 3)
        owner.buy(player_te, 5)
        owner.buy(player_wr2, 5)
        owner.buy(player_wr, 5)

        self.assertAlmostEqual(5, owner.start_value())
        self.assertAlmostEqual(1, owner.bench_value())
        self.assertAlmostEqual(3, owner.score(.5))

        owner = Owner(20, [RosterSlot.WR, RosterSlot.WRRBTE, RosterSlot.BN], 0)
        player_wr = Player("blahWR", Position.WR, 5)
        player_wr2 = Player("blahWR2", Position.WR, 10)
        player_te = Player("blahTE", Position.TE, 20)
        owner.buy(player_te, 5)
        owner.buy(player_wr2, 5)
        owner.buy(player_wr, 5)

        self.assertAlmostEqual(30, owner.start_value())
        self.assertAlmostEqual(5, owner.bench_value())
        self.assertAlmostEqual(17.5, owner.score(.5))




