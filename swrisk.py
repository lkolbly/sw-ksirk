import collections
import statistics
import random

# The falcon and executor slots are used to store the hitpoints
ShipCounter = collections.namedtuple("ShipCounter", "xwing, ywing, bwing, falcon, tie, executor")
emptyShipCounter = ShipCounter(0,0,0,0,0,0)
xwingGroup = ShipCounter(5,0,0,0,0,0)
ywingGroup = ShipCounter(0,4,0,0,0,0)
bwingGroup = ShipCounter(0,0,3,0,0,0)
tieGroup = ShipCounter(0,0,0,0,4,0)

SHIP_TOUGHNESS = (3, 4, 5, 5, 3, 5)

def selectGroup(ships, shipType, shipCount=1000):
    res = [0]*6
    res[shipType] = min(shipCount, ships[shipType])
    return ShipCounter._make(res)

def canOverlap(shipsA, shipsB):
    rebelsA = shipsA[0] + shipsA[1] + shipsA[2] + shipsA[3]
    empireA = shipsA[4] + shipsA[5]
    rebelsB = shipsB[0] + shipsB[1] + shipsB[2] + shipsB[3]
    empireB = shipsB[4] + shipsB[5]
    if rebelsA > 0 and empireB > 0:
        return False
    if empireA > 0 and rebelsB > 0:
        return False
    # Assume A and B are already internally consistent
    return True

# Each node contains the adjacent nodes
BOARD = [
    # The six mothership locations (start: 0)
    (6,),
    (7,),
    (7,),
    (8,),
    (8,),
    (9,),

    # The outer ring (6)
    (0, 7, 14, 15),
    (1, 2, 6, 15, 16, 8),
    (3, 4, 7, 16, 17, 9),
    (5, 8, 17, 10),

    (9, 17, 18, 19, 11),
    (10, 19, 12),
    (11, 19, 20, 13),
    (12, 20, 14),
    (13, 20, 21, 15, 6),

    # The middle ring (15)
    (6, 7, 16, 23, 22, 21, 14),
    (7, 8, 17, 23, 15),
    (8, 9, 10, 18, 24, 23, 16),
    (10, 19, 25, 24, 17),
    (10, 11, 12, 20, 26, 25, 18),
    (12, 13, 14, 21, 27, 26, 19),
    (14, 15, 22, 27, 20),

    # The inner ring (22)
    (15, 23, 27, 21),
    (15, 16, 17, 24, 22),
    (17, 18, 25, 23),
    (18, 19, 26, 24),
    (19, 20, 27, 25),
    (20, 21, 22, 26),
]

# All of the actions and their cards
IMPERIAL_ACTIONS = [
    ("move", 4), # Move ties (or spawn ties)
    ("move", 5), # Move executor
    ("deathstar",), # Fire death star
    ("lightsaber", "empire"), # Roll for the empire's lightsaber
    ("lightning",), # Take two off of Luke's health
    ("stormtroopers"), # Apply stormtroopers
]

REBEL_ACTIONS = [
    ("move", 0), # xwings
    ("move", 1), # ywings
    ("move", 2), # bwings
    ("move", 3), # falcon
    ("shield",), # Roll for the shield generator
    ("lightsaber", "rebel"), # Roll for the rebellion lightsaber
    ("hat",), # If nearly done with the lightsaber, get 5 cards
]

IMPERIAL_CARDS = {
    # Executor/lightning
    (1, 4): 2,

    # Executor/stormtrooper
    (1, 5): 4,

    # tie fighter/stormtrooper
    (0, 5): 8,

    # tie fighter/lightsaber
    (0, 3): 6,

    # tie fighter/lightning
    (0, 4): 2,

    # death star/stormtrooper
    (2, 5): 2,

    # death star/lightsaber
    (2, 3): 2,

    # death star/lightning
    (2, 4): 2,

    # death star/executor/lightsaber
    (2, 1, 3): 2,
}

