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

    def look_in_direction(self, start_rect, direction, combined_trails):
        """Measures normalized distance to obstacles (1.0 = wide open, 0.0 = immediate crash)."""
        x, y = start_rect.x, start_rect.y
        dx, dy = direction
        distance = 0.0
        max_vision = 400.0 
        
        while distance < max_vision:
            x += dx
            y += dy
            distance += STEP_SIZE
            
            if x < 0 or x >= SCREEN_WIDTH or y < 0 or y >= SCREEN_HEIGHT:
                break
                
            test_rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
            if test_rect.collidelist(combined_trails) != -1:
                break
                
        # Returns a clear gradient float between 0.0 and 1.0
        return distance / max_vision
    
    def get_inputs(self, player_rect, current_dir, opponent_rect, combined_trails):
        dx, dy = current_dir
        dir_straight = (dx, dy)
        dir_left = (dy, -dx)
        dir_right = (-dy, dx)

        dist_straight = self.look_in_direction(player_rect, dir_straight, combined_trails)
        dist_left = self.look_in_direction(player_rect, dir_left, combined_trails)
        dist_right = self.look_in_direction(player_rect, dir_right, combined_trails)
        
        heading_angle = math.atan2(dy, dx)
        target_angle = math.atan2(opponent_rect.y - player_rect.y, opponent_rect.x - player_rect.x)
        relative_angle = target_angle - heading_angle
        
        while relative_angle > math.pi: relative_angle -= 2 * math.pi
        while relative_angle < -math.pi: relative_angle += 2 * math.pi
        
        enemy_straight = 1.0 if abs(relative_angle) < 0.2 else 0.0
        enemy_left = 1.0 if relative_angle < -0.2 else 0.0
        enemy_right = 1.0 if relative_angle > 0.2 else 0.0
        
        left_right_balance = dist_left - dist_right
        
        # ADDED CURRENT VELOCITY: 9 inputs total now. 
        # Normalized directional headings (-1, 0, or 1) help the network stabilize its outputs
        norm_dx = dx / STEP_SIZE
        norm_dy = dy / STEP_SIZE
        
        return [dist_straight, dist_left, dist_right, enemy_straight, enemy_left, enemy_right, left_right_balance, norm_dx, norm_dy]

    def change_direction(self, current_dir, action):
        dx, dy = current_dir
        if action == 1:    # Turn Left
            return (dy, -dx)
        elif action == 2:  # Turn Right
            return (-dy, dx)
        return current_dir 
    def play_frame(self, screen=None):
        self.frame_count += 1
        combined_trails = self.p1_trail + self.p2_trail
        old_distance = math.hypot(self.p1.x - self.p2.x, self.p1.y - self.p2.y)

        # AI Decisions
        inputs1 = self.get_inputs(self.p1, self.p1_dir, self.p2, combined_trails)
        outputs1 = self.net1.activate(inputs1)
        action1 = outputs1.index(max(outputs1))
        self.p1_dir = self.change_direction(self.p1_dir, action1)

        inputs2 = self.get_inputs(self.p2, self.p2_dir, self.p1, combined_trails)
        outputs2 = self.net2.activate(inputs2)
        action2 = outputs2.index(max(outputs2))
        self.p2_dir = self.change_direction(self.p2_dir, action2)

        # Spin Penalties (Scaled down significantly)
        for act, last, con, gen in [(action1, self.p1_last_turn, self.p1_consecutive_turns, self.genome1), 
                                    (action2, self.p2_last_turn, self.p2_consecutive_turns, self.genome2)]:
            if act in (1, 2):
                con = (con + 1) if act == last else 1
                last = act
                if con >= 4:
                    gen.fitness -= 50.0 # Small penalty, don't break the network
                    con = 0
            else:
                con = 0

        # Move and leave trail
        self.p1_trail.append(self.p1.copy())
        self.p2_trail.append(self.p2.copy())
        self.p1.move_ip(self.p1_dir)
        self.p2.move_ip(self.p2_dir)

        new_distance = math.hypot(self.p1.x - self.p2.x, self.p1.y - self.p2.y)
        
        p1_dead = False
        p2_dead = False
        p1_killed_by_p2 = False
        p2_killed_by_p1 = False

        # Surviving each frame gives a baseline reward
        self.genome1.fitness += 0.1
        self.genome2.fitness += 0.1

        # Chasedown logic (gentle rewards/penalties)
        p1_is_hunting = (inputs1[3] == 1.0)
        p2_is_hunting = (inputs2[3] == 1.0)
        
        if new_distance < old_distance:
            self.genome1.fitness += 0.5 if p1_is_hunting else 0.2
            self.genome2.fitness += 0.5 if p2_is_hunting else 0.2
        else:
            self.genome1.fitness -= 0.1
            self.genome2.fitness -= 0.1

        # Collisions
        if self.p1.left < 0 or self.p1.right > SCREEN_WIDTH or self.p1.top < 0 or self.p1.bottom > SCREEN_HEIGHT:
            p1_dead = True
        if self.p2.left < 0 or self.p2.right > SCREEN_WIDTH or self.p2.top < 0 or self.p2.bottom > SCREEN_HEIGHT:
            p2_dead = True

        if self.p1.collidelist(self.p1_trail) != -1: p1_dead = True
        if self.p2.collidelist(self.p2_trail) != -1: p2_dead = True

        if self.p1.collidelist(self.p2_trail) != -1:
            p1_dead = True
            p1_killed_by_p2 = True
        if self.p2.collidelist(self.p1_trail) != -1:
            p2_dead = True
            p2_killed_by_p1 = True

        if self.p1.colliderect(self.p2):
            p1_dead = True
            p2_dead = True

        # End Game Phase 
        if p1_dead or p2_dead or self.frame_count > self.max_frames:
            if p1_killed_by_p2 and not p2_dead:
                self.genome1.fitness -= 20.0
                self.genome2.fitness += 50.0
            elif p2_killed_by_p1 and not p1_dead:
                self.genome2.fitness -= 20.0
                self.genome1.fitness += 50.0
            elif p1_dead and not p2_dead:
                self.genome1.fitness -= 30.0
                self.genome2.fitness += 30.0
            elif p2_dead and not p1_dead:
                self.genome2.fitness -= 30.0
                self.genome1.fitness += 30.0
            else:
                self.genome1.fitness -= 10.0
                self.genome2.fitness -= 10.0
            return False

        if screen:
            screen.fill((0, 0, 0))
            for segment in self.p1_trail: pygame.draw.rect(screen, (0, 255, 255), segment)
            for segment in self.p2_trail: pygame.draw.rect(screen, (255, 165, 0), segment)
            pygame.draw.rect(screen, (255, 255, 255), self.p1)
            pygame.draw.rect(screen, (255, 255, 255), self.p2)
            return True
        return True