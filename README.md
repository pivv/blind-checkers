# Blind Checkers

**This repository is related to the term project of Computational Modeling class in Seoul National University.** The goal of the project is to create an artificial intelligence of "Blind Checkers" to be explained. Anyone who does not attend the class can also enjoy Blind Checkers through this repository.

## Introduction

[https://en.wikipedia.org/wiki/Draughts](https://en.wikipedia.org/wiki/Draughts)

The Blind Checkers is a variation of the Checkers. It is almost similar to international Checkers, except you cannot see all of your opponents. More precisely, each piece in Blind Checkers has own field of view, and you cannot see anything out of sight. Therefore, not only catching opponent pieces but securing a broad view will be an important strategy.

## Rules

You can adjust all of the detailed rules by modifying the constants.

* 10x10 Checkers board
* Two spaces of view for both men and kings (It means that 5x5 box centered at each piece is visible.)
* Two spaces of attack range for kings (1 corresponds to no flying kings rule, and 9 corresponds to flying kings rule.)
* Mandatory capture if possible
* Men can capture backwards

In practice, the attack range of kings is limited since flying kings are too strong in Blind Checkers. Also, for easy implementation, any captured pieces are removed from the board immediately, unlike the international rules in which removal is done after one turn is over. Finally, since you cannot see all board in Blind Checkers, the "threefold repetition" rule is excluded. The "fourty-move" rule is implemented.

## Usage

The implementation is done with pygame, so you should install pygame to 

## Environment

This repository is based on [OpenAI Gym](https://github.com/openai/gym), and the main ``Checkers`` object plays the role of environment. It has similar functions as in [OpenAI Gym](https://github.com/openai/gym), except for some differences.

* reset(self): Reset the environment's state. Returns next player, observation, legal moves, and info.
* step(self, action): Step the environment by one timestep. Returns next player, observation, legal moves, reward, done, and info.
* render(self): Render one frame of the environment.

When initializing the ``Checkers`` object, you can select whether to visualize the board to human-friendly UI. You can choose from four ways to visualize.

* "dark": You can show only dark sides. (When you play yourself at dark side, be sure to use this option.)
* "light": You can show only light sides. (When you play yourself at light side, be sure to use this option.)
* "both": You can show both sides with limited view alternatively. (Implemented for pvp mode.)
* "no-blind": You can show all of the board. (Observer mode, watch the battle between AIs!)

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
    'force_catch': True,
    'backward_catch': True
    })

# Load graphics.
graphics = Graphics(rule)

agent_dark = GreedyAgent(1, rule)
agent_light = HumanAgent(-1, rule, graphics) # Human agent needs graphics.

# Main loop.
env = Checkers(rule, graphics=graphics, visualize=True, visualize_type='light')

player, obs, moves, info = env.reset()
env.print("Game Start", font_size=72)
env_done = False

while not env_done:
    if player == 1:
        current_agent = agent_dark
    else:
        assert(player == -1)
        current_agent = agent_light

    action = current_agent.act(obs, moves, info)
    player, obs, moves, rew, env_done, info = env.step(action)
    current_agent.consume(rew)

    env.render()

    if env_done > 0: # game is ended.
        if env_done == 2: # draw
            env.print("Draw", font_size=72)
        else:
            assert(env_done == 1)
            env.print("{} Win".format(current_agent), font_size=56)

env.close()
```

The observation of 

## Agents

Each agent plays the Checkers game. In this repository three types of basic agents are provided: HumanAgent, RandomAgent, GreedyAgent.

* HumanAgent is the agent that leaves choice to a person. This agent is not limited in ability!
* RandomAgent is the agent that performs randomly among the available actions.
* GreedyAgent is the simple AI that first assumes that there are no pieces in blind reasons, then performs a Monte-Carlo simulation for each available actions (by using RandomAgent), and finally chooses the action with best reward.

You can also create your own agent and compete it with existing agents. Especially using deep reinforcement learning to create agents is the goal of the term project.

## Resource

You can use your own images for Checkers board or pieces by put them in the resource folder.

## References

Much of this repository have been referred to [OpenAI Gym](https://github.com/openai/gym), [Seoul AI Gym](https://github.com/seoulai/gym), and [Pygame-Checkers](https://github.com/everestwitman/Pygame-Checkers).
