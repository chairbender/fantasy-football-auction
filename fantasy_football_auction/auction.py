"""
This module contains classes related to the running and logic of the actual auction game. This all lives in the
Auction class.
"""
import random
from enum import Enum

from fantasy_football_auction.owner import Owner


class Error(Exception):
    """
    Base class for all exceptions raised by this module
    """


class InvalidActionError(Error):
    """
    Someone tried to do something that isn't allowed by the rules of the game. See the message for details.
    """


class AuctionState(Enum):
    """
    A state for the auction to be in
    """
    NOMINATE = 0
    BID = 1
    DONE = 2


class Auction:
    """
    Represents a fantasy football auction.
    You specify a list of draftable players, each having a position, value (based on how
    good they are to have on your team), name, and integer ID.
    You specify the number of owners.
    and the money available for each to spend.
    You specify the number and type of each position that needs to be filled on each
    team.

    Attributes:
        :ivar list(Owner) owners: all of the owners in the game. Read only.
        :ivar list(Player) players: all of the draftable players in the game. Read only.
        :ivar list(Player) undrafted_players: all of the undrafted players in the current
            game. Read only.
        :ivar int money: starting money of each owner. Read only.
        :ivar list(RosterPosition) roster: all of the slots that each owner needs
            to fill in this game. Read only.
        :ivar AuctionState state: current state of the auction game FSM. Read only.
        :ivar int turn_index: index of owner whose turn it is to nominate a player
            for auction. Read only.
        :ivar Player nominee: current player who is up for auction. Read only.
        :ivar list(int) tickbids: current bids that have been submitted on
            a given tick of the game. The index of this list represents the owner_id of the Owner
            who submitted the bid. Read only.
        :ivar list(int) bids: each owner's most recent bid value for the current
            nominee. The index of this list represents the owner_id of the Owner who submitted the
            bid. Read only.
        :ivar int bid: current bid amount for the current nominee. Read only.
    """

    def __init__(self, players, num_owners, money, roster):
        """
        Starts the auction with the specified settings.

        :param list(Player) players: Players in this auction
        :param int num_owners: number of owners. Owners are referenced by integer id.
        :param int money: integer dollar amount of money each player has
        :param list(RosterPosition) roster:
            list of RosterPositions each player needs to fill
        """
        self.owners = [Owner(money, roster, i) for i in range(num_owners)]
        self.players = players
        self.players.sort(key=lambda player: player.value, reverse=True)
        # sorted by value
        self.undrafted_players = list(players)
        self.undrafted_players.sort(key=lambda player: player.value, reverse=True)
        self.money = money
        self.roster = roster
        self.state = AuctionState.NOMINATE
        self.turn_index = 0
        self.nominee = None
        self.tickbids = [0] * num_owners
        self.bids = [0] * num_owners
        self.bid = None

        # for performance reasons
        self._nominee_index = -1
        # stores the owner_id (or -1 if unowned) of each player
        self._player_ownership = [-1 for player in self.players]

    def _winning_owner(self):
        """

        :return Owner: owner who bid the most
        """
        return self.owners[self.winning_owner_index()]

    def owner_index_of_player(self, player_idx):
        """
        Fast way to look up the owner_id of the owner for a given player
        :param int player_idx: index of the player to lookup
        :return int: -1 if unowned, else the owner_id of the owner
        """

        return self._player_ownership[player_idx]

    def winning_owner_index(self):
        """

        :return Owner: owner who bid the most
        """
        winner_idx = -1
        price = 0
        for idx, bid in enumerate(self.bids):
            if bid > price:
                price = bid
                winner_idx = idx
        return winner_idx

    def nominee_index(self):
        """

        :return: int: index of the current player nominee in the players list. -1 if no nominee.
        """
        return self._nominee_index

    def tick(self):
        """
        Advances time in the game. Use this once all "choices" have been submitted for the current
        game state using the other methods.
        """
        if self.state == AuctionState.NOMINATE:
            # if no nominee submitted, exception
            if self.nominee is None:
                raise InvalidActionError("Tick was invoked during nomination but no nominee was selected.")
            self.state = AuctionState.BID
            # initialize bids array to hold each owner's bid
            # this holds the latest bids submitted for the current bidding phase
            self.bids = [self.bid if i == self.turn_index else 0 for i in range(len(self.owners))]
            # this holds the bids submitted on a given tick
            self.tickbids = [0] * len(self.owners)
        elif self.state == AuctionState.BID:
            # If no new bids submitted, we're done with this bid and the player gets what they bid for
            if not any(bid > 0 for bid in self.tickbids):
                winner = self._winning_owner()
                winner.buy(self.nominee, self.bid)
                self._player_ownership[self._nominee_index] = self.winning_owner_index()
                self.undrafted_players.remove(self.nominee)
                self.nominee = None
                # check if we're done, or move to the next player who still has space
                done = True
                for i in range(len(self.owners)):
                    next_turn = (self.turn_index + 1 + i) % len(self.owners)
                    if self.owners[next_turn].remaining_picks() > 0:
                        self.turn_index = next_turn
                        done = False
                        break
                # if we didn't move on, we're done
                if done:
                    self.state = AuctionState.DONE
                else:
                    self.state = AuctionState.NOMINATE
            else:
                # new bids have been submitted,
                # randomly pick the bid to accept from the highest,
                # then everyone gets a chance to submit more
                top_idxs = [i for i, bid in enumerate(self.tickbids) if bid == max(self.tickbids)]
                accept_idx = random.choice(top_idxs)
                # set this as the new bid
                self.bid = self.tickbids[accept_idx]
                # update the bids for this round
                self.bids[accept_idx] = self.bid
                # clear this for the next tick
                self.tickbids = [0] * len(self.owners)

    def place_bid(self, owner_id, bid):
        """
        Submits a bid for this tick for current player. This is not a guarantee that it will be accepted!
        If other players submit a higher bid this same tick, the bid won't be counted. Try again next tick if it's not
        too high!
        :param int owner_id: id of owner who is submitting the bid
        :param int bid: bid amount

        :raise InvalidActionError: if the action is not allowed according to the rules. See the error message
            for details.
        """

        if self.state != AuctionState.BID:
            raise InvalidActionError("Bid was attempted, but it is not currently time to submit bids.")
        elif self.bid > bid:
            raise InvalidActionError("Bid amount " + str(bid) + " must be greater than current bid of " + str(self.bid))
        elif not self.owners[owner_id].can_buy(self.nominee, bid):
            raise InvalidActionError("The owner with index " + str(owner_id) +
                                     " cannot afford a bid of " + str(bid) + " for player " + self.nominee.name +
                                     " or cannot actually buy this player (due to "
                                     "not having any free slots)")

        # success, add their bid to the current tick
        self.tickbids[owner_id] = bid

    def nominate(self, owner_id, player_idx, bid):
        """
        Nominates the player for auctioning.

        :param int owner_id: index of the owner who is nominating
        :param int player_idx: index of the player to nominate in the players list
        :param int bid: starting bid

        :raise InvalidActionError: if the action is not allowed according to the rules. See the error message
            for details.
        """

        owner = self.owners[owner_id]
        nominated_player = self.players[player_idx]

        if self.state != AuctionState.NOMINATE:
            raise InvalidActionError("Auction state is not NOMINATE, so nomination is not allowed")
        elif self.turn_index != owner_id:
            raise InvalidActionError("Owner " + str(owner_id) + " tried to nominate, but it is currently " +
                                     str(self.turn_index) + "'s turn")
        elif nominated_player not in self.undrafted_players:
            raise InvalidActionError("The player with index " + str(player_idx) + ", named " +
                                     nominated_player.name +
                                     " has already been purchased and cannot be nominated.")
        elif bid > owner.max_bid():
            raise InvalidActionError("Bid amount was " + str(bid) + " but this owner can only bid a maximum of " +
                                     str(owner.max_bid()))
        elif bid < 1:
            raise InvalidActionError("Bid amount was " + str(bid) + " but must be greater than 1")
        elif not any(owner.can_buy(nominated_player, bid) for owner in self.owners):
            raise InvalidActionError("No owner can actually buy this player, so nomination is not allowed.")

        # nomination successful, bidding time
        self.nominee = nominated_player
        self._nominee_index = player_idx
        self.bid = bid
        self.tickbids[owner_id] = bid

    def scores(self, starter_value):
        """

        :param float starter_value: floating point between 0 and 1 inclusive indicating how heavily the final score
            should be weighted between starter and bench. If 1, for example, bench value will be completely ignored when
            calculating winners. If 0, only bench value will be used to calculate winners
        :return float: an array of weighted final scores, with index corresponding to owner index and
            element value corresponding to the weighted score (weighted based on starter_value)
        """

        return [owner.score(starter_value) for owner in self.owners]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        response = "State: "
        if self.state == AuctionState.NOMINATE:
            response += "Nominating\n"
            response += "Owner " + str(self.turn_index) + "'s turn\n"
        elif self.state == AuctionState.BID:
            response += "Bidding\n\n"
            response += "Nominee: " + self.nominee.position.name + " " + self.nominee.name + " ($" + str(
                self.nominee.value) + ")" "\n\n"
        else:
            response += "Done\n\n"

        for i, owner in enumerate(self.owners):
            response += "Owner " + str(i) + ": $" + str(self.bids[i]) + "(Tick: $" + str(
                self.tickbids[i]) + " Max $" + str(owner.max_bid()) + ")\n"

        response += "\n###OWNER STATUS###\n"

        for i, owner in enumerate(self.owners):
            response += "Owner " + str(i) + "\nRoster:\n"

            for slot in owner.roster:
                if slot.occupant is None:
                    response += slot.abbreviation + " Empty\n"
                else:
                    response += slot.abbreviation + " " + slot.occupant.name + "\n"
            response += "\n"

        response += "\n###UNDRAFTED PLAYERS###\n"

        for i, player in enumerate(self.undrafted_players):
            response += str(i + 1) + ". " + str(player.position.name) + " " + str(player.name) + " ($" + str(
                player.value) + ")\n"

        return response
