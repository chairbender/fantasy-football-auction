from csv import reader

from fantasy_football_auction.position import Position


class Player:
    """
    Represents an individual draftable player who has a Position,
    name, id, and value (as in how good they are to have on your team)
    """

    def __init__(self, name, position, value):
        """
        :param name: name of this player
        :param position: Position this player plays
        :param value: integer value of this player (how good they are)
        """
        self.name = name
        self.position = position
        self.value = value


def players_from_fantasypros_cheatsheet(file):
    """
    :param file: path to the file containing the player values in the standard
    CSV format used for fantasypros cheatsheets
    :return: a list of Players based on the info in the cheatsheet
    """

    with open(file, newline='') as csvfile:
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
                players.append(Player(name, position, value))
                playerindex += 1
            linecount += 1
    return players
