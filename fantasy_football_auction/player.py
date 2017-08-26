from csv import reader

from fantasy_football_auction.position import Position


class Player:
    """
    Represents an individual draftable player who has a Position,
    name, id, and value (as in how good they are to have on your team)
    """

    def __init__(self, fid, name, position, value):
        """
        :param fid: (football id) shorthand id integer to use to refer to this player,
            must not overlap with any other player
        :param name: name of this player
        :param position: Position this player plays
        :param value: integer value of this player (how good they are)
        """
        self.fid = fid
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
                rawName = row[0]
                name = rawName[:rawName.find('(') - 1]
                positionText = rawName[rawName.find('(') + 1:rawName.find('-') - 1]
                position = Position[positionText]
                value = int(row[2].replace('$', ''))
                players.append(Player(playerindex, name, position, value))
                playerindex += 1
            linecount += 1
    return players