REBEL_CARDS = {
    # Hat/shield
    (6, 4): 1,

    # shield/lightsaber
    (4, 5): 3,

    # xwing/hat
    (0, 6): 1,

    # xwing/lightsaber
    (0, 5): 1,

    # xwing/shield
    (0, 4): 1,

    # ywing/lightsaber
    (1, 5): 4,

    # ywing/shield
    (1, 4): 2,

    # bwing/lightsaber
    (2, 5): 2,

    # bwing/shield
    (2, 4): 1,

    # xwing/ywing/lightsaber
    (0, 1, 5): 1,

    # xwing/ywing/shield
    (0, 1, 4): 1,

    # xwing/bwing/lightsaber
    (0, 2, 5): 1,

    # xwing/bwing/shield
    (0, 2, 4): 2,

    # ywing/bwing/shield
    (1, 2, 4): 1,

    # Falcon/bwing/shield
    (3, 2, 4): 1,

    # Falcon/xwing/lightsaber
    (3, 0, 5): 1,

    # Falcon/xwing/shield
    (3, 0, 4): 1,

    # Falcon/bwing/hat
    (3, 2, 6): 1,

    # Falcon/bwing/lightsaber
    (3, 2, 5): 1,

    # Falcon/ywing/lightsaber
    (3, 1, 5): 1,

    # Falcon/ywing/shield
    (3, 1, 4): 2,
}

def processDeck(cards, actions):
    deck = []
    for k,v in cards.items():
        #print(k,v)
        for _ in range(v):
            card = []
            for actionId in k:
                card.append(actions[actionId])
            deck.append(tuple(card))
            pass
        pass
    return deck

REBEL_CARDS = processDeck(REBEL_CARDS, REBEL_ACTIONS)
IMPERIAL_CARDS = processDeck(IMPERIAL_CARDS, IMPERIAL_ACTIONS)

SHIELD_ROLLS = [
    2, 2, 2, 2, 2, 2, 2, 2, 2,
    3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
    4, 4, 4, 4,
    5, 5
]

class GamePlayer:
    def __init__(self, deck):
        deck = list(deck)
        random.shuffle(deck)
        self.deck = deck[3:]
        self.hand = deck[0:3]
        self.down = []
        self.discard = []

    def deal(self, N):
        if len(self.deck) < N:
            l = self.discard
            random.shuffle(l)
            self.deck = self.deck + l
            self.discard = []
        self.hand = self.deck[0:N] + self.hand
        self.deck = self.deck[N:]

    def getHand(self):
        return self.hand

    def setDownCards(self, cards):
        self.down = cards
        for c in self.down:
            self.hand.remove(c)

    def getBonusCards(self, ncards):
        if len(self.deck) < ncards:
            l = self.discard
            random.shuffle(l)
            self.deck = self.deck + l
            self.discard = []
        bonus = self.deck[0:ncards]
        self.down = bonus + self.down

    def popDownCard(self):
        card = self.down[0]
        del self.down[0]
        self.discard.append(card)
        return card

GameState = collections.namedtuple("GameState", "winner, empire_lightsaber, rebel_lightsaber, shield_position, stormtrooper_count, surviving_motherships, board")

