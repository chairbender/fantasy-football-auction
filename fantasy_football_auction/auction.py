import random
from enum import Enum, auto
from functools import reduce
from itertools import count, filterfalse


class AuctionState(Enum):
    """
    A state for the auction to be in
    """
    NOMINATE = 0
    BID = 1
    DONE = 2


class Purchase:
    """
    Represents an owners purchase of a player
    """

    def __init__(self, player, cost, roster_slot):
        """

        :param player: player purchased
        :param cost: cost paid
        :param roster_slot: roster_slot the player will occupy
        """

        self.player = player
        self.cost = cost
        self.roster_slot = roster_slot


class Owner:
    """
    Represents an owner during an auction
    """

    def __init__(self, money, roster, id):
        """

        :param money: starting money
        :param roster: roster slots this player needs to fill
        :param id: unique id of the owner to distinguish it from other owners, Must be [0,num owners)
        """
        self.money = money
        # create our own copy so we can sort by the number of accepted positions
        self.roster = list(roster)
        self.roster.sort(key=lambda roster_slot: roster_slot.num_accepted())
        # tracks the purchases made by this owner
        self.purchases = []
        self.id = id

    def buy(self, player, cost):
        """
        indicate that the player was bought at the specified cost

        :param player: player to buy
        :param cost: cost to pay
        """
        self.money -= cost
        # remove the roster slot that is the most specific
        # we know they are sorted by specificity
        for roster_slot in self.roster:
            if roster_slot.accepts(player):
                self.purchases.append(Purchase(player, cost, roster_slot))
                self.roster.remove(roster_slot)
                break

    def max_bid(self):
        """

        :return: the maximum bid the player can make. (current money + 1) - number of slots left (since they have to pay
        one dollar per slot and must fill all slots).

        """
        return (self.money + 1) - len(self.roster)

    def can_buy(self, player, bid):
        """

        :param player: player to check
        :param bid: bid amount
        :return: true iff this owner has space in the roster for the given player and has enough to
            bid the given amount
        """

        return any(roster_slot.accepts(player) for roster_slot in self.roster) and bid <= self.max_bid()

    def remaining_picks(self):
        """

        :return: the number of picks left for this owner to make until their roster is filled, 0 if full
        """

        return len(self.roster)

    def possible_nominees(self, players):
        """

        :param players: list of players to choose from
        :return: a list of players that could be legally nominated by this owner
        """

        return list(filter(lambda player: self.can_buy(player,1), players))


