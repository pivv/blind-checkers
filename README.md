# Blind Checkers

This repository is related to the term project of Computational Modeling class in Seoul National University. The goal of the project is to create an artificial intelligence of "Blind Checkers" to be explained. Anyone who does not attend the class can also play Blind Checkers through this repository.

## Introduction

[https://en.wikipedia.org/wiki/Draughts](https://en.wikipedia.org/wiki/Draughts)

The Blind Checkers is a variation of the Checkers. It is almost similar to international Checkers, except you cannot see all of your opponents. More precisely, each piece in Blind Checkers has own field of view, and you cannot see anything out of sight. Therefore, not only catching opponent pieces but securing a broad view will be an important strategy.

## Rules

You can adjust all of the detailed rules by modifying the constants.

* 10x10 Checkers board
* Two spaces of view for both men and kings (It means that 5x5 box centered at each piece is visible.)
* Two spaces of attack range for kings (1 corresponds to no flying kings rule, and 9 corresponds to flying kings rule.)
* Mandatory capture if possible
* men can capture backwards

In practice, flying kings are too strong in Blind Checkers. Also, for easy implementation, any captured pieces are removed from the board immediately, unlike the international rules in which removal is done after one turn is over.

## Usage

The implementation is done with pygame, so you should install pygame to 

## Environment

This 

## Agents

Each agent plays the Checkers game. In this repository three types of basic agents are provided: HumanAgent, RandomAgent, GreedyAgent.

* HumanAgent is the agent that leaves choice to a person. This agent is not limited in ability!
* RandomAgent is the agent that performs randomly among the available actions.
* GreedyAgent is the simple AI that first assumes that there are no pieces in blind reasons, then performs a Monte-Carlo simulation for each available actions (by using RandomAgent), and finally chooses the action with best reward.

You can also create your own agent and compete it with existing agents. Especially using deep reinforcement learning to create agents is the goal of the term project. 