class Game:
    def __init__(self, gs=None):
        self.maxTies = 56
        if gs is not None:
            self.from_state(gs)
        else:
            self.create_new()

    def from_state(self, state):
        self.has_won = state.winner is not None
        self.winner = state.winner
        self.lightsaberPosition = {
            "empire": state.empire_lightsaber,
            "rebel": state.rebel_lightsaber
        }
        self.shieldRolls = list(SHIELD_ROLLS)[state.shield_position:]
        self.stormtroopers = [True]*state.stormtrooper_count + [False]*(len(self.shieldRolls) - state.stormtrooper_count)
        self.survivingMotherships = list(state.surviving_motherships)
        self.board = list(state.board)
        pass

    def to_state(self):
        return GameState(
            winner=self.winner,
            empire_lightsaber=self.lightsaberPosition['empire'],
            rebel_lightsaber=self.lightsaberPosition['rebel'],
            shield_position=len(SHIELD_ROLLS)-len(self.shieldRolls),
            stormtrooper_count=self.stormtroopers.count(True),
            surviving_motherships=tuple(self.survivingMotherships),
            board=tuple(self.board)
        )

    def create_new(self):
        self.has_won = False
        self.winner = None

        self.lightsaberPosition = {
            "empire": 13,
            "rebel": 11
        }

        self.shieldRolls = list(SHIELD_ROLLS)
        self.stormtroopers = [False]*len(self.shieldRolls)

        self.survivingMotherships = [0, 1, 2, 3, 4, 5]

        # The board
        self.board = [emptyShipCounter]*len(BOARD)
        self.board[13] = ShipCounter(0, 0, 0, 0, 0, 8)
        self.board[15] = ShipCounter(5, 0, 0, 6, 0, 0)

        # The imperial ships
        self.board[12] = tieGroup
        self.board[11] = tieGroup
        self.board[20] = tieGroup
        self.board[19] = tieGroup
        self.board[26] = tieGroup
        self.board[27] = tieGroup

        # The rebel ships
        self.board[8] = xwingGroup
        self.board[1] = xwingGroup
        self.board[5] = xwingGroup
        #self.board[15] = xwingGroup

        self.board[0] = ywingGroup
        self.board[3] = ywingGroup
        self.board[7] = ywingGroup
        self.board[17] = ywingGroup

        self.board[2] = bwingGroup
        self.board[4] = bwingGroup
        self.board[16] = bwingGroup
        self.board[9] = bwingGroup
        pass

    def enumerate_attacks(self, sofar, ships, pos):
        for attpos in BOARD[pos]:
            if not canOverlap(ships, self.board[attpos]):
                yield sofar + [('attack', ships, attpos)]
                pass

        # We could also attack nowhere
        yield sofar

        # We might be able to attack the death star
        if ships[0] + ships[1] + ships[2] + ships[3] > 0 and len(self.shieldRolls) == 0 and pos >= 22:
            yield sofar + [('attack_deathstar', ships)]
        pass

    # Generate all possible actions on the given card
    def enumerate_actions(self, card):
        yield [] # The no-op action
        for action in card:
            if action[0] == 'move':
                # Falcon and executor move twice, treat them specially
                if action[1] == 3 or action[1] == 5:
                    start = None
                    ships = None
                    for pos,s in enumerate(self.board):
                        if s[action[1]] > 0:
                            start = pos
                            ships = s
                            break
                    if ships == None:
                        return

                    for pos in BOARD[start]:
                        if pos < 6:
                            continue
                        sofar = [('move', start, ships, pos)]

                        # We could move just once, and then attack
                        for attack_action in self.enumerate_attacks(sofar, ships, pos):
                            yield attack_action

                        # We could move one more time
                        for pos2 in BOARD[pos]:
                            if pos2 < 6:
                                continue
                            sofar2 = sofar + [('move', pos, ships, pos2)]

                            # We could attack
                            for attack_action in self.enumerate_attacks(sofar2, ships, pos2):
                                yield attack_action

                            # Or we could stop
                            yield sofar2

                        # Or, we could just move once and stop
                        yield sofar
                    return

                # Find all the possible groups we could move
                for pos,ships in enumerate(self.board):
                    if ships[action[1]] > 0:
                        movingShips = selectGroup(ships, action[1])
                        # Find all the places we could move to
                        for npos in BOARD[pos]:
                            # If npos is a mothership, then we can't move there
                            if npos < 6:
                                continue
                            if canOverlap(movingShips, self.board[npos]):
                                # We could move any number of ships
                                for i in range(1,movingShips[action[1]]+1):
                                    tomove = selectGroup(movingShips, action[1], i)
                                    for attack_action in self.enumerate_attacks([('move', pos, tomove, npos)], tomove, npos):
                                        yield attack_action

                # We could also spawn 4 tie fighters
                if action[1] == 4 and self.maxTies - self.shipCount().tie > 4:
                    for epos,ships in enumerate(self.board):
                        if ships.executor > 0:
                            for attack_action in self.enumerate_attacks([('spawn', epos)], ShipCounter(0,0,0,0,4,0), epos):
                                yield attack_action

                            # Or, just spawn and do nothing
                            yield [('spawn', epos)]
                            break
            elif action[0] == 'deathstar':
                # If there are still motherships, we must hit them first
                if len(self.survivingMotherships) > 0:
                    for i in self.survivingMotherships:
                        yield [('fire_deathstar', i)]
                    pass
                else:
                    # We can hit anywhere with rebel ships
                    for pos,ships in enumerate(self.board):
                        if ships[0] + ships[1] + ships[2] + ships[3] > 0:
                            yield [('fire_deathstar', pos)]
                        pass
                    pass
            elif action[0] == 'lightsaber':
                if self.lightsaberPosition[action[1]] > 0:
                    yield [('lightsaber', action[1])]
            elif action[0] == 'lightning':
                if self.lightsaberPosition['empire'] > 0:
                    yield [('lightning',)]
            elif action[0] == 'hat':
                if self.lightsaberPosition['rebel'] <= 3:
                    yield [('hat',)]
            elif action[0] == 'stormtroopers':
                if self.stormtroopers.contains(False) and self.stormtroopers.count(True) < 9 and len(self.shieldRolls) > 0:
                    yield [('stormtroopers',)]
            elif action[0] == 'shield':
                if len(self.shieldRolls) > 0:
                    yield [('shield',)]
            pass
        pass

    # This is from the more detailed action in enumerate_actions
    def perform_action(self, action):
        if action[0] == 'move':
            self.moveShips(action[2], action[1], action[3])
        elif action[0] == 'spawn':
            self.board[action[1]] = ShipCounter(
                self.board[action[1]][0],
                self.board[action[1]][1],
                self.board[action[1]][2],
                self.board[action[1]][3],
                self.board[action[1]][4] + 4,
                self.board[action[1]][5],
            )
        elif action[0] == 'attack':
            had_falcon = self.board[action[2]].falcon > 0
            #print("Attacking")
            self.attack(action[1], action[2])
            bonus = 0
            if sum(self.board[action[2]]) == 0:
                #self.players[self.cur_player].getBonusCards(1)
                bonus += 1
            if self.board[action[2]].falcon == 0 and had_falcon:
                #self.players[self.cur_player].getBonusCards(2)
                bonus += 2
            return bonus
        elif action[0] == 'attack_deathstar':
            if action[1].falcon > 0:
                roll = rollDice(2)
            else:
                roll = rollDice(sum(action[1]))
            if 6 in roll:
                print("The rebellion won the game!")
                self.has_won = True
                self.winner = "rebel"
            pass
        elif action[0] == 'fire_deathstar':
            roll = rollDice(2)
            if 5 in roll or 6 in roll:
                bonusCards = 0
                if action[1] < 6:
                    self.survivingMotherships.remove(action[1])
                else:
                    # If it has the falcon, we get two extra
                    if self.board[action[1]].falcon > 0:
                        bonusCards += 2
                        #self.players[self.cur_player].getBonusCards(2)
                    #self.players[self.cur_player].getBonusCards(1)
                    bonusCards += 1
                self.board[action[1]] = ShipCounter(0,0,0,0,0,0)
                return bonusCards
            pass
        elif action[0] == 'lightsaber':
            roll = rollDice(4)
            tot = roll.count(4) + roll.count(5) + roll.count(6)
            return self.advanceLightsaber(tot, action[1])
        elif action[0] == 'lightning':
            return self.advanceLightsaber(2, 'empire')
        elif action[0] == 'hat':
            return self.advanceLightsaber(4, 'rebel', True) # 4 should be enough for the hat range
        elif action[0] == 'stormtroopers':
            idx = self.stormtroopers.index(False)
            cnt = 0
            while self.stormtroopers.count(True) < 9 and cnt < 3:
                self.stormtroopers[idx+cnt] = True
                cnt += 1
            pass
        elif action[0] == 'shield':
            roll = rollDice(5)
            while len(self.shieldRolls) > 0:
                torm = -1
                nextval = self.shieldRolls[0]
                if self.stormtroopers[0]:
                    nextval += 1
                for r in roll:
                    if r >= nextval:
                        torm = r
                        pass
                if torm >= 0:
                    roll.remove(torm)
                    self.stormtroopers = self.stormtroopers[1:]
                    self.shieldRolls = self.shieldRolls[1:]
                else:
                    break
            pass
        pass

    def perform_actions(self, actions):
        for a in actions:
            self.perform_action(a)

        # See if the empire has won
        sc = self.shipCount()
        nrebel = sc[0] + sc[1] + sc[2] + sc[3]
        if nrebel == 0 and not self.has_won:
            print("The empire won the game!")
            self.has_won = True
            self.winner = "empire"

    def shipCount(self):
        cnt = [0]*6
        for ships in self.board:
            for i in range(6):
                cnt[i] += ships[i]
        return ShipCounter._make(cnt)

    def advanceLightsaber(self, amt, side, isExtra=False):
        if self.lightsaberPosition[side] > 0:
            self.lightsaberPosition[side] -= amt
            if self.lightsaberPosition[side] <= 0:
                # Distribute bonus cards
                ncards = 4
                if side == "rebel":
                    ncards = 3
                    if isExtra:
                        ncards = 5
                #self.players[self.cur_player].getBonusCards(ncards)
                return ncards
        return 0

    def moveShips(self, ships, src, dst):
        self.board[dst] = ShipCounter(
            self.board[dst][0] + ships[0],
            self.board[dst][1] + ships[1],
            self.board[dst][2] + ships[2],
            self.board[dst][3] + ships[3],
            self.board[dst][4] + ships[4],
            self.board[dst][5] + ships[5],
        )
        self.board[src] = ShipCounter(
            self.board[src][0] - ships[0],
            self.board[src][1] - ships[1],
            self.board[src][2] - ships[2],
            self.board[src][3] - ships[3],
            self.board[src][4] - ships[4],
            self.board[src][5] - ships[5],
        )

    def attack(self, ships, tgt):
        # TODO: Work in the priority system
        destroyed = [0,0,0,0,0,0]
        if ships.executor > 0:
            roll = rollDice(4)
        elif ships.falcon > 0:
            roll = rollDice(2)
        else:
            roll = rollDice(sum(ships))
        for r in roll:
            for i in range(6):
                if SHIP_TOUGHNESS[i] <= r and self.board[tgt][i] > 0:
                    destroyed[i] += 1
                    break
            pass
        #print(destroyed)
        #print("%s destroyed by %s"%(ShipCounter._make(destroyed), ships))
        self.board[tgt] = ShipCounter(
            max(0, self.board[tgt][0] - destroyed[0]),
            max(0, self.board[tgt][1] - destroyed[1]),
            max(0, self.board[tgt][2] - destroyed[2]),
            max(0, self.board[tgt][3] - destroyed[3]),
            max(0, self.board[tgt][4] - destroyed[4]),
            max(0, self.board[tgt][5] - destroyed[5]),
        )
        return destroyed

