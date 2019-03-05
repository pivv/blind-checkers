# Blind Checkers

**This repository is related to the term project of Computational Modeling class in Seoul National University.** The goal of the project is to create an artificial intelligence of **Blind Checkers** to be explained. Anyone who does not attend the class can also enjoy Blind Checkers through this repository.

## Introduction

[https://en.wikipedia.org/wiki/Draughts](https://en.wikipedia.org/wiki/Draughts)

The Blind Checkers is a variation of the Checkers. It is almost similar to international Checkers, except you cannot see all of your opponents. More precisely, each piece in Blind Checkers has own field of view, and you cannot see anything out of sight. Therefore, not only capturing opponent pieces but securing a broad view will be an important strategy.

<img src="https://github.com/pivv/blind-checkers/blob/master/images/image_blind_checkers.PNG" width="500">

## Rules

You can adjust all of the detailed rules by modifying the constants.

* 10x10 Checkers board
* Two spaces of view for both men and kings (It means that 5x5 box centered at each piece is visible.)
* Three spaces of attack range for kings (You have additional view for attack range. 1 corresponds to no flying kings rule, and 9 corresponds to flying kings rule.)
* Mandatory capture if possible
* Men can capture backwards

In practice, the attack range of kings is limited since flying kings are too strong in Blind Checkers. As in the international rules, removal of captured pices is done after one turn is all over. But unlike the international rules, you can choose any sequence of capture since you cannot see all path before capturing. Finally, since you cannot see all board in Blind Checkers, the "threefold repetition" rule is excluded. The "fourty-move" rule is implemented, but as you may not know opponent's promotion, a draw is declared if there was no capture during last fourty moves for both players.

## Usage

The implementation is done with [pygame](https://www.pygame.org), so you should install pygame first. Then download the project, and do ``python blind_checkers.py`` to start the game. Currently no installation is provided, and you can test with various rules or AIs by adjusting ``"blind_checkers/constants.py"``.

## Environment

This repository is based on [OpenAI Gym](https://github.com/openai/gym), and the main [Checkers](https://github.com/pivv/blind-checkers/blob/master/blind_checkers/game.py) object plays the role of environment. It has similar functions as in [OpenAI Gym](https://github.com/openai/gym), except for some differences.

* ``reset(self)``: Reset the environment's state. Returns next player, observation, legal moves, and info.
* ``step(self, action)``: Step the environment by one timestep. Returns next player, observation, legal moves, reward, done, and info.
* ``render(self)``: Render one frame of the environment.
* ``print(self, font_size, color)``: Print the message to the screen. If visualize is set to False, this function just uses built-in ``print()`` function.

When initializing the ``Checkers`` object, you can select whether to visualize the board to human-friendly UI. You can choose from four ways to visualize.

* ``"dark"``: You can show only dark sides. (When you play yourself at dark side, be sure to use this option.)
* ``"light"``: You can show only light sides. (When you play yourself at light side, be sure to use this option.)
* ``"both"``: You can show both sides with limited view alternatively. (Implemented for pvp mode.)
* ``"no-blind"``: You can show all of the board. (Observer mode, watch the battle between AIs!)

The following code is an example of a match between person and AI.

```python
from blind_checkers.rule import Rule
from blind_checkers.board import Board
from blind_checkers.graphics import Graphics
from blind_checkers.game import Checkers

from blind_checkers.agents.Random.agent import RandomAgent
from blind_checkers.agents.Greedy.agent import GreedyAgent
from blind_checkers.agents.Human.agent import HumanAgent

# Set rules.
rule = Rule({
    'board_size': 10,
    'sight': 2,
    'king_sight': 2,
    'king_range': 2,
    'force_capture': True,
    'backward_capture': True
    })

# Load graphics.
graphics = Graphics(rule)

agent_dark = GreedyAgent(1, rule)
agent_light = HumanAgent(-1, rule, graphics) # Human agent needs graphics.

# Main loop.
env = Checkers(rule, graphics=graphics, visualize=True, visualize_type='light')

player, obs, moves, info = env.reset()
env.print("Game Start", font_size=72)
done = 0

while done == 0:
    if player == 1:
        current_agent = agent_dark
    else:
        assert(player == -1)
        current_agent = agent_light

    action = current_agent.act(obs, moves, info)
    player, obs, moves, rew, done, info = env.step(action)
    current_agent.consume(rew)

    env.render()

    if done > 0: # game is ended.
        if done == 2: # draw
            env.print("Draw", font_size=72)
        else:
            assert(done == 1)
            env.print("{} Win".format(current_agent), font_size=56)

env.close()
```

``step`` function gets ``action`` of form ``(from_pos, to_pos)`` where ``from_pos`` is a location of current piece, and ``to_pos`` is a destination to go. Then the function returns six variables: ``player``, ``obs``, ``moves``, ``rew``, ``done``, ``info``.

* ``player`` is the next player to play: ``1`` means dark side, and ``-1`` means light side. It may same to previous ``player``!
* ``obs`` is the current observation of Checkers board to ``player``. It is in the form of 2D numpy array. In default, ``0`` is for empty space, ``1``(``-1``) is for dark(light) man, ``2``(``-2``) is for dark(light) king, and ``3`` is for an invisible space.
* ``moves`` is the collection of all legal moves. It is a ``list`` of ``(from_pos, legal_moves)`` where ``legal_moves`` is again a ``list`` of multiple ``to_pos`` which is valid to arrive on departure from ``from_pos``. So, you should choose ``action`` among ``moves``.
* ``rew`` contains the information related to reward during last movement. ``rew["capture-man"]``(``rew["capture-king"]``) stores whether you captured opponent man(king) in last move, ``rew["promotion"]`` stores whether your uncrowned piece promoted to king in last move, and ``rew["win"]``(``rew["draw"]``) stores whether the game is ended with your victory(draw). You can use this to create your own reward. (For example, see ``GreedyAgent``.)
* ``done`` let you know whether the game is over. ``0`` means game is not over yet, ``1`` means ``player`` wins, and ``2`` means draw.
* ``info`` contains additional information of the game. ``info["prev-obs"]`` contains the previous observations during opponent's turn. ``info["move-count"]`` contains the count of previous moves without capture and promotion. If this count reach to 80, It becomes draw.

## Agents

Each agent plays the Checkers game. In this repository three types of basic agents are provided: [HumanAgent](https://github.com/pivv/blind-checkers/blob/master/blind_checkers/agents/Human/agent.py), [RandomAgent](https://github.com/pivv/blind-checkers/blob/master/blind_checkers/agents/Random/agent.py), and [GreedyAgent](https://github.com/pivv/blind-checkers/blob/master/blind_checkers/agents/Greedy/agent.py).

* ``HumanAgent`` is the agent that leaves choice to a person. This agent is not limited in ability!
* ``RandomAgent`` is the agent that performs randomly among the available actions.
* ``GreedyAgent`` is the simple AI that first assumes that there are no pieces in blind reasons, then performs a Monte-Carlo simulation for each available actions (by using ``RandomAgent``), and finally chooses the action with best reward.

You can also create your own agent and compete it with existing agents. Especially using deep reinforcement learning to create agents is the goal of the term project.

## Resources

You can use your own images for Checkers board or pieces by put them into the ``"blind_checkers/resources/"`` folder. (You can also change the font.) As an example, icons purchased from [iconfinder](https://www.iconfinder.com/icons/3813566/boardgames_checkers_draughts_games_king_crown_king_piece_monopoly_icon) are used as pieces.

<img src="https://github.com/pivv/blind-checkers/blob/master/images/image_customized_blind_checkers.PNG" width="500">

## References

Much of this repository have been referred to [OpenAI Gym](https://github.com/openai/gym), [Seoul AI Gym](https://github.com/seoulai/gym), and [Pygame-Checkers](https://github.com/everestwitman/Pygame-Checkers).
