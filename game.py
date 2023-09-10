import os
import sys
import time
from matplotlib import pyplot as plt
import numpy as np
import math
import copy
import random
from playsound import playsound
import pygame
import pygame.font


UP, DOWN, LEFT, RIGHT = range(4)
all_grid = []
BOARD_SIZE = (15, 10)
NUM_ZOMBIES = 4
NUM_OBSTACLES = 10
NUM_VACCINES = 4
NUM_SHOTS = 3

def V_hat(x, w):
        return np.dot(w, x)


class Board:

    def __init__(self):
        self.width = 10
        self.height = 15
        self.grid = [[None for y in range(self.width)] for x in range(self.height)]
        self.player_position = None
        self.zombies_positions = [None for _ in range(NUM_ZOMBIES)]
        self.obstacle_positions = [None for _ in range(NUM_OBSTACLES)]
        self.vaccine_position =None
        self.exit_position = None
        self.pit_position = None
        self.score = 0
        self.num_zombie_cure = 0
        self.shoot = 3
        self.has_vaccine = False
        self.num_shooted_zombie = 0
        self.num_remain_vaccine = 4
        self.play_pickup = True
        #initialize the grid
        self.player_position = self.generate_random_position()
        self.zombies_positions = [self.generate_random_position() for _ in range(NUM_ZOMBIES)]
        self.obstacle_positions = [self.generate_random_position() for _ in range(NUM_OBSTACLES)]
        self.vaccine_position = self.generate_random_position()
        self.exit_position = self.generate_random_position()
        self.pit_position = self.generate_random_position()


        self.grid[self.player_position[0]][self.player_position[1]] = "A"
        for zombie_pos in self.zombies_positions:
            self.grid[zombie_pos[0]][zombie_pos[1]] = "Z"
        for obstacle_pos in self.obstacle_positions:
            self.grid[obstacle_pos[0]][obstacle_pos[1]] = "O"
        self.grid[self.vaccine_position[0]][self.vaccine_position[1]] = "V"
        self.grid[self.exit_position[0]][self.exit_position[1]] = "E"
        self.grid[self.pit_position[0]][self.pit_position[1]] = "P"

        self.move_dict = {
            'UP': (-1, 0),
            'DOWN': (1, 0),
            'LEFT': (0, -1),
            'RIGHT': (0, 1)
        }
        
    def generate_random_position(self):
        x = random.randint(0, BOARD_SIZE[0] - 1)
        y = random.randint(0, BOARD_SIZE[1] - 1)
        position = (x, y)

        occupied_positions = (
            [self.player_position] +
            self.zombies_positions +
            self.obstacle_positions +
            [self.vaccine_position, self.exit_position, self.pit_position]
        )

        if any(pos == position for pos in occupied_positions if pos is not None):
            return self.generate_random_position()

        return position

    def player_action(self, action):
         
        if action == 'UP':
            if self.player_position[0] > 0 and self.grid[self.player_position[0]-1][self.player_position[1]] !=  'O':
                self.grid[self.player_position[0]][self.player_position[1]] = None
                self.player_position = (self.player_position[0]-1, self.player_position[1])
                self.grid[self.player_position[0]][self.player_position[1]] = "A"

        elif action == 'DOWN':
            if self.player_position[0] < self.height-1 and self.grid[self.player_position[0]+1][self.player_position[1]] !=  'O':
                self.grid[self.player_position[0]][self.player_position[1]] = None
                self.player_position = (self.player_position[0]+1, self.player_position[1])
                self.grid[self.player_position[0]][self.player_position[1]] = "A"

        elif action == 'LEFT':
            if self.player_position[1] > 0 and self.grid[self.player_position[0]][self.player_position[1]-1] !=  'O':
                self.grid[self.player_position[0]][self.player_position[1]] = None
                self.player_position = (self.player_position[0], self.player_position[1]-1)
                self.grid[self.player_position[0]][self.player_position[1]] = "A"

        elif action == 'RIGHT':
            if self.player_position[1] < self.width-1 and self.grid[self.player_position[0]][self.player_position[1]+1] !=  'O':
                self.grid[self.player_position[0]][self.player_position[1]] = None
                self.player_position = (self.player_position[0], self.player_position[1]+1)
                self.grid[self.player_position[0]][self.player_position[1]] = "A"

        elif action == 'SHOOT':
              for i in range(self.height):
                for j in range(self.width):
                    if i-2 >= 0 :
                        if self.grid[i][j] == "A" and self.grid[i-2][j] == "Z" and self.shoot !=0:
                            self.grid[i-2][j] = None
                            self.shoot -= 1
                            playsound('./sounds/gun.mp3')
                            # time.sleep(1)
                    if i+2 < self.height:
                        if self.grid[i][j] == "A" and self.grid[i+2][j] == "Z" and self.shoot !=0:
                            self.grid[i+2][j] = None
                            self.shoot -= 1
                            playsound('./sounds/gun.mp3')
                            # time.sleep(1)
                    if j-2 >= 0:
                        if self.grid[i][j] == "A" and self.grid[i][j-2] == "Z" and self.shoot !=0:
                            self.grid[i][j-2] = None
                            self.shoot -= 1
                            playsound('./sounds/gun.mp3')
                            # time.sleep(1)
                    if j+2 < self.width:
                        if self.grid[i][j] == "A" and self.grid[i][j+2] == "Z" and self.shoot !=0:
                            self.grid[i][j+2] = None
                            self.shoot -= 1
                            playsound('./sounds/gun.mp3')
                            # time.sleep(1)


    def is_valid_pos(self, pos):
        return pos[0] >= 0 and pos[0] < self.width and pos[1] >= 0 and pos[1] < self.height
    

    def exit_exist(self):
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == "E":
                    return True
        return False


    def zombies_action(self , best_actions):
            for acts in best_actions:

                zombies_position = acts[0], acts[1]
                action = acts[2]
                if action == 'UP':
                    if zombies_position[0] > 0 and (self.grid[zombies_position[0]-1][zombies_position[1]] == None or self.grid[zombies_position[0]-1][zombies_position[1]] == "P"):
                        self.grid[zombies_position[0]][zombies_position[1]] = None
                        self.grid[zombies_position[0]-1][zombies_position[1]] = "Z"

                elif action == 'DOWN':
                    if zombies_position[0] < self.height-1 and ( self.grid[zombies_position[0]+1][zombies_position[1]] == None or self.grid[zombies_position[0]+1][zombies_position[1]] == "P"):
                        self.grid[zombies_position[0]][zombies_position[1]] = None
                        self.grid[zombies_position[0]+1][zombies_position[1]] = "Z"

                elif action == 'LEFT':
                    if zombies_position[1] > 0 and (self.grid[zombies_position[0]][zombies_position[1]-1] == None or self.grid[zombies_position[0]][zombies_position[1]-1] == 'P'):
                        self.grid[zombies_position[0]][zombies_position[1]] = None
                        self.grid[zombies_position[0]][zombies_position[1]-1] = "Z"

                elif action == 'RIGHT':
                    if zombies_position[1] < self.width-1 and (self.grid[zombies_position[0]][zombies_position[1]+1] == None or self.grid[zombies_position[0]][zombies_position[1]+1] == 'P'):
                        self.grid[zombies_position[0]][zombies_position[1]] = None
                        self.grid[zombies_position[0]][zombies_position[1]+1] = "Z"
               

                
    
    def use_vaccine(self):
        self.has_vaccine = True
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == "V":
                    self.has_vaccine = False
 

    def use_gun(self, direction):
        pass

    def can_shoot(self):
        
        for i in range(self.height):
            for j in range(self.width):
                if i-2 >= 0 :
                    if self.grid[i][j] == "A" and self.grid[i-2][j] == "Z" and self.shoot !=0:
                        return True
                if i+2 < self.height:
                    if self.grid[i][j] == "A" and self.grid[i+2][j] == "Z" and self.shoot !=0:
                        return True
                if j-2 >= 0:
                    if self.grid[i][j] == "A" and self.grid[i][j-2] == "Z" and self.shoot !=0:
                        return True
                if j+2 < self.width:
                    if self.grid[i][j] == "A" and self.grid[i][j+2] == "Z" and self.shoot !=0:
                        return True
        return False

                    

    def is_game_over(self):
        # zombie_exist = False
        # for i in range(self.height):
        #     for j in range(self.width):
        #         if self.grid[i][j] == "Z":
        #             zombie_exist = True
        # if not zombie_exist : 
        #     return True
        # if self.has_vaccine :
        #     playsound('./sounds/pickup.mp3')
        #     time.sleep(2)
        self.use_vaccine()
        if self.has_vaccine and self.play_pickup:
            playsound('./sounds/pickup.mp3')
            self.play_pickup = False
            # time.sleep(1)

        self.zombie_fell_into_pit()

        if self.player_cure_zombie():
            playsound('./sounds/down.mp3')
            time.sleep(2)

        if self.player_captured_by_zombies():
            playsound('./sounds/evil.mp3')
            # time.sleep(1)
            draw_game_over("You lost!")
            time.sleep(2)
            return True
        
        if not self.exit_exist() and self.find_zombies_number() == 0:
            playsound('./sounds/Tabl.mp3')
            # time.sleep(1)
            draw_game_over("You won!")
            time.sleep(2)
            return True

        if not self.exit_exist():
            playsound('./sounds/evil.mp3')
            # time.sleep(1)
            draw_game_over("You lost!")
            time.sleep(2)
            return True        
        
        if self.player_fell_into_pit():
            playsound('./sounds/fall.wav')
            # time.sleep(1)
            draw_game_over("You lost!")
            time.sleep(2)
            return True

        

                                 
        return False
    
    def put_vaccine(self):
        while True:
            row = random.randint(0, self.height-1)
            col = random.randint(0, self.width-1)
            if self.grid[row][col] == None:
                self.grid[row][col] = "V"
                self.play_pickup = True
                # print_grid(self.grid)
                break

    def player_cure_zombie(self):
        for i in range(self.height):
            for j in range(self.width):
                if i-1 >= 0 :
                    if self.grid[i][j] == "A" and self.grid[i-1][j] == "Z" and self.has_vaccine:
                        self.grid[i-1][j] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < 4 :
                            self.put_vaccine()
                        return True

                if i+1 < self.height:
                    if self.grid[i][j] == "A" and self.grid[i+1][j] == "Z" and self.has_vaccine:
                        self.grid[i+1][j] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < 4 :
                            self.put_vaccine()
                        return True

                if j-1 >= 0:
                    if self.grid[i][j] == "A" and self.grid[i][j-1] == "Z" and self.has_vaccine:
                        self.grid[i][j-1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < 4 :
                            self.put_vaccine()
                        return True

                if j+1 < self.width:
                    if self.grid[i][j] == "A" and self.grid[i][j+1] == "Z" and  self.has_vaccine:
                        self.grid[i][j+1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < 4 :
                            self.put_vaccine()
                        return True
                    
                if i-1 >= 0 and j-1 >= 0:
                    if self.grid[i][j] == "A" and self.grid[i-1][j-1] == "Z" and self.has_vaccine:
                        self.grid[i-1][j-1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < 4 :
                            self.put_vaccine()
                        return True 

                if i-1 >= 0 and j+1 < self.width:
                    if self.grid[i][j] == "A" and self.grid[i-1][j+1] == "Z" and self.has_vaccine:
                        self.grid[i-1][j+1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < 4 :
                            self.put_vaccine()
                        return True
                    
                if i+1 < self.height and j-1 >= 0:
                    if self.grid[i][j] == "A" and self.grid[i+1][j-1] == "Z" and self.has_vaccine:
                        self.grid[i+1][j-1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < 4 :
                            self.put_vaccine()
                        return True
                if i+1 < self.height and j+1 < self.width:
                    if self.grid[i][j] == "A" and self.grid[i+1][j+1] == "Z" and self.has_vaccine:
                        self.grid[i+1][j+1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < 4 :
                            self.put_vaccine()
                        return True
                    
        return False



    def player_captured_by_zombies(self):
        for i in range(self.height):
            for j in range(self.width):
                if i-1 >= 0 :
                    if self.grid[i][j] == "A" and self.grid[i-1][j] == "Z" and not self.has_vaccine:
                        return True
                if i+1 < self.height:
                    if self.grid[i][j] == "A" and self.grid[i+1][j] == "Z" and not self.has_vaccine:
                        return True
                if j-1 >= 0:
                    if self.grid[i][j] == "A" and self.grid[i][j-1] == "Z" and not self.has_vaccine:
                        return True
                if j+1 < self.width: 
                    if self.grid[i][j] == "A" and self.grid[i][j+1] == "Z" and not self.has_vaccine:
                        return True
                if i-1 >= 0 and j-1 >= 0:
                    if self.grid[i][j] == "A" and self.grid[i-1][j-1] == "Z" and not self.has_vaccine:
                        return True
                if i-1 >= 0 and j+1 < self.width:
                    if self.grid[i][j] == "A" and self.grid[i-1][j+1] == "Z" and not self.has_vaccine:
                        return True
                if i+1 < self.height and j-1 >= 0:
                    if self.grid[i][j] == "A" and self.grid[i+1][j-1] == "Z" and not self.has_vaccine:
                        return True
                if i+1 < self.height and j+1 < self.width:
                    if self.grid[i][j] == "A" and self.grid[i+1][j+1] == "Z" and not self.has_vaccine:
                        return True
                    
        return False

    def zombie_captured_player(self):
        for i in range(self.height):
            for j in range(self.width):
                if i-1 >= 0 :
                    if self.grid[i][j] == "A" and self.grid[i-1][j] == "Z" and not self.has_vaccine:
                        return True
                if i+1 < self.height:
                    if self.grid[i][j] == "A" and self.grid[i+1][j] == "Z" and not self.has_vaccine:
                        return True
                if j-1 >= 0:
                    if self.grid[i][j] == "A" and self.grid[i][j-1] == "Z" and not self.has_vaccine:
                        return True
                if j+1 < self.width: 
                    if self.grid[i][j] == "A" and self.grid[i][j+1] == "Z" and not self.has_vaccine:
                        return True
                if i-1 >= 0 and j-1 >= 0:
                    if self.grid[i][j] == "A" and self.grid[i-1][j-1] == "Z" and not self.has_vaccine:
                        return True
                if i-1 >= 0 and j+1 < self.width:
                    if self.grid[i][j] == "A" and self.grid[i-1][j+1] == "Z" and not self.has_vaccine:
                        return True
                if i+1 < self.height and j-1 >= 0:
                    if self.grid[i][j] == "A" and self.grid[i+1][j-1] == "Z" and not self.has_vaccine:
                        return True
                if i+1 < self.height and j+1 < self.width:
                    if self.grid[i][j] == "A" and self.grid[i+1][j+1] == "Z" and not self.has_vaccine:
                        return True
                    
        return False
    
    
    def player_fell_into_pit(self):
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == "P":
                    return False
        if self.grid[self.pit_position[0]][self.pit_position[1]] == "A":
            # print("piiiit")
            return True
                
        return False
    
    def zombie_fell_into_pit(self):
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == "P":
                    return False
        if self.grid[self.pit_position[0]][self.pit_position[1]] == "Z":
            self.grid[self.pit_position[0]][self.pit_position[1]] = 'P'
            self.zombies_positions = [self.generate_random_position()]
            self.grid[self.zombies_positions[0][0]][self.zombies_positions[0][1]] = 'Z'

            return True
                
        return False
    
    def find_zombies_number(self):
        num = 0
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == "Z":
                    num += 1
                
        return num
    

    def get_possible_action(self):
        actions = []
        row, col = 0, 0
        num_zombies = 0
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == "A":
                    row, col = i, j
                if self.grid[i][j] == "Z":
                    num_zombies += 1

        if num_zombies > 0:
            if row > 0 and self.grid[row-1][col] !=  'O' and self.grid[row-1][col] !=  'E':  # Up
                actions.append("UP")
            if row < self.height-1 and self.grid[row+1][col] !=  'O' and self.grid[row+1][col] !=  'E':  # Down
                actions.append("DOWN")
            if col > 0 and self.grid[row][col-1] !=  'O' and self.grid[row][col - 1] !=  'E':  # Left
                actions.append("LEFT")
            if col < self.width-1 and self.grid[row][col+1] !=  'O' and self.grid[row][col+1] !=  'E':  # Right
                actions.append("RIGHT")
            if self.can_shoot():
                actions.append("SHOOT")
        else:
            
            if row > 0 and self.grid[row-1][col] !=  'O':  # Up
                actions.append("UP")
            if row < self.height-1 and self.grid[row+1][col] !=  'O':  # Down
                actions.append("DOWN")
            if col > 0 and self.grid[row][col-1] !=  'O':  # Left
                actions.append("LEFT")
            if col < self.width-1 and self.grid[row][col+1] !=  'O':  # Right
                actions.append("RIGHT")
        return actions
    
    def get_possible_action_zombie(self, row, col):
        actions = []
        # for i in range(self.height):
        #     for j in range(self.width):
        #         if self.grid[i][j] == "Z":
        #             row, col = i, j

        if row > 0 and self.grid[row-1][col] !=  'O' and self.grid[row-1][col] !=  'V' and self.grid[row-1][col] !=  'E':  # Up
            actions.append("UP")
        if row < self.height-1 and self.grid[row+1][col] !=  'O' and self.grid[row+1][col] !=  'V' and self.grid[row+1][col] !=  'E':  # Down
            actions.append("DOWN")
        if col > 0 and self.grid[row][col-1] !=  'O' and self.grid[row][col-1] !=  'V' and self.grid[row][col-1] !=  'E':  # Left
            actions.append("LEFT")
        if col < self.width-1 and self.grid[row][col+1] !=  'O' and self.grid[row][col+1] !=  'V' and self.grid[row][col+1] !=  'E':  # Right
            actions.append("RIGHT")

        return actions
    
    def get_successor_state(self, action):
        # state = []
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == "A":
                    player_position = [i, j]
        grid_copy = copy.deepcopy(self.grid)
        if action == 'SHOOT':
            for i in range(self.height):
                for j in range(self.width):
                    if i-2 >= 0 :
                        if grid_copy[i][j] == "A" and grid_copy[i-2][j] == "Z" and self.shoot !=0:
                            grid_copy[i-2][j] = None
                    if i+2 < self.height:
                        if grid_copy[i][j] == "A" and grid_copy[i+2][j] == "Z" and self.shoot !=0:
                            grid_copy[i+2][j] = None
                    if j-2 >= 0:
                        if grid_copy[i][j] == "A" and grid_copy[i][j-2] == "Z" and self.shoot !=0:
                            grid_copy[i][j-2] = None
                    if j+2 < self.width:
                        if grid_copy[i][j] == "A" and grid_copy[i][j+2] == "Z" and self.shoot !=0:
                            grid_copy[i][j+2] = None
                
            return grid_copy
        
        else : 
            grid_copy[player_position[0]][player_position[1]] = None
            grid_copy[player_position[0]+self.move_dict[action][0]][player_position[1]+self.move_dict[action][1]] = "A"
            return grid_copy
        
    def get_successor_state_zombie(self, action, row, col):
        # state = []
        # for i in range(self.height):
        #     for j in range(self.width):
        #         if self.grid[i][j] == "Z":
        #             zombie_position = [i, j]
        zombie_position = [row, col]
        grid_copy = copy.deepcopy(self.grid)
        grid_copy[zombie_position[0]][zombie_position[1]] = None
        grid_copy[zombie_position[0]+self.move_dict[action][0]][zombie_position[1]+self.move_dict[action][1]] = "Z"

        return grid_copy
    

   
    def extract_features(self, successor_state):
        features = []

        # Check if the successor state is the exit port
        player_position = None
        player_exist = False
        exit_port_exist = False
        zombie_exist = False
        number_of_zombie = 0
        # number_of_obstacle = 0
        distance_from_all_obstacle = []
        number_of_vaccines = 0
        distance_from_vaccines = 0
        distance_from_all_zombies = []
        distance_from_pit = 0
        distance_from_exit = 0
        shoot_option_exist = 0
        go_to_exit = 0
        has_vaccine = 0
        go_to_vaccine = 1
        go_to_zombies = 1
        distance_from_nearest_zombies = 0
        shoot = -1000000
        pit = 1
        # num_of_exist_zombies = self.find_zombies_number()
        if self.has_vaccine :
            has_vaccine = 1
            go_to_zombies = -1
            shoot = 0
     

        for i in range(self.height):
            for j in range(self.width):
                if successor_state[i][j] == "A":
                    player_position = [i, j]
                
        for i in range(self.height):
            for j in range(self.width):
                if i-2 >= 0 :
                    if self.grid[i][j] == "A" and self.grid[i-2][j] == "Z" and self.shoot !=0:
                        shoot_option_exist = 1
                if i+2 < self.height:
                    if self.grid[i][j] == "A" and self.grid[i+2][j] == "Z" and self.shoot !=0:
                        shoot_option_exist = 1
                if j-2 >= 0:
                    if self.grid[i][j] == "A" and self.grid[i][j-2] == "Z" and self.shoot !=0:
                        shoot_option_exist =  1
                if j+2 < self.width:
                    if self.grid[i][j] == "A" and self.grid[i][j+2] == "Z" and self.shoot !=0:
                        shoot_option_exist =  1
                
                if successor_state[i][j] == "E":
                    exit_port_exist = True
                    distance_from_exit = math.dist(player_position, [i, j])
                if successor_state[i][j] == "A":
                    player_exist = True
                if successor_state[i][j] == "Z":
                    zombie_exist = True
                    number_of_zombie += 1
                    
                    distance_from_all_zombies.append(math.dist(player_position, [i, j]))
                if successor_state[i][j] == "O":
                    distance_from_all_obstacle.append(math.dist(player_position, [i, j]))
                if successor_state[i][j] == "V":
                    # number_of_vaccines += 1
                    distance_from_vaccines = math.dist(player_position, [i, j])
                if successor_state[i][j] == "P":
                    distance_from_pit = math.dist(player_position, [i, j])

        if number_of_zombie == 0 :
            go_to_exit = 100
            distance_from_nearest_zombies = 0
            go_to_vaccine = 0
            has_vaccine = 0
            go_to_zombies = 0
            pit = 10
            
        else :
            go_to_exit = 0
            distance_from_nearest_zombies = min(distance_from_all_zombies)
            go_to_vaccine = 1

        # if number_of_zombie == 0 : 
        #     features = [ -2 , 0 , 0 , 0 , 0 , 0 , 0 , 2]
        # else : 
        features.append( go_to_exit*(distance_from_exit/20))
        features.append(shoot*number_of_zombie)
        remain_vaccine = 4 - self.num_zombie_cure
        features.append(remain_vaccine)
                    
        
        features.append(go_to_vaccine*distance_from_vaccines/20)
        features.append(go_to_zombies * distance_from_nearest_zombies/20)
        features.append(has_vaccine)
        features.append(min(distance_from_all_obstacle)/20)
        features.append(pit * distance_from_pit/20)
        # features.append(shoot_option_exist)
        return np.array(features)



    def extract_features_zombie(self, successor_state, row, col):
        features = []

        distance_from_all_obstacle = []
        distance_from_vaccines = 0
        distance_from_pit = 0
        has_vaccine = 0
        go_to_player = -10
        zombie_position = None
        distance_from_player = 0
 
        # for i in range(self.height):
        #     for j in range(self.width):
        #         if successor_state[i][j] == "Z":
        #             zombie_position = [i, j]
        #             print(zombie_position)
        zombie_position = [row,col]
        # print([row,col])
        # time.sleep(5)
        for i in range(self.height):
            for j in range(self.width):

                if successor_state[i][j] == "A":
                    distance_from_player = math.dist(zombie_position, [i, j])
                                  
                if successor_state[i][j] == "O":
                    distance_from_all_obstacle.append(math.dist(zombie_position, [i, j]))
                if successor_state[i][j] == "V":
                    distance_from_vaccines = math.dist(zombie_position, [i, j])
                if successor_state[i][j] == "P":
                    distance_from_pit = math.dist(zombie_position, [i, j])

        if self.has_vaccine :
            # has_vaccine = 10
            go_to_player = 10
            # print('vvvvvvvvvvvvvvvvvvv')
            # features =  [1000 , 1000 , 0 ]
        features.append(go_to_player*distance_from_player/20)
        
        features.append(distance_from_pit/20)

        features.append((min(distance_from_all_obstacle))/40)
        
        # features.append(has_vaccine)


        return np.array(features)
 
    
    def get_zombies_position(self):
        zombies_possitions = []
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == "Z":
                    zombie_position = [i, j]
                    zombies_possitions.append(zombie_position)
        return zombies_possitions


def print_grid(grid):
    print ( "===============================")

    for i in range(len(grid)):
        row = ""
        for j in range(len(grid[i])):
            row += grid[i][j] + "|" if grid[i][j] != None else " |"
        print(row + "|")
    print ( "===============================")



pygame.init()
screen = pygame.display.set_mode(( BOARD_SIZE[1] * 50, BOARD_SIZE[0] * 50 + 50))
clock = pygame.time.Clock()
bg_color = (255, 255, 255)
pygame.display.set_caption("Pac-Man Z") 


grid_color = (200, 200, 200)



player_img = pygame.image.load("./images/player.png").convert_alpha()
zombie_img = pygame.image.load("./images/zombie.png").convert_alpha()
obstacle_img = pygame.image.load("./images/obstacle.png").convert_alpha()
vaccine_img = pygame.image.load("./images/vaccine.png").convert_alpha()
exit_img = pygame.image.load("./images/exit.png").convert_alpha()
pit_img = pygame.image.load("./images/pit.png").convert_alpha()

player_img = pygame.transform.scale(player_img, (50, 50))
zombie_img = pygame.transform.scale(zombie_img, (50, 50))
obstacle_img = pygame.transform.scale(obstacle_img, (50, 50))
vaccine_img = pygame.transform.scale(vaccine_img, (50, 50))
exit_img = pygame.transform.scale(exit_img, (50, 50))
pit_img = pygame.transform.scale(pit_img, (50, 50))


def draw_screen(board):
            
        screen.fill(bg_color)

        for x in range(board.width):
            pygame.draw.line(screen, grid_color, (x * 50, 0), (x * 50, board.height * 50))
        for y in range(board.height):
            pygame.draw.line(screen, grid_color, (0, y * 50), (board.width * 50, y * 50))

        # Draw the objects on the board
        for y in range(board.width):
            for x in range(board.height):
                if board.grid[x][y] == "A":
                    screen.blit(player_img, (y * 50, x * 50))
                elif  board.grid[x][y] == "Z":
                    screen.blit(zombie_img, (y * 50, x * 50))
                elif  board.grid[x][y] == "O":
                    screen.blit(obstacle_img, (y * 50, x * 50))
                elif  board.grid[x][y] == "V":
                    screen.blit(vaccine_img, (y * 50, x * 50))
                elif  board.grid[x][y] == "E":
                    screen.blit(exit_img, (y * 50, x * 50))
                elif board.grid[x][y] == "P":
                    screen.blit(pit_img, (y * 50, x * 50))
                # Draw HUD
        draw_hud(board)

        pygame.display.update()


score = 0

def draw_hud(board):
        font = pygame.font.Font(None, 24)
        score_text = font.render(f"                  ", True, (0, 0, 0))
        cured_zombies_text = font.render(f"Cured Zombies: {board.num_zombie_cure}", True, (0, 0, 0))
        shoot_text = font.render(f"Killed zombies: {(3 - board.shoot)}", True, (0, 0, 0))

        score_text_rect = score_text.get_rect()
        cured_zombies_text_rect = cured_zombies_text.get_rect()
        shoot_text_rect = shoot_text.get_rect()

        score_text_rect.topleft = (10, board.height * 50 + 10)
        cured_zombies_text_rect.topleft = (10 + score_text_rect.width + 20, board.height * 50 + 10)
        shoot_text_rect.topleft = (10 + score_text_rect.width + 20 + cured_zombies_text_rect.width + 20, board.height * 50 + 10)

        screen.blit(score_text, score_text_rect)
        screen.blit(cured_zombies_text, cured_zombies_text_rect)
        screen.blit(shoot_text, shoot_text_rect)
        # Add more HUD elements here (e.g., lives, level)
reset_button_rect = None        
def draw_reset_button():
        font = pygame.font.Font(None, 24)
        reset_button_text = font.render("Reset", True, (0, 0, 0))
        reset_button_rect = reset_button_text.get_rect()
        

        reset_button_rect.topleft = (10, BOARD_SIZE[0] * 50 + 10)
        pygame.draw.rect(screen, (200, 200, 200), reset_button_rect.inflate(10, 10))
        screen.blit(reset_button_text, reset_button_rect)
        pygame.display.update

def is_reset_button_clicked(mouse_pos):
        if reset_button_rect is not None:
            return reset_button_rect.collidepoint(mouse_pos)
        return False

def draw_start_button():
    font = pygame.font.Font(None, 36)
    text = font.render('Start Game', True, (0, 0, 0))
    text_rect = text.get_rect()
    text_rect.center = (screen.get_width() // 2, screen.get_height() // 2)
    screen.fill(bg_color)
    screen.blit(text, text_rect)
    pygame.display.update()

def draw_game_over(message):
    font = pygame.font.Font(None, 36)
    text = font.render(message, True, (0, 0, 0))
    text_rect = text.get_rect()
    text_rect.center = (screen.get_width() // 2,screen.get_height() // 2)
    screen.fill(bg_color)

    screen.blit(text, text_rect)
    pygame.display.update()



def read_data(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()

    numbers = []

    for line in lines:
        number = float(line.strip())
        numbers.append(number)

    # print(numbers)

    return numbers

def write_data(file_name, data):
    with open(file_name, 'w') as file:
        for number in data:
            file.write(str(number) + '\n')



w_hat_player = read_data('w_hat_player.txt')
w_hat_zombie = read_data('w_hat_zombie.txt')
            
def display_main_menu(board):
        font = pygame.font.Font(None, 36)
        menu = True
        while menu:
            screen.fill(bg_color)
            user_button_text = font.render("User Mode", True, (0, 0, 0))
            computer_button_text = font.render("Computer Mode", True, (0, 0, 0))

            user_button_rect = user_button_text.get_rect()
            computer_button_rect = computer_button_text.get_rect()

            user_button_rect.center = (screen.get_width() // 2, screen.get_height() // 2 - 50)
            computer_button_rect.center = (screen.get_width() // 2, screen.get_height() // 2 + 50)

            screen.blit(user_button_text, user_button_rect)
            screen.blit(computer_button_text, computer_button_rect)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if user_button_rect.collidepoint(event.pos):
                        menu = False
                        play(board, user_play=True)
                    elif computer_button_rect.collidepoint(event.pos):
                        menu = False
                        play(board, user_play=False)
    
def play(board: Board , user_play: bool = False):

    # self.clock.tick(1)

    # display_main_menu()
    # start_game = False
    # while not start_game:
    #     for event in pygame.event.get():
    #         if event.type == pygame.MOUSEBUTTONDOWN:
    #             start_game = True
    #         if event.type == pygame.QUIT:
    #             pygame.quit()
    #             sys.exit()
        
    # game_reset = False
    while not board.is_game_over():

        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if user_play:
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT , pygame.K_SPACE):
                            # Determine the action based on the key pressed
                            if event.key == pygame.K_UP:
                                action = "UP"
                            elif event.key == pygame.K_DOWN:
                                action = "DOWN"
                            elif event.key == pygame.K_LEFT:
                                action = "LEFT"
                            elif event.key == pygame.K_RIGHT:
                                action = "RIGHT"
                            elif event.key == pygame.K_SPACE:
                                action = "SHOOT"


                            # Perform the player's action and update the game state
                            board.player_action(action)

                            zombies_positions = board.get_zombies_position()
                            best_actions = []
                            for zombie_postions in zombies_positions:
                                # print(zombie_postions)
                                row, col = zombie_postions[0], zombie_postions[1]
                                # print(row, col)
                                actions_zombie = board.get_possible_action_zombie(row, col)
                                max_V_zombie = -np.inf
                                best_action_zombie = None
                                random.shuffle(actions_zombie)
                                for action_zombie in actions_zombie:
                                    successor_state_zombie = board.get_successor_state_zombie(action_zombie, row, col)
                                    successor_features_zombie = board.extract_features_zombie(successor_state_zombie, row+board.move_dict[action_zombie][0], col+board.move_dict[action_zombie][1])
                                    successor_V_zombie = V_hat(successor_features_zombie, w_hat_zombie)
                                    if successor_V_zombie > max_V_zombie:
                                        best_action_zombie = action_zombie
                                        max_V_zombie = successor_V_zombie
                                best_actions.append((row, col, best_action_zombie))
                                
                            # print(actions_player)
                            board.zombies_action(best_actions)

                    draw_screen(board)
                    pygame.display.update()




        if not user_play:
            
            draw_screen(board)
            pygame.display.update()
                    

        
            max_V_player = -np.inf
            best_action_player = None
            actions_player = board.get_possible_action()
            random.shuffle(actions_player)
            for action_player in actions_player:
                successor_state_player = board.get_successor_state(action_player)
                successor_features_player = board.extract_features(successor_state_player)
                successor_V_player = V_hat(successor_features_player, w_hat_player)
                if successor_V_player >= max_V_player:
                    best_action_player = action_player
                    max_V_player = successor_V_player


            board.player_action(best_action_player)

            zombies_positions = board.get_zombies_position()
            best_actions = []
            for zombie_postions in zombies_positions:
                # print(zombie_postions)
                row, col = zombie_postions[0], zombie_postions[1]
                # print(row, col)
                actions_zombie = board.get_possible_action_zombie(row, col)
                max_V_zombie = -np.inf
                best_action_zombie = None
                random.shuffle(actions_zombie)
                for action_zombie in actions_zombie:
                    successor_state_zombie = board.get_successor_state_zombie(action_zombie, row, col)
                    successor_features_zombie = board.extract_features_zombie(successor_state_zombie, row+board.move_dict[action_zombie][0], col+board.move_dict[action_zombie][1])
                    successor_V_zombie = V_hat(successor_features_zombie, w_hat_zombie)
                    if successor_V_zombie > max_V_zombie:
                        best_action_zombie = action_zombie
                        max_V_zombie = successor_V_zombie
                best_actions.append((row, col, best_action_zombie))
                
            # print(actions_player)
            board.zombies_action(best_actions)
            

            clock.tick(1)
            draw_screen(board)
            pygame.display.update()
        

            

for i in range(100):
    board = Board()
    display_main_menu(board)