# Choose from the actions randomly
class RandomAgent:
    def __init__(self):
        pass

    def newGame(self):
        pass

    def pickDownCards(self, game, hand):
        return [hand[0], hand[1], hand[2]]

    def pickAction(self, game, actions):
        return random.choice(actions)

    def feedback(self, startState, card, action, endState, bonusCards):
        pass

    def roundFeedback(self, startState, hand, chosenCards, endState):
        pass

# Value actions that attack.
class AttackAgent:
    def __init__(self):
        pass

    def newGame(self):
        pass

    def pickDownCards(self, game, hand):
        return [hand[0], hand[1], hand[2]]

    def pickAction(self, game, actions):
        attackActions = []
        for a in actions:
            if 'attack' in list(map(lambda x: x[0], a)):
                attackActions.append(a)
        if len(attackActions) > 0:
            return random.choice(attackActions)
        return random.choice(actions)

    def feedback(self, startState, card, action, endState, bonusCards):
        pass

    def roundFeedback(self, startState, hand, chosenCards, endState):
        pass

# Value actions that advance the shield, and then value actions that attack DS
class ShieldAgent:
    def __init__(self):
        pass

    def newGame(self):
        pass

    def pickDownCards(self, game, hand):
        return [hand[0], hand[1], hand[2]]

    def pickAction(self, game, actions):
        #print(len(actions))
        if len(game.shieldRolls) > 0:
            shieldActions = []
            for a in actions:
                if 'shield' in list(map(lambda x: x[0], a)):
                    shieldActions.append(a)
            if len(shieldActions) > 0:
                return random.choice(shieldActions)
            return random.choice(actions)

        # Prefer attacking the death star
        attackDsActions = []
        attackActions = []
        for a in actions:
            if 'attack_deathstar' in list(map(lambda x: x[0], a)):
                attackDsActions.append(a)
            if 'attack' in list(map(lambda x: x[0], a)):
                attackActions.append(a)
        if len(attackDsActions) > 0:
            return random.choice(attackDsActions)
        if len(attackActions) > 0:
            return random.choice(attackActions)
        return random.choice(actions)

    def feedback(self, startState, card, action, endState, bonusCards):
        pass

    def roundFeedback(self, startState, hand, chosenCards, endState):
        pass

