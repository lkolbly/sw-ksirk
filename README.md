# sw-ksirk
Game dynamic simulator for the Star Wars Risk board game. (Note: I'm not related to Hasbro in any way, except that I own a copy of the game)

This module simulates all of the game dynamics of Risk: Star Wars Edition (this one: https://www.amazon.com/Risk-Star-Wars-Edition-Game/dp/B00SDJG59K).

It's designed to be useful for building AI agents - indeed, I use it as a testbed for teaching myself AI. Scroll to the bottom for the API.

## Game Rules

The game takes place in 3 battles, termed the shield generator, the lightsaber battle (or the "throne room"), and the space battle.

The goal of the Rebellion is to successfully attack the death star. The goal of the Empire is to prevent this. The Empire can win by destroying all of the Rebellion's ships - then the Rebellion has no ships to attack the Death Star with (the opposite is not true. If the Rebellion destroys all of the Empire's ships, the Empire can still win with the Death Star).

There are (nominally) two players, one plays as the Rebellion and the other as the Empire. Each has a deck of 30 "action cards", from which they draw a hand of 6.

Each action card has two or three possible actions on it. When an action card is played, any one (but at most one) of the shown actions can be played. (the different types of actions will be covered below)

The game then progresses in rounds, until the game is complete. In each round:
* Each player chooses 3 action cards to execute in that round, and places them face-down in the "order stack".
* The players alternate (Rebellion going first) turning over a action card (from the 3 that they selected) and playing one of the actions on it and moving the card to the discard pile (they may choose not to play any of the actions, but they still discard that card).
* If the player gets bonus cards for their actions, they add them to the bottom of their order stack.
* This continues round-robin until all players have no more remaining action cards in their order stack. If a player has no more remaining cards in their order stack, they pass and play continues with the next player with cards in their order stack.
* When everyone's order stack is emptied, each player draws 3 cards from their deck into their hand (shuffling in the discard pile if necessary), and a new round is started.

There are a number of different action cards:
* Ship "move" cards: These cards allow you to move a ship (X-Wing, Y-Wing, B-Wing, TIE Fighter, Falcon, or Executor) and then attack with it. What type of ship you can move varies based on the card - each card action restricts you to moving a single ship type (e.g. you might have a card that says "move X-Wings"). You may move any number of ships of that type, but you may attack with at most the ships you move. For instance, if you move 1 TIE fighter onto a square with 4 TIE fighters, you can only attack with 1 TIE fighter. Also, you may only attack with up to 5 ships. All ships move 1 space, except for the Falcon and the Executor which move up to two spaces.
  * To attack, a 6-sided die is rolled for each attacking ship (except for the Falcon, which attacks with 2 dice, and the Executor, which attacks with 4 dice). Each die can potentially be used to destroy one ship (or deal one damage). Dice which land 3 or above can be used to destroy X-Wings or TIE fighters, 4 or above can be used for Y-Wings, and 5 or 6 can be used to destroy B-Wings or damage the Falcon or the Executor.
  * The Falcon and the Executor each have a number of hitpoints. Once all of their hitpoints are depleted, the ships are destroyed. The Falcon starts with 6 hitpoints and the Executor with 8. If the Falcon is destroyed, the Empire gets 2 bonus cards.
  * If the action is "move TIE fighters", and the Executor is still in play, the Empire may choose to spawn 4 new TIE fighters onto the square the Executor is at, and attack with them. The Empire may have up to 56 TIE fighters in play.
  * If an attack clears the square of all ships, the attacker gets a bonus card.
  * For example: The Empire moves 4 TIE fighters onto a square with 5 TIE fighters, and attacks a square holding 1 X-Wing, 2 B-Wings, and a Falcon with 4 hitpoints left. They roll 4 dice, for each of 4 TIEs attacking, and get 3, 4, 5, 5. The 3 cannot destroy any B-Wings or damage the Falcon, but it can destroy the X-Wing. The 4 is the same, except that if there were a Y-Wing, it could destroy that. Since the 3 is used for the X-Wing, the 4 is useless. The two remaining dice, the 5s, can be used to damage any of the ships. They could both be used to destroy the two remaining B-Wings, or they could both be used to damage the Falcon (which would then have 2 hitpoints), or they could be used to do 1 damage to the Falcon and destroy one B-Wing.
  * If (and only if) the shield generator run is completed, the Rebellion may attack the Death Star from an adjacent space (one on the inner ring). In order to destroy the Death Star, the Rebellion must roll a 6.
* "fire_deathstar" actions are used to fire the Death Star. There are 6 mothership spaces on the board, the Death Star must be used to destroy these before it can target any other sectors. The Death Star attacks with 2 dice, and if either is a 5 or a 6 the attack succeeds and empties the space. Once the 6 motherships spaces have all been destroyed (they must be destroyed, even if there are no ships on them), the Death Star can target any other sector. If the attack succeeds, the sector is cleared and the Empire receives 1 bonus card (+2 if they destroy the Falcon).

The shield generator run consists of a series of spaces, each marked with a number ranging from 2 to 5. The Rebellion starts at one side, and must make it to the last space before they can attack the Death Star.
* "shield" actions allow the Rebellion to roll 5 dice to move. The Rebellion can move one space for each dice they have which is greater than or equal to the value of the space. For example, if the values of the next 6 spaces are 2, 2, 3, 3, 3, 4, and the Rebellion rolls 1, 2, 2, 2, 5, then the rebellion can move past the two "2" spaces (using two "2" dice) and then onto the first "3" space (using the "5" die, since the remaining "2" die is not sufficient to go onto a "3" space.
* "stormtrooper" actions allow the Empire to place "stormtroopers" on the next few spaces in front of the Rebellion, 3 at a time. If there is a stormtrooper on a space, the value of that space is increased by 1. (if the next three spaces are already covered by stormtroopers, the Empire may place 3 stormtroopers on the spaces after those already covered. A space may have at most 1 trooper). The Empire may have at most 9 stormtroopers on the board.

The lightsaber battle consists of two hitpoint counters, one for the Rebellion and one for the Empire. The Rebellion's counter starts at 12, whereas the Empire's counter starts at 13.
* The "lightsaber" action allows the player to roll 4 dice, and deal 1 damage to the opposing side's hitpoint counter for each dice that is 4 or greater.
* The "lightning" action allows the Empire to deal 2 damage immediately to the Rebel's hitpoint counter.
* The "hat" action allows the Rebellion to, if and only if the Empire's counter is at 3 or below, to advance the Empire's hitpoint counter to 0.

If either side's hitpoint counter is at 0, then no more lightsaber actions can be taken. When the Rebellion's counter reaches 0, the Empire gets 4 bonus cards. If the Rebellion takes the Empire's counter to 0 using "lightsaber" actions, they get 3 bonus cards, but if they do it using "hat" actions, they get 5 bonus cards.

## API

If you're doing AI development, the important class is the HeadlessAgentGame class and the Agent interface. The HeadlessAgentGame orchestrates the interactions between the agents and the game to simulate the turns. You instantiate it using two agents, rebel and empire, and then can play games using the play() method:

```python
hag = HeadlessAgentGame(rebelAgent, empireAgent)
nturns = hag.play()
print("Winner was %s!"%hag.winner)
```

You can also use the testAgents function:

```python
winners, medianTurns = testAgents(rebelAgent, empireAgent, ntests=100)
print(winners) # {'rebel': <rebel games won>, 'empire': <imperial games won>}
```

Anywhere that ship counts are mentioned, it refers to a named tuple "ShipCounter", which has a count of each type of ship. For the Falcon and the Executor, for which there is only one ship in the game, the count is instead of the number of hitpoints that ship has. For example:

```python
# Represents 5 X-Wings
ShipCounter(xwing=5, ywing=0, bwing=0, falcon=0, tie=0, executor=0)

# Represents 5 X-Wings and a fully-charged falcon.
ShipCounter(xwing=5, ywing=0, bwing=0, falcon=6, tie=0, executor=0)

# Represents 16 TIE fighters and a heavily damaged executor.
ShipCounter(xwing=0, ywing=0, bwing=0, falcon=0, tie=16, executor=1)
```

The board topology is represented in the global variable "BOARD". Each element is a tuple containing the neighbors that the square is connected to. The first 6 elements are the six motherships, that can be destroyed by the death star.

An Agent doesn't necessarily have to be specialized for one side or another, but to be used in the HeadlessAgentGame it must implement the following methods:

```python
class RandomAgent:
    # Whatever one-time initialization you need to do.
    def __init__(self):
        pass

    # Whatever you need to prepare for a new game.
    def newGame(self):
        pass

    # Select 3 down cards from a hand of 6. The first card played is the last,
    # then the second-to-last, then the first (third-to-last).
    def pickDownCards(self, game, hand):
        return [hand[0], hand[1], hand[2]]

    # Given all of the possible actions, pick one and do it.
    # This agent picks an action uniformly at random.
    def pickAction(self, game, actions):
        return random.choice(actions)

    # Provide feedback on how the action went. Passed the state that was
    # passed to pickAction, the card that pickAction chose an action from,
    # the action that pickAction picked, and the state that we ended up in,
    # as well as the number of bonus cards we got.
    def feedback(self, startState, card, action, endState, bonusCards):
        pass

    # Provide feedback on how the round went. Passed the state passed to
    # pickDownCards, the hand passed to pickDownCards, the cards that it
    # chose, and the state that we ended up in after all cards were played.
    def roundFeedback(self, startState, hand, chosenCards, endState):
        pass
```

The "actions" parameter in pickAction is an enumerated list of all of the possible actions. Each element is itself a list of "sub-actions" for that action (for example, moving and attacking is a single possible action, but constitutes two sub-actions). Each sub-action is a tuple, with the first element denoting the type of the sub-action:
* move: Moves action[2] ships from action[1] to action[3] (action[2] is a ShipCounter).
* spawn: Create 4 TIE fighters at the position of the executor.
* attack: Attacks the tile action[2] with the ships in action[1] (action[1] is a ShipCounter).
* attack_deathstar: Attacks the death star with the ships in action[1] (a ShipCounter).
* fire_deathstar: Fire the deathstar at the given target (action[1]).
* lightsaber: Rolls dice for the lightsaber battle.
* lightning: Applies 2 immediate hits on the lightsaber battle.
* hat: Finishes the lightsaber battle.
* stormtroopers: Add 3 stormtroopers to the shield generator run.
* shield: Roll for the shield generator run.

See the game rules for information about what these mean.
