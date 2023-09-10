import os
import sys
import time
from matplotlib import pyplot as plt
import numpy as np
import math
import copy
import random



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
                    if i+2 < self.height:
                        if self.grid[i][j] == "A" and self.grid[i+2][j] == "Z" and self.shoot !=0:
                            self.grid[i+2][j] = None
                            self.shoot -= 1
                    if j-2 >= 0:
                        if self.grid[i][j] == "A" and self.grid[i][j-2] == "Z" and self.shoot !=0:
                            self.grid[i][j-2] = None
                            self.shoot -= 1
                    if j+2 < self.width:
                        if self.grid[i][j] == "A" and self.grid[i][j+2] == "Z" and self.shoot !=0:
                            self.grid[i][j+2] = None
                            self.shoot -= 1

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
        self.zombie_fell_into_pit()
        self.use_vaccine()

        self.player_cure_zombie()
        #     return True

        if self.player_captured_by_zombies():
            return True
        
        if self.player_fell_into_pit():
            return True

                                 
        return False
    
    def put_vaccine(self):
        while True:
            # print('helllllllllllllllllllllllllllllllllllo')
            row = random.randint(0, self.height-1)
            col = random.randint(0, self.width-1)
            if self.grid[row][col] == None:
                self.grid[row][col] = "V"
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

                if i+1 < self.height:
                    if self.grid[i][j] == "A" and self.grid[i+1][j] == "Z" and self.has_vaccine:
                        self.grid[i+1][j] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < 4 :
                            self.put_vaccine()

                if j-1 >= 0:
                    if self.grid[i][j] == "A" and self.grid[i][j-1] == "Z" and self.has_vaccine:
                        self.grid[i][j-1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < 4 :
                            self.put_vaccine()

                if j+1 < self.width:
                    if self.grid[i][j] == "A" and self.grid[i][j+1] == "Z" and  self.has_vaccine:
                        self.grid[i][j+1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < 4 :
                            self.put_vaccine()

                if i-1 >= 0 and j-1 >= 0:
                    if self.grid[i][j] == "A" and self.grid[i-1][j-1] == "Z" and self.has_vaccine:
                        self.grid[i-1][j-1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < 4 :
                            self.put_vaccine()
                    

                if i-1 >= 0 and j+1 < self.width:
                    if self.grid[i][j] == "A" and self.grid[i-1][j+1] == "Z" and self.has_vaccine:
                        self.grid[i-1][j+1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < 4 :
                            self.put_vaccine()

                if i+1 < self.height and j-1 >= 0:
                    if self.grid[i][j] == "A" and self.grid[i+1][j-1] == "Z" and self.has_vaccine:
                        self.grid[i+1][j-1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < 4 :
                            self.put_vaccine()

                if i+1 < self.height and j+1 < self.width:
                    if self.grid[i][j] == "A" and self.grid[i+1][j+1] == "Z" and self.has_vaccine:
                        self.grid[i+1][j+1] = None
                        self.score += 10
                        self.has_vaccine = False
                        self.num_zombie_cure += 1
                        if self.num_zombie_cure < 4 :
                            self.put_vaccine()
        
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
            print("piiiit")
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
            go_to_exit = 1/100
            distance_from_nearest_zombies = 0
            go_to_vaccine = 0
            has_vaccine = 0
            go_to_zombies = 0
            
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
        features.append(distance_from_pit/20)
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

def repeated_move(pre_actions, action):
    ten_actions = pre_actions[-4:]
    if ten_actions[0] == ten_actions[2]:# and ten_actions[2] == ten_actions[4] and ten_actions[4] == ten_actions[6] and ten_actions[6] == ten_actions[8]:
        if ten_actions[1] == ten_actions[3] and action == ten_actions[2] :# and ten_actions[3] == ten_actions[5] and ten_actions[5] == ten_actions[7] and ten_actions[7] == ten_actions[9]:
            
            return True
    return False
    
class Model:

    def __init__(self, num_features_player, num_features_zombie):
        self.w_hat_player = np.random.randn(num_features_player)
        self.w_hat_zombie = np.random.randn(num_features_zombie)
      

        self.num_win = 0
        self.store_grid = []
        

    
    def train_zombie(self, board: Board, alpha=0.001):
        V_train = 0
        counter = 0
        list_of_past_grids = []
        first_board = None
        second_counter = 0
        all_grid.clear()
        previous_action = []
        while not board.is_game_over() :

            counter +=1
            if counter >= 1000:
            
                break      

            current_state = copy.deepcopy(board.grid)
            print_grid(board.grid)
            time.sleep(1)
            clear = lambda: os.system('cls')
            clear()
            current_features_zombie = board.extract_features_zombie(current_state)
            # print(self.w_hat_zombie)

            
            max_V_zombie = -np.inf
            best_action_zombie = None
            actions_zombie = board.get_possible_action_zombie()
            random.shuffle(actions_zombie)
            for action_zombie in actions_zombie:
                # if len(previous_action) >= 10 and repeated_move(previous_action, action_zombie):

                #     continue
                successor_state_zombie = board.get_successor_state_zombie(action_zombie)
                successor_features_zombie = board.extract_features_zombie(successor_state_zombie)
                successor_V_zombie = V_hat(successor_features_zombie, self.w_hat_zombie)
                if successor_V_zombie > max_V_zombie:
                    best_action_zombie = action_zombie
                    max_V_zombie = successor_V_zombie
            if best_action_zombie == None : 
                print(actions_zombie)
                print_grid(board.grid)
                time.sleep(3)
            previous_action.append(best_action_zombie)


            max_V_player = -np.inf
            best_action_player = None
            actions_player = board.get_possible_action()
            random.shuffle(actions_player)
            for action_player in actions_player:
                successor_state_player = board.get_successor_state(action_player)
                successor_features_player = board.extract_features(successor_state_player)
                successor_V_player = V_hat(successor_features_player, self.w_hat_player)
                if successor_V_player > max_V_player:
                    best_action_player = action_player
                    max_V_player = successor_V_player

            board.zombies_action(best_action_zombie) 
            board.player_action(best_action_player)

            save_current_state = copy.deepcopy(board.grid)
            all_grid.append(save_current_state)
 

            V_train = max_V_zombie 

            if board.zombie_captured_player():
                V_train = 1000
                print("zombie win")
            if board.zombie_fell_into_pit():
                V_train = -100
                print("zombie fall in pit")
            if board.player_cure_zombie():
                V_train = -1000

            
            self.w_hat_zombie = self.w_hat_zombie - alpha * (V_train - V_hat(current_features_zombie, self.w_hat_zombie)) * np.array(current_features_zombie)
            

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



model = Model(8 , 3)

model.w_hat_player = read_data('w_hat_player.txt')
model.w_hat_zombie = read_data('w_hat_zombie.txt')

# first_weights = model.w_hat_zombie
for i in range(10000):
    if i % 1000 == 0:
    
        print(i)
    board = Board()
 
    model.train_zombie(board, 0.01)

print(model.w_hat_zombie)

write_data('w_hat_zombie.txt', model.w_hat_zombie)