# Run two agents against each other, 1v1
class HeadlessAgentGame:
    def __init__(self, rebelAgent, empireAgent):
        self.rebel_agent = rebelAgent
        self.empire_agent = empireAgent

    def do_round(self):
        # Deal three to each player
        self.rebel_player.deal(3)
        self.empire_player.deal(3)

        # Remember the state of the game
        round_start_state = self.game.to_state()
        empireStartHand = list(self.empire_player.getHand())
        rebelStartHand = list(self.rebel_player.getHand())

        # Pick the three down cards
        empireDownCards = list(self.empire_agent.pickDownCards(self.game, self.empire_player.getHand()))
        rebelDownCards = list(self.rebel_agent.pickDownCards(self.game, self.rebel_player.getHand()))
        self.rebel_player.setDownCards(rebelDownCards)
        self.empire_player.setDownCards(empireDownCards)

        # Continue until nobody has any more cards, or the game is won
        while (len(self.rebel_player.down) > 0 or len(self.empire_player.down) > 0) and not self.game.has_won:
            if len(self.rebel_player.down) > 0:
                player = self.rebel_player
                agent = self.rebel_agent
            if len(self.empire_player.down) > 0:
                player = self.empire_player
                agent = self.empire_agent
            card = player.popDownCard()
            s1 = self.game.to_state()
            possible_actions = list(self.game.enumerate_actions(card))

            # Now pick an action and execute it
            action = agent.pickAction(self.game, possible_actions)
            bonusCards = self.game.perform_actions(action)
            if bonusCards is None:
                bonusCards = 0
            if bonusCards > 0:
                player.getBonusCards(bonusCards)
            agent.feedback(Game(s1), card, action, self.game, bonusCards)
            self.num_turns += 1

        # Give feedback on the whole round
        self.empire_agent.roundFeedback(Game(round_start_state), empireStartHand, empireDownCards, self.game)
        self.rebel_agent.roundFeedback(Game(round_start_state), rebelStartHand, rebelDownCards, self.game)
        pass

    def play(self):
        self.game = Game()
        self.rebel_player = GamePlayer(REBEL_CARDS)
        self.empire_player = GamePlayer(IMPERIAL_CARDS)
        self.rebel_agent.newGame()
        self.empire_agent.newGame()
        self.num_turns = 0

        while not self.game.has_won:
            self.do_round()
            #st = self.game.to_state()
            #self.game = Game(st)
            print(self.game.shipCount())
        self.winner = self.game.winner
        return self.num_turns

