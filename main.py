import pygame
import neat
import os
import sys
import random
import math
import pickle

# Game Constants
GRID_SIZE = 8
PLAYER_SIZE = 8
STEP_SIZE = 8  
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

class TronGame:
    def __init__(self, genome1, net1, genome2, net2):
        self.genome1 = genome1
        self.net1 = net1
        self.genome2 = genome2
        self.net2 = net2
        
        # Directions pool (alined with the grid)
        directions = [(STEP_SIZE, 0), (-STEP_SIZE, 0), (0, STEP_SIZE), (0, -STEP_SIZE)]

        p1_x = random.randrange(50, 1150, GRID_SIZE)
        p1_y = random.randrange(200, SCREEN_HEIGHT - 200, GRID_SIZE)
        self.p1 = pygame.Rect((p1_x, p1_y, PLAYER_SIZE, PLAYER_SIZE))
        self.p1_dir = random.choice(directions) 
        self.p1_trail = []
        
        p2_x = random.randrange(50, 1150, GRID_SIZE)
        p2_y = random.randrange(200, SCREEN_HEIGHT - 200, GRID_SIZE)
        self.p2 = pygame.Rect((p2_x, p2_y, PLAYER_SIZE, PLAYER_SIZE))
        self.p2_dir = random.choice(directions) 
        self.p2_trail = []

        while p2_x+0<=p1_x <= p2_x + 50 or p2_x+0<=p1_x == p2_x + 50:
        # Player 1: Spawns
        # spawns randomly but not too close to player 2
            p1_x = random.randrange(50, 1150, GRID_SIZE)
            p1_y = random.randrange(200, SCREEN_HEIGHT - 200, GRID_SIZE)
            self.p1 = pygame.Rect((p1_x, p1_y, PLAYER_SIZE, PLAYER_SIZE))
            self.p1_dir = random.choice(directions) 
            self.p1_trail = []
        
        # Player 2: Spawns
        # spawns randomly but not too close to player 1
            p2_x = random.randrange(50, 1150, GRID_SIZE)
            p2_y = random.randrange(200, SCREEN_HEIGHT - 200, GRID_SIZE)
            self.p2 = pygame.Rect((p2_x, p2_y, PLAYER_SIZE, PLAYER_SIZE))
            self.p2_dir = random.choice(directions) 
            self.p2_trail = []

            
        # Turn counters
        self.p1_consecutive_turns = 0
        self.p2_consecutive_turns = 0
        self.p1_last_turn = 0 
        self.p2_last_turn = 0
        
        self.frame_count = 0
        self.max_frames = 1000  