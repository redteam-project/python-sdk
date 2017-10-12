import EDB, RedTeamTrello

class RedTeam(object):

    def __init__(self):
        self.EDB = EDB.EDB()
        self.RedTeamTrello = RedTeamTrello.RedTeamTrello()