def rollDice(ndice):
    l = []
    for i in range(ndice):
        l.append(random.randint(1,6))
    return l

def testAgents(rebelAgent, empireAgent, ntests=100):
    winners = {
        'empire': 0,
        'rebel': 0
    }
    nturns_history = []
    ra = rebelAgent
    ea = empireAgent
    for i in range(ntests):
        #g = Game()
        #g.do_game()
        g = HeadlessAgentGame(ra, ea)
        nturns = g.play()
        winners[g.winner] += 1
        #nturns_hist[nturns] = nturns_hist.get(nturns, 0) + 1
        nturns_history.append(nturns)

    return winners, statistics.median(nturns_history)

def simulateShieldRolls(stormtroopers=False):
    rolls = list(SHIELD_ROLLS)
    if stormtroopers:
        for i in range(len(rolls)):
            rolls[i] += 1
    cnt = 0
    #print(rolls, len(rolls))
    while len(rolls) > 0:
        cnt += 1
        roll = rollDice(5)
        roll.sort()
        #print(roll)

        while len(rolls) > 0:
            torm = -1
            nextval = rolls[0]
            for r in roll:
                if r >= nextval:
                    torm = r
            if torm >= 0:
                roll.remove(torm)
                rolls = rolls[1:]
            else:
                break
        #print(rolls, len(rolls))
        pass
    return cnt

def findExpectedShieldRolls(N=1000):
    cnts = []
    for i in range(N):
        cnts.append(simulateShieldRolls(False))
    print(sum(cnts)/float(N))

    cnts = []
    for i in range(N):
        cnts.append(simulateShieldRolls(True))
    print(sum(cnts)/float(N))
    pass

if __name__ == "__main__":
    winners, medianTurns = testAgents(ShieldAgent(), AttackAgent())
    print(winners)
    print("Median turns: %d"%medianTurns)
