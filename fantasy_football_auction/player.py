"""
This module holds logic relating to individual football players (the people who are bought in the auction).
"""

from csv import reader
from fantasy_football_auction.position import Position


class Player:
    """
    Represents an individual draftable player who has a Position,
    name, id, and value (as in how good they are to have on your team)

    Attributes:
        :ivar str name: Name of the player
        :ivar Position position: position they play
        :ivar int value: integer value of the player indicating how valuable they are
        :ivar int player_id: unique integer ID of the player to distinguish them from other players
    """

    def __init__(self, name, position, value, player_id):
        """
        :param str name: name of this player
        :param Position position: Position this player plays
        :param int value: integer value of this player (how good they are)
        :param int player_id: unique integer ID of the player to distinguish them from other players
        """
        self.name = name
        self.position = position
        self.value = value
        self.player_id = player_id

    def __eq__(self, other):
        return isinstance(self, other.__class__) and self.player_id == other.player_id


def players_from_fantasypros_cheatsheet(file):
    """
    :param File file: path to the file containing the player values in the standard
    CSV format used for fantasypros cheatsheets
    :return list(Player): a list of Players based on the info in the cheatsheet
    """

    with open(file, newline='') as csvfile:
        # Note - considered using a generator for this, but I don't want to hold the file open
        # for a long time and it's pretty small anyway.
        players = []
        playerindex = 0
        playerreader = reader(csvfile, delimiter=',')
        linecount = 0
        for row in playerreader:
            if linecount > 1:
                raw_name = row[0]
                name = raw_name[:raw_name.find('(') - 1]
                position_text = raw_name[raw_name.find('(') + 1:raw_name.find('-') - 1]
                position = Position[position_text]
                value = int(row[2].replace('$', ''))
                players.append(Player(name, position, value, linecount-2))
                playerindex += 1
            linecount += 1
    return players
