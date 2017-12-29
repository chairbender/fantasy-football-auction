from unittest import TestCase

from fantasy_football_auction.auction import Auction, AuctionState, InvalidActionError
from fantasy_football_auction.player import Player
from fantasy_football_auction.position import Position, RosterSlot


class AuctionTestCase(TestCase):
    
    def setUp(self):
        # Starts a 3 player game, 200 to spend
        roster_slots = [RosterSlot.QB, RosterSlot.RB, RosterSlot.RB, RosterSlot.WR, RosterSlot.WR, RosterSlot.WRRBTE,
                        RosterSlot.TE, RosterSlot.K, RosterSlot.DST, RosterSlot.BN, RosterSlot.BN]
        self.players = [
            Player("GoodQB1", Position.QB, 35, 0),
            Player("GoodQB2", Position.QB, 30, 1),
            Player("GoodQB3", Position.QB, 25, 2),
            Player("GoodQB4", Position.QB, 20, 3),
            Player("GoodQB5", Position.QB, 15, 4),
            Player("GoodQB6", Position.QB, 10, 5),
            Player("GoodWR1", Position.WR, 50, 6),
            Player("GoodWR2", Position.WR, 48, 7),
            Player("GoodWR3", Position.WR, 46, 8),
            Player("OkayWR1", Position.WR, 40, 9),
            Player("OkayWR2", Position.WR, 38, 10),
            Player("OkayWR3", Position.WR, 36, 11),
            Player("BadWR1", Position.WR, 20, 12),
            Player("BadWR2", Position.WR, 15, 13),
            Player("BadWR3", Position.WR, 5, 14),
            Player("GoodRB1", Position.RB, 45, 15),
            Player("GoodRB2", Position.RB, 43, 16),
            Player("GoodRB3", Position.RB, 41, 17),
            Player("OkayRB1", Position.RB, 35, 18),
            Player("OkayRB2", Position.RB, 33, 19),
            Player("OkayRB3", Position.RB, 31, 20),
            Player("BadRB1", Position.RB, 15, 21),
            Player("BadRB2", Position.RB, 10, 22),
            Player("BadRB3", Position.RB, 5, 23),
            Player("GoodTE1", Position.TE, 35, 24),
            Player("GoodTE2", Position.TE, 30, 25),
            Player("GoodTE3", Position.TE, 25, 26),
            Player("GoodTE4", Position.TE, 10, 27),
            Player("GoodTE5", Position.TE, 8, 28),
            Player("GoodTE6", Position.TE, 5, 29),
            Player("GoodK1", Position.K, 10, 30),
            Player("GoodK2", Position.K, 9, 31),
            Player("GoodK3", Position.K, 8, 32),
            Player("GoodK4", Position.K, 7, 33),
            Player("GoodK5", Position.K, 6, 34),
            Player("GoodK6", Position.K, 5, 35),
            Player("GoodDST1", Position.DST, 10, 36),
            Player("GoodDST2", Position.DST, 9, 37),
            Player("GoodDST3", Position.DST, 8, 38),
            Player("GoodDST4", Position.DST, 7, 39),
            Player("GoodDST5", Position.DST, 6, 40),
            Player("GoodDST6", Position.DST, 5, 41),
        ]
        self.auction = Auction(self.players, 3, 200, roster_slots)

    def player(self, name):
        """

        :param name: name of player to get index of
        :return int: index of the player in the players array.
        """
        return [index for index, player in enumerate(self.players) if player.name == name][0]

    def test_auction(self):
        # make sure str method works
        str(self.auction)

        # play a mock game
        # To start, it should be owner 0's turn to nominate
        self.assertEqual(AuctionState.NOMINATE, self.auction.state)
        self.assertEqual(0, self.auction.turn_index)

        # let's be 'that guy' and nominate a kicker first.
        self.auction.nominate(0, self.player("GoodK1"), 1)

        # others who try to nominate should get an exception
        with self.assertRaises(InvalidActionError):
            self.auction.nominate(1, self.player("GoodK1"), 1)
        with self.assertRaises(InvalidActionError):
            self.auction.nominate(2, self.player("GoodK1"), 1)

        # should be able to change nomination before the tick
        self.auction.nominate(0, self.player("GoodK2"), 2)
        self.auction.nominate(0, self.player("GoodK1"), 2)
        self.auction.tick()
        # check if the nomination went through
        self.assertEqual(AuctionState.BID, self.auction.state)
        self.assertEqual(self.players[self.player("GoodK1")], self.auction.nominee)
        self.assertEqual([2, 0, 0], self.auction.bids)
        self.assertEqual(2, self.auction.bid)

        # nominating at this point should not be allowed by anyone
        with self.assertRaises(InvalidActionError):
            self.auction.nominate(0, self.player("GoodK1"), 3)
        with self.assertRaises(InvalidActionError):
            self.auction.nominate(1, self.player("GoodK1"), 3)
        with self.assertRaises(InvalidActionError):
            self.auction.nominate(2, self.player("GoodK1"), 3)

        # bidding at or under the current bid amount should cause an error
        with self.assertRaises(InvalidActionError):
            self.auction.place_bid(1, 1)
        with self.assertRaises(InvalidActionError):
            self.auction.place_bid(2, 0)

        # make sure str method works
        str(self.auction)

        # if multiple people submit new bids, the highest one should be the "accepted" bid for that tick
        self.auction.place_bid(0, 2)
        self.auction.place_bid(1, 2)
        self.auction.place_bid(2, 3)
        self.auction.tick()
        self.assertEqual(AuctionState.BID, self.auction.state)
        self.assertEqual(self.players[self.player("GoodK1")], self.auction.nominee)
        self.assertEqual([2, 0, 3], self.auction.bids)
        self.assertEqual(3, self.auction.bid)

        # make sure str method works
        str(self.auction)

        # should be able to raise bid amount for no reason
        self.auction.place_bid(2, 4)
        self.auction.tick()
        self.assertEqual(AuctionState.BID, self.auction.state)
        self.assertEqual(self.players[self.player("GoodK1")], self.auction.nominee)
        self.assertEqual([2, 0, 4], self.auction.bids)
        self.assertEqual(4, self.auction.bid)

        # make sure str method works
        str(self.auction)

        # no more bids, it should make the purchase and move to the next nomination
        self.auction.tick()
        self.assertEqual(AuctionState.NOMINATE, self.auction.state)
        self.assertEqual(1, self.auction.turn_index)
        owner2 = self.auction.owners[2]
        self.assertEqual(196, owner2.money)
        self.assertTrue(owner2.owns(self.players[self.player("GoodK1")]))

        # make sure str method works
        str(self.auction)

        # cannot nominate someone already nominated
        with self.assertRaises(InvalidActionError):
            self.auction.nominate(1, self.player("GoodK1"), 1)

        # nominate a good WR
        self.auction.nominate(1, self.player("GoodWR1"), 20)

        # others who try to nominate should get an exception
        with self.assertRaises(InvalidActionError):
            self.auction.nominate(0, self.player("GoodWR2"), 15)
        with self.assertRaises(InvalidActionError):
            self.auction.nominate(2, self.player("GoodRB1"), 10)

        self.auction.tick()
        # check if the nomination went through
        self.assertEqual(AuctionState.BID, self.auction.state)
        self.assertEqual(self.players[self.player("GoodWR1")], self.auction.nominee)
        self.assertEqual([0, 20, 0], self.auction.bids)
        self.assertEqual(20, self.auction.bid)

        # make sure str method works
        str(self.auction)

        # let player 1 and 2 go back and forth a bit
        self.auction.place_bid(1, 21)
        self.auction.tick()
        self.auction.place_bid(2, 22)
        self.auction.tick()
        self.auction.place_bid(1, 25)
        self.auction.tick()
        self.auction.place_bid(1, 30)
        self.auction.tick()
        self.auction.place_bid(2, 40)
        self.auction.tick()
        self.assertEqual(AuctionState.BID, self.auction.state)
        self.assertEqual(self.players[self.player("GoodWR1")], self.auction.nominee)
        self.assertEqual([0, 30, 40], self.auction.bids)
        self.assertEqual(40, self.auction.bid)
        # let p2 have it for 40
        self.auction.tick()
        self.assertTrue(owner2.owns(self.players[self.player("GoodWR1")]))

        self.assertEqual(AuctionState.NOMINATE, self.auction.state)
        self.assertEqual(2, self.auction.turn_index)
        owner2 = self.auction.owners[2]
        self.assertEqual(156, owner2.money)
        self.assertTrue(owner2.owns(self.players[self.player("GoodWR1")]))

        # make sure str method works
        str(self.auction)














