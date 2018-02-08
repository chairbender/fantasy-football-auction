"""
This module holds the logic related to the fantasy football owner in an auction. This primarily lives in the
Owner class.

"""

from enum import Enum
from functools import reduce

from fantasy_football_auction.player import Player
from fantasy_football_auction.position import RosterSlot


class Error(Exception):
    """
    Base class for all exceptions raised by this module
    """


class InsufficientFundsError(Error):
    """
    Owner tried to make a purchase with insufficient funds.
    """


class NoValidRosterSlotError(Error):
    """
    Owner tried to make a purchase but there isn't space in the roster
    for this type of player.
    """


class AlreadyPurchasedError(Error):
    """
    Owner tried to buy the same player twice
    """


class OwnerRosterSlot(RosterSlot):
    """
    Just like a RosterSlot, but has the possibility of having a player occupying or not occupying it, and a purchase
    price.

    Attributes:
        :ivar Player occupant: player which has filled this slot. None if not filled.
        :ivar int cost: price the player was purchased for
    """

    @classmethod
    def from_roster_slot(cls, roster_slot):
        """

        :param RosterSlot roster_slot: to create from
        :return OwnerRosterSlot: an OwnerRosterSlot with the same state as roster_slot
        """
        return cls(roster_slot.positions, roster_slot.abbreviation)

    def __init__(self, positions, abbreviation):
        """

        :param list(Position) positions: set of positions that can occupy this slot
        :param str abbreviation: abbreviation to use to refer to this roster slot
        """
        super(OwnerRosterSlot, self).__init__(positions, abbreviation)
        self.occupant = None
        self.cost = -1


class Owner:
    """
    Represents an owner during an auction

    Attributes:
        :ivar int money : amount of money the owner has remaining. Read only.
        :ivar list(OwnerRosterSlot) roster: the Owner's current roster, indicating which positions need to be filled
            (where occupant is None) and which have been filled (where occupant indicates the player that filled it).
            This will be ordered by most -> least specific slots (so the bench slots will always be last). Read only.
        :ivar int id: id of this owner. Read only.
    """

    def __init__(self, money, roster, owner_id):
        """

        :param int money:  starting money
        :param list(RosterSlot) roster: roster slots this owner needs to fill
        :param int owner_id: unique id of the owner to distinguish it from other owners, Must be [0,num owners)
        """
        self.money = money
        self.roster = [OwnerRosterSlot.from_roster_slot(roster_slot) for roster_slot in roster]
        self.roster.sort(key=lambda roster_slot: roster_slot.num_accepted())
        self.id = owner_id
        self._remaining_picks = len(self.roster)
        self._owned_player_ids = set()

    def _slot_in(self, player, cost):
        """

        :param Player player: player to slot into the owner's current roster. Puts this
            player in the most specific slot that it can occupy, kicking out any lower-value players
            (and finding alternate slots for them) if the slot is occupied. If this player is lower valued than
            that of a player in an occupied slot, finds the next most specific slot and so on.

            This has the side effect of ensuring that the highest value players are on the start rather than the
            bench. It also seems to match how fantasy owners like to order their team.
        :param int cost: cost paid for this player

        """

        # find the most specific slot this player can fit into where they are the highest value.
        to_replace = player
        to_replace_cost = cost
        for roster_slot in self.roster:
            if roster_slot.accepts(to_replace):
                # check if the slot is already occupied
                if roster_slot.occupant is None:
                    # We're done. Just put the new person here.
                    roster_slot.occupant = to_replace
                    roster_slot.cost = to_replace_cost
                    break
                elif to_replace.value > roster_slot.occupant.value:
                    # the new player's value is higher than this slot's value, so
                    # put the new player here and kick out the old player, then keep looking
                    # for a new spot for the kicked-out player
                    replacee = roster_slot.occupant
                    replacee_cost = roster_slot.cost
                    roster_slot.occupant = to_replace
                    roster_slot.cost = to_replace_cost
                    to_replace = replacee
                    to_replace_cost = replacee_cost
                # keep looking

    def buy(self, player, cost):
        """
        indicate that the player was bought at the specified cost

        :param Player player: player to buy
        :param int cost: cost to pay

        :raises InsufficientFundsError: if owner doesn't have the money
        :raises NoValidRosterSlotError: if owner doesn't have a slot this player could fill
        :raises AlreadyPurchasedError: if owner already bought this player
        """
        if cost > self.max_bid():
            raise InsufficientFundsError()
        elif not any(roster_slot.accepts(player) and roster_slot.occupant is None for roster_slot in self.roster):
            raise NoValidRosterSlotError()
        elif self.owns(player):
            raise AlreadyPurchasedError()

        self.money -= cost
        self._remaining_picks -= 1
        self._owned_player_ids.add(player.player_id)
        self._slot_in(player, cost)

    def owns(self, player):
        """

        :param Player player: player to check
        :return boolean: true iff this player is already owned by this owner
        """
        return player.player_id in self._owned_player_ids

    def max_bid(self):
        """

        :return int: the maximum bid the player can make. (current money + 1) - number of slots left
        (since they have to pay one dollar per slot and must fill all slots).

        """
        return (self.money + 1) - self.remaining_picks()

    def can_buy(self, player, bid):
        """

        :param Player player: player to check
        :param int bid: bid amount
        :return boolean: true iff this owner has space in the roster for the given player and has enough to
            bid the given amount and has not already purchased this player
        """

        return any(roster_slot.accepts(player) and roster_slot.occupant is None for roster_slot in self.roster) and \
            bid <= self.max_bid() and \
            not self.owns(player)

    def remaining_picks(self):
        """

        :return int: the number of picks left for this owner to make until their roster is filled, 0 if full
        """

        return self._remaining_picks

    def start_value(self):
        """

        :return float: total value of all players in this owner's
            starting lineup
        """

        return reduce(lambda x, y: x + y, [roster_slot.occupant.value for roster_slot in self.roster
                                           if roster_slot != RosterSlot.BN and roster_slot.occupant is not None], 0)

    def bench_value(self):
        """

        :return float: total value of all players in this owner's
            bench lineup
        """
        if not any(roster_slot == RosterSlot.BN for roster_slot in self.roster):
            # no bench slots
            return 0
        else:
            return reduce(lambda x, y: x + y, [roster_slot.occupant.value for roster_slot in self.roster
                                               if roster_slot == RosterSlot.BN and roster_slot.occupant is not None], 0)

    def score(self, starter_value):
        """

        :param float starter_value: floating point between 0 and 1
            inclusive indicating how heavily the final score should
            be weighted between starter and bench. If 1, for example,
            bench value will be completely ignored when calculating
            winners. If 0, only bench value will be used to calculate winners
        :return float: the score this owner earns based on the
            value of their players and the ratio of starter to bench value
        """

        return self.start_value() * starter_value + self.bench_value() * (1 - starter_value)
