from enum import Enum


class Position(Enum):
    """
    Represents a position in football that a player occupies.
    """
    QB = 1,
    RB = 2
    WR = 3,
    TE = 4,
    DST = 5,
    K = 6,
    LB =7,
    DE  = 8,
    DT = 9,
    CB = 10,
    S = 11


class RosterSlot:
    """
    Represents a position in football.
    """

    def __init__(self, positions):
        """

        :param positions: set of positions that can occupy this slot
        """
        self.positions = positions

    def num_accepted(self):
        """

        :return: number of different accepted positions
        """
        return len(self.positions)

    def accepts(self, player):
        """

        :param player: player to check
        :return: true iff this slot accepts the player, based on their position
        """
        return player.position in self.positions

RosterSlot.QB = RosterSlot({Position.QB})
RosterSlot.RB = RosterSlot({Position.RB})
RosterSlot.WR = RosterSlot({Position.WR})
RosterSlot.TE = RosterSlot({Position.TE})
RosterSlot.WRRB = RosterSlot({Position.WR, Position.RB})
RosterSlot.WRTE = RosterSlot({Position.WR, Position.TE})
RosterSlot.RBTE = RosterSlot({Position.RB, Position.TE})
RosterSlot.WRRBTE = RosterSlot({Position.WR, Position.RB, Position.TE})
RosterSlot.QBWRRBTE = RosterSlot({Position.QB, Position.WR, Position.RB, Position.TE})
RosterSlot.DST = RosterSlot({Position.DST})
RosterSlot.K = RosterSlot({Position.K})
RosterSlot.BN = RosterSlot({Position.QB, Position.RB, Position.WR, Position.TE, Position.DST, Position.K,
                               Position.LB, Position.DE, Position.DT, Position.CB, Position.S})
RosterSlot.DL = RosterSlot({Position.DT, Position.DE})
RosterSlot.LB = RosterSlot({Position.LB})
RosterSlot.DB = RosterSlot({Position.CB, Position.S})
RosterSlot.IDP = RosterSlot({Position.LB, Position.DE, Position.DT, Position.CB, Position.S})
RosterSlot.DE = RosterSlot({Position.DE})
RosterSlot.DT = RosterSlot({Position.DT})
RosterSlot.CB = RosterSlot({Position.CB})
RosterSlot.S = RosterSlot({Position.S})
