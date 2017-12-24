from unittest import TestCase, main

from fantasy_football_auction.player import Player
from fantasy_football_auction.position import RosterSlot, Position


class RosterSlotTestCase(TestCase):

    def test_num_accepted(self):
        pos1 = RosterSlot.QB
        pos3 = RosterSlot.WRRBTE
        pos11 = RosterSlot.BN
        self.assertEqual(1, pos1.num_accepted())
        self.assertEqual(3, pos3.num_accepted())
        self.assertEqual(11, pos11.num_accepted())

    def test_accepts(self):
        pos1 = RosterSlot.QB
        pos3 = RosterSlot.WRRBTE
        pos11 = RosterSlot.BN
        playerQB = Player("blah", Position.QB, 1)
        playerWR = Player("blah", Position.WR, 1)
        playerRB = Player("blah", Position.RB, 1)
        playerTE = Player("blah", Position.TE, 1)
        playerCB = Player("blah", Position.CB, 1)
        playerS = Player("blah", Position.S, 1)
        self.assertTrue(pos1.accepts(playerQB))
        self.assertTrue(pos3.accepts(playerWR))
        self.assertTrue(pos3.accepts(playerRB))
        self.assertTrue(pos3.accepts(playerTE))
        self.assertTrue(pos11.accepts(playerQB))
        self.assertTrue(pos11.accepts(playerCB))
        self.assertTrue(pos11.accepts(playerS))

    def test_equals(self):
        ros1 = RosterSlot({Position.QB}, "QB")
        ros2 = RosterSlot({Position.QB}, "QB")
        self.assertEqual(ros1, ros2)
        ros1 = RosterSlot({Position.WR, Position.RB, Position.TE}, "WR/RB/TE")
        ros2 = RosterSlot({Position.WR, Position.RB, Position.TE}, "WR/RB/TE")
        self.assertEqual(ros1, ros2)


