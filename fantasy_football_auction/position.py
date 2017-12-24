from enum import Enum


class Position(Enum):
    """
    Represents a position in football that a player occupies.
    """
    QB = 0
    RB = 1
    WR = 2
    TE = 3
    DST = 4
    K = 5
    LB = 6
    DE = 7
    DT = 8
    CB = 9
    S = 10


class RosterSlot:
    """
    Represents a position in football.

    Attributes:
        positions (:obj:`list` of :obj:`Position`): list of positions that can occupy this slot
        abbreviation (str): abbreviation to use to refer to this slot
    """

    def __init__(self, positions, abbreviation):
        """

        :param positions (:obj:`list` of :obj:`Position`): set of positions that can occupy this slot
        :param abbreviation (str): abbreviation to use to refer to this roster slot
        """
        self.positions = positions
        self.abbreviation = abbreviation

    def num_accepted(self):
        """

        :return (:obj:`int`): number of different accepted positions
        """
        return len(self.positions)

    def accepts(self, player):
        """

        :param Player player: player to check
        :return boolean: true iff this slot accepts the player, based on their position
        """
        return player.position in self.positions

    def __eq__(self, other):
        """
        check if the slot is the same
        """
        return isinstance(self, other.__class__) and self.abbreviation == other.abbreviation


RosterSlot.QB = RosterSlot({Position.QB}, "QB")
RosterSlot.RB = RosterSlot({Position.RB}, "RB")
RosterSlot.WR = RosterSlot({Position.WR}, "WR")
RosterSlot.TE = RosterSlot({Position.TE}, "TE")
RosterSlot.WRRB = RosterSlot({Position.WR, Position.RB}, "WR/RB")
RosterSlot.WRTE = RosterSlot({Position.WR, Position.TE}, "WR/TE")
RosterSlot.RBTE = RosterSlot({Position.RB, Position.TE}, "RB/TE")
RosterSlot.WRRBTE = RosterSlot({Position.WR, Position.RB, Position.TE}, "WR/RB/TE")
RosterSlot.QBWRRBTE = RosterSlot({Position.QB, Position.WR, Position.RB, Position.TE}, "QB/WR/RB/TE")
RosterSlot.DST = RosterSlot({Position.DST}, "DST")
RosterSlot.K = RosterSlot({Position.K}, "K")
RosterSlot.BN = RosterSlot({Position.QB, Position.RB, Position.WR, Position.TE, Position.DST, Position.K,
                            Position.LB, Position.DE, Position.DT, Position.CB, Position.S}, "BN")
RosterSlot.DL = RosterSlot({Position.DT, Position.DE}, "DL")
RosterSlot.LB = RosterSlot({Position.LB}, "LB")
RosterSlot.DB = RosterSlot({Position.CB, Position.S}, "DB")
RosterSlot.IDP = RosterSlot({Position.LB, Position.DE, Position.DT, Position.CB, Position.S}, "IDP")
RosterSlot.DE = RosterSlot({Position.DE}, "DE")
RosterSlot.DT = RosterSlot({Position.DT}, "DT")
RosterSlot.CB = RosterSlot({Position.CB}, "CB")
RosterSlot.S = RosterSlot({Position.S}, "S")

RosterSlot.slots = [RosterSlot.QB, RosterSlot.RB, RosterSlot.WR, RosterSlot.TE, RosterSlot.WRRB, RosterSlot.WRTE,
                    RosterSlot.RBTE, RosterSlot.WRRBTE, RosterSlot.QBWRRBTE, RosterSlot.DST, RosterSlot.K,
                    RosterSlot.BN, RosterSlot.DL, RosterSlot.LB, RosterSlot.DB, RosterSlot.IDP, RosterSlot.DE,
                    RosterSlot.DT, RosterSlot.CB, RosterSlot.S]
