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
        player_qb = Player("blahQB", Position.QB, 1, 0)
        player_wr = Player("blahWR", Position.WR, 1, 1)
        player_rb = Player("blahRB", Position.RB, 1, 2)
        player_te = Player("blahTE", Position.TE, 1, 3)
        player_cb = Player("blahCB", Position.CB, 1, 4)
        player_s = Player("blahS", Position.S, 1, 5)
        self.assertTrue(pos1.accepts(player_qb))
        self.assertTrue(pos3.accepts(player_wr))
        self.assertTrue(pos3.accepts(player_rb))
        self.assertTrue(pos3.accepts(player_te))
        self.assertTrue(pos11.accepts(player_qb))
        self.assertTrue(pos11.accepts(player_cb))
        self.assertTrue(pos11.accepts(player_s))
        self.assertFalse(pos1.accepts(player_s))
        self.assertFalse(pos1.accepts(player_s))
        self.assertFalse(pos1.accepts(player_te))
        self.assertFalse(pos1.accepts(player_cb))
        self.assertFalse(pos3.accepts(player_s))

    def test_equals(self):
        ros1 = RosterSlot({Position.QB}, "QB")
        ros2 = RosterSlot({Position.QB}, "QB")
        self.assertEqual(ros1, ros2)
        ros1 = RosterSlot({Position.WR, Position.RB, Position.TE}, "WR/RB/TE")
        ros2 = RosterSlot({Position.WR, Position.RB, Position.TE}, "WR/RB/TE")
        self.assertEqual(ros1, ros2)


