class Nim:
    def __init__(self, initial=[1, 3, 5, 7]):
        self.piles = initial.copy()
        self.player = 0
        self.winner = None

    @classmethod
    def available_actions(cls, piles):
        actions = set()
        for i, pile in enumerate(piles):
            for j in range(1, pile + 1):
                actions.add((i, j))
        return actions

    @classmethod
    def other_player(cls, player):
        return 0 if player == 1 else 1

    def switch_player(self):
        self.player = Nim.other_player(self.player)

    def move(self, action):
        pile, count = action
        if self.winner is not None:
            raise Exception("Game already won")
        if pile < 0 or pile >= len(self.piles):
            raise Exception("Invalid pile")
        if count < 1 or count > self.piles[pile]:
            raise Exception("Invalid number of objects")

        self.piles[pile] -= count
        self.switch_player()

        if all(pile == 0 for pile in self.piles):
            self.winner = self.player