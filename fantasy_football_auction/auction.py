class Auction:
    """
    Represents a fantasy football auction.
    You specify a list of draftable players, each having a position, value (based on how
    good they are to have on your team), name, and integer ID.
    You specify an ordered list of owners (in draft order)
    and the money available for each to spend.
    You specify the number and type of each position that needs to be filled on each
    team.
    """
    def __init__(self,players,owners,money,positions):
        """

        :param players: Players in this auction
        :param owners: list of Owners in draft order
        :param money: integer dollar amount of money each player has
        :param positions: list of RosterPositions each player needs to fill
        """
        self.players = players
        self.owners = owners
        self.money = money
        self.positions = positions