class Auction:
    """
    Represents a fantasy football auction.
    You specify a list of draftable players, each having a position, value (based on how
    good they are to have on your team), name, and integer ID.
    You specify the number of owners.
    and the money available for each to spend.
    You specify the number and type of each position that needs to be filled on each
    team.
    """

    def __init__(self, players, num_owners, money, roster):
        """
        Starts the auction with the specified settings.

        :param players: Players in this auction
        :param num_owners: number of owners. Owners are referenced by integer id.
        :param money: integer dollar amount of money each player has
        :param positions: list of RosterPositions each player needs to fill
        """
        self.owners = [Owner(money, roster, i) for i in range(num_owners)]
        self.players = players
        # sorted by value
        self.undrafted_players = list(players)
        self.undrafted_players.sort(key=lambda player: player.value, reverse=True)
        self.money = money
        self.roster = roster
        self.state = AuctionState.NOMINATE
        # index of owner whose turn it is to nominate
        self.turn_index = 0

        # holds current bid nominee
        self.nominee = None
        # holds bids submitted on a given tick (if there's a tie on the highest, the accepted bid for that tick is randomly chosen),
        # this doesn't mean they'll win that bid though, it just means their bid "went through"
        self.tickbids = [0] * num_owners
        # holds the actual submitted bid values for the current nominee, just so one can see
        # who has bid what so far
        self.bids = [0] * num_owners

    def _winning_owner(self):
        """

        :return: owner who bid the most
        """
        winner_idx = -1
        price = 0
        for idx, bid in enumerate(self.bids):
            if bid > price:
                price = bid
                winner_idx = idx
        assert winner_idx > -1
        return self.owners[winner_idx]

    def tick(self):
        """
        Advances time in the game. Use this once all "choices" have been submitted for the current
        game state using the other methods.
        """
        if self.state == AuctionState.NOMINATE:
            # if no nominee submitted, pick the next highest valued player for $1
            if self.nominee is None:
                self.nominee = self.undrafted_players[0]
                self.bid = 1
            self.state = AuctionState.BID
            # initialize bids array to hold each owner's bid
            # this holds the latest bids submitted for the current bidding phase
            self.bids = [self.bid if i == self.turn_index else 0 for i in range(len(self.owners))]
            # this holds the bids submitted on a given tick
            self.tickbids = [0] * len(self.owners)
            self.turn_index = self.turn_index + 1 % len(self.owners)
        elif self.state == AuctionState.BID:
            # If no new bids submitted, we're done with this bid and the player gets what they bid for
            if not any(bid > 0 for bid in self.tickbids):
                winner = self._winning_owner()
                winner.buy(self.nominee, self.bid)
                self.undrafted_players.remove(self.nominee)
                self.nominee = None
                # check if we're done
                if any(owner.remaining_picks() > 0 for owner in self.owners):
                    self.state = AuctionState.NOMINATE
                else:
                    self.state = AuctionState.DONE
            else:
                # new bids have been submitted, randomly pick the bid to accept from the highest, then everyone gets a chance to submit more
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
        :param owner_id: id of owner who is submitting the bid
        :param bid: bid amount
        :return: false iff choice was not allowed
        """

        #is it time to bid?
        if self.state != AuctionState.BID:
            return False

        # is bid greater than current bid amount
        if self.bid > bid:
            return False

        # has bid already been submitted this tick by this player?
        if self.tickbids[owner_id] > 0:
            return False

        # can this owner add the player to their roster
        if not self.owners[owner_id].can_buy(self.nominee, bid):
            return False

        # success, add their bid to the current tick
        self.tickbids[owner_id] = bid

        return True

    def nominate(self, owner_id, player_idx, bid):
        """
        Nominates the player for auctioning.

        :param owner_id: index of the owner who is nominating
        :param player_idx: index of the player to nominate in the players array
        :param bid: starting bid
        :return false iff operation not allowed in the current state
        """

        owner = self.owners[owner_id]
        nominated_player = self.players[player_idx]

        # Is it time to nominate?
        if self.state != AuctionState.NOMINATE:
            return False

        # Is the player draftable?
        if nominated_player not in self.undrafted_players:
            return False

        # Is it this owner's turn to nominate?
        if owner_id != self.turn_index:
            return False

        # Is the owner allowed to bid that much?
        if bid > owner.max_bid():
            return False

        # has the owner already nominated
        if self.nominee is not None:
            return False

        #bid must be 1 or higher
        if bid < 1:
            return False

        # can any owner actually get this player
        if not any(owner.can_buy(nominated_player,bid) for owner in self.owners):
            return False

        # nomination successful, bidding time
        self.nominee = nominated_player
        self.bid = bid

        return True

    def scores(self, starter_value):
        """

        :param starter_value: floating point between 0 and 1 inclusive indicating how heavily the final score should
            be weighted between starter and bench. If 1, for example, bench value will be completely ignored when calculating
            winners. If 0, only bench value will be used to calculate winners
        :return: an array of weighted final scores, with index corresponding to owner index and
            element value corresponding to the weighted score (weighted based on starter_value)
        """
        return map(lambda owner: owner.start_value() * starter_value - owner.bench_value() * (1 - starter_value), self.owners)


    def __repr__(self):
        return self.__str__()

    def __str__(self):
        response = "State: "
        if self.state == AuctionState.NOMINATE:
            response += "Nominating\n"
            response += "Owner " + str(self.turn_index) + "'s turn\n"
        else:
            response += "Bidding\n\n"
            response += "Nominee: " + self.nominee.position.name + " " + self.nominee.name + " ($" + str(
                self.nominee.value) + ")" "\n\n"

        for i, owner in enumerate(self.owners):
            response += "Owner " + str(i) + ": $" + str(self.bids[i]) + "(Tick: $" + str(
                self.tickbids[i]) + " Max $" + str(owner.max_bid()) + ")\n"

        response += "\n###OWNER STATUS###\n"

        for i, owner in enumerate(self.owners):
            response += "Owner " + str(i) + "\nPurchased:\n"

            for purchase in owner.purchases:
                response += purchase.roster_slot.abbreviation + " " + purchase.player.name + " ($" + str(
                    purchase.cost) + ")\n"

            response += "Open:\n"
            for roster_slot in owner.roster:
                response += roster_slot.abbreviation + "\n"
            response += "\n"

        response += "\n###UNDRAFTED PLAYERS###\n"

        for i, player in enumerate(self.undrafted_players):
            response += str(i + 1) + ". " + str(player.position.name) + " " + str(player.name) + " ($" + str(
                player.value) + ")\n"

        return response
