from Game import Game
import constants
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
import math as m
import random

#To Calculate the angle between 2 points

#myradians = math.atan2(targetY-gunY, targetX-gunX)

class FuzzyRulesForBricksController:


    def __init__(self, max_moves=2000):
        self.max_moves = max_moves
        self.current_move_number = 0
        self.game = Game()
        self.mf_pm_right()
        self.mf_pm_left()
        self.mf_pm_up()
        self.mf_pm_down()
        self.old_snake_pos_y = 0
        self.old_snake_pos_x = 0

# '''Membership Function of the snake when the Snake is facing right'''
    def mf_pm_right(self):
        '''if the previous move is RIGHT, the only direction
        you can move is UP, RIGHT, DOWN'''
        self.next_move_pm_right = ctrl.Consequent(np.arange(0, 101, 1), 'Next Direction')

        self.next_move_pm_right['up'] = fuzz.trapmf(self.next_move_pm_right.universe,[0,0,25, 50])
        self.next_move_pm_right['right'] = fuzz.trimf(self.next_move_pm_right.universe,[25,50,75])
        self.next_move_pm_right['down'] = fuzz.trapmf(self.next_move_pm_right.universe,[50,75,100,100])

        '''Based on a clock with respect the the snake head'''
        self.food_loc = ctrl.Antecedent(np.arange(-181, 181, 1), 'food_loc')

        self.food_loc['up'] = fuzz.trimf(self.food_loc.universe,[-50,0, 50])
        self.food_loc['right'] = fuzz.trimf(self.food_loc.universe,[45,135,181])
        self.food_loc['left'] = fuzz.trimf(self.food_loc.universe, [-181,-135,-45])

        self.rule1 = ctrl.Rule(self.food_loc['up'], self.next_move_pm_right['right'])
        self.rule2 = ctrl.Rule(self.food_loc['left'], self.next_move_pm_right['up'])
        self.rule3 = ctrl.Rule(self.food_loc['right'], self.next_move_pm_right['down'])

        # self.collison_ang = ctrl.Antecedent(np.arange(-181, 181, 1), 'collison_ang')
        # '''Based on a clock with respect the the snake head'''
        # self.collison_ang['0'] = fuzz.trapmf(self.collison_ang.universe,[-50,-25,25,50])
        # self.collison_ang['90'] = fuzz.trimf(self.collison_ang.universe,[25,90,135])
        # self.collison_ang['-90'] = fuzz.trimf(self.collison_ang.universe, [-135,-90,-25])
        #
        # self.rule4 = ctrl.Rule(self.collison_ang['0'], self.next_move_pm_right['right'])
        # self.rule5 = ctrl.Rule(self.collison_ang['90'], self.next_move_pm_right['up'])
        # self.rule6 = ctrl.Rule(self.collison_ang['-90'], self.next_move_pm_right['down'])

        '''Based on a clock with respect the the snake head'''
        self.collison_ang_2 = ctrl.Antecedent(np.arange(-181, 181, 1), 'collison_ang_2')

        self.collison_ang_2['0'] = fuzz.trapmf(self.collison_ang_2.universe,[-90,-45,45,90])
        self.collison_ang_2['90'] = fuzz.trimf(self.collison_ang_2.universe,[45,90,135])
        self.collison_ang_2['-90'] = fuzz.trimf(self.collison_ang_2.universe, [-135,-90,-45])

        self.rule7 = ctrl.Rule(self.collison_ang_2['0'], self.next_move_pm_right['right'])
        self.rule8 = ctrl.Rule(self.collison_ang_2['90'], self.next_move_pm_right['up'])
        self.rule9 = ctrl.Rule(self.collison_ang_2['-90'], self.next_move_pm_right['down'])

        '''Weight of the Snake to check if it is tilted to the left or right'''
        self.weight_snake = ctrl.Antecedent(np.arange(-10,10,1),'weight_snake')

        self.weight_snake['left'] = fuzz.trapmf(self.weight_snake.universe,[-10,-10,-2,0])
        self.weight_snake['right'] = fuzz.trapmf(self.weight_snake.universe,[0,2,10,10])

        self.rule10 = ctrl.Rule(self.weight_snake['left'], self.next_move_pm_right['down'])
        self.rule11= ctrl.Rule(self.weight_snake['right'], self.next_move_pm_right['up'])

        '''To check if the snake is spiraling Anti-clockwise or Clockwise'''
        self.spiral_snake = ctrl.Antecedent(np.arange(-91,91,1),'spiral_snake')

        self.spiral_snake['-90'] = fuzz.trimf(self.spiral_snake.universe,[-91,-90,-89])
        self.spiral_snake['90'] = fuzz.trimf(self.spiral_snake.universe,[89,90,91])
        self.spiral_snake['0'] = fuzz.trimf(self.spiral_snake.universe,[-1,0,1])

        self.rule12 = ctrl.Rule(self.spiral_snake['-90'], self.next_move_pm_right['down'])
        self.rule13= ctrl.Rule(self.spiral_snake['90'], self.next_move_pm_right['up'])
        self.rule14= ctrl.Rule(self.spiral_snake['0'], self.next_move_pm_right['right'])

        '''To check if the snake is colliding with 1 brick?'''
        self.collison_brick_ang = ctrl.Antecedent(np.arange(-181, 181, 1), 'collison_brick_ang')
        '''Based on a clock with respect the the snake head'''
        self.collison_brick_ang['0'] = fuzz.trimf(self.collison_brick_ang.universe,[-1,0,1])
        self.collison_brick_ang['90'] = fuzz.trimf(self.collison_brick_ang.universe,[-25,90,135])
        self.collison_brick_ang['-90'] = fuzz.trimf(self.collison_brick_ang.universe, [-135,-90,25])

        self.rule15 = ctrl.Rule(self.collison_brick_ang['0'], self.next_move_pm_right['right'])
        self.rule16 = ctrl.Rule(self.collison_brick_ang['90'], self.next_move_pm_right['up'])
        self.rule17 = ctrl.Rule(self.collison_brick_ang['-90'], self.next_move_pm_right['down'])

        '''To check if the snake is colliding with 2 brick? If it is, we need to sum the 1st collison_brick_ang + and the 2nd collison_brick_ang
        There will only be 3 numbers and each will have a distinct direction to go to'''
        self.collison_brick_ang_2 = ctrl.Antecedent(np.arange(-181, 181, 1), 'collison_brick_ang_2')
        self.collison_brick_ang_2['0'] = fuzz.trapmf(self.collison_brick_ang_2.universe,[-50,-25,25,50])
        self.collison_brick_ang_2['90'] = fuzz.trimf(self.collison_brick_ang_2.universe,[25,90,135])
        self.collison_brick_ang_2['-90'] = fuzz.trimf(self.collison_brick_ang_2.universe, [-135,-90,-25])

        self.rule18 = ctrl.Rule(self.collison_brick_ang_2['0'], self.next_move_pm_right['right'])
        self.rule19 = ctrl.Rule(self.collison_brick_ang_2['90'], self.next_move_pm_right['up'])
        self.rule20 = ctrl.Rule(self.collison_brick_ang_2['-90'], self.next_move_pm_right['down'])

###############################################################################################
# '''Membership Function of the snake when the Snake is facing left'''
    def mf_pm_left(self):
        '''if the previous move is LEFT, the only direciton
        you can move is UP, LEFT, DOWN'''
        self.next_move_pm_left = ctrl.Consequent(np.arange(0, 101, 1), 'Next Direction')
        self.next_move_pm_left['up'] = fuzz.trapmf(self.next_move_pm_left.universe,[0,0,25, 50])
        self.next_move_pm_left['left'] = fuzz.trimf(self.next_move_pm_left.universe,[25,50,75])
        self.next_move_pm_left['down'] = fuzz.trapmf(self.next_move_pm_left.universe,[50,75,100,100])

        self.food_loc = ctrl.Antecedent(np.arange(-181, 181, 1), 'food_loc')
        '''Based on a clock with respect the the snake head'''
        self.food_loc['up'] = fuzz.trimf(self.food_loc.universe,[-50,0, 50])
        self.food_loc['right'] = fuzz.trimf(self.food_loc.universe,[45,135,181])
        self.food_loc['left'] = fuzz.trimf(self.food_loc.universe, [-181,-135,-45])

        self.rule1 = ctrl.Rule(self.food_loc['up'], self.next_move_pm_left['left'])
        self.rule2 = ctrl.Rule(self.food_loc['left'], self.next_move_pm_left['down'])
        self.rule3 = ctrl.Rule(self.food_loc['right'], self.next_move_pm_left['up'])

        # self.collison_ang = ctrl.Antecedent(np.arange(-181, 181, 1), 'collison_ang')
        # '''Based on a clock with respect the the snake head'''
        # self.collison_ang['0'] = fuzz.trapmf(self.collison_ang.universe,[-50,-25,25,50])
        # self.collison_ang['90'] = fuzz.trimf(self.collison_ang.universe,[25,90,135])
        # self.collison_ang['-90'] = fuzz.trimf(self.collison_ang.universe, [-135,-90,-25])
        #
        # self.rule4 = ctrl.Rule(self.collison_ang['0'], self.next_move_pm_left['left'])
        # self.rule5 = ctrl.Rule(self.collison_ang['90'], self.next_move_pm_left['down'])
        # self.rule6 = ctrl.Rule(self.collison_ang['-90'], self.next_move_pm_left['up'])

        self.collison_ang_2 = ctrl.Antecedent(np.arange(-181, 181, 1), 'collison_ang_2')
        '''Based on a clock with respect the the snake head'''
        self.collison_ang_2['0'] = fuzz.trapmf(self.collison_ang_2.universe,[-90,-45,45,90])
        self.collison_ang_2['90'] = fuzz.trimf(self.collison_ang_2.universe,[45,90,135])
        self.collison_ang_2['-90'] = fuzz.trimf(self.collison_ang_2.universe, [-135,-90,-45])

        self.rule7 = ctrl.Rule(self.collison_ang_2['0'], self.next_move_pm_left['left'])
        self.rule8 = ctrl.Rule(self.collison_ang_2['90'], self.next_move_pm_left['down'])
        self.rule9 = ctrl.Rule(self.collison_ang_2['-90'], self.next_move_pm_left['up'])

        self.weight_snake = ctrl.Antecedent(np.arange(-10,10,1),'weight_snake')
        self.weight_snake['left'] = fuzz.trapmf(self.weight_snake.universe,[-10,-10,-2,0])
        self.weight_snake['right'] = fuzz.trapmf(self.weight_snake.universe,[0,2,10,10])

        self.rule10 = ctrl.Rule(self.weight_snake['left'], self.next_move_pm_left['up'])
        self.rule11= ctrl.Rule(self.weight_snake['right'], self.next_move_pm_left['down'])

        self.spiral_snake = ctrl.Antecedent(np.arange(-91,91,1),'spiral_snake')
        self.spiral_snake['-90'] = fuzz.trimf(self.spiral_snake.universe,[-91,-90,-89])
        self.spiral_snake['90'] = fuzz.trimf(self.spiral_snake.universe,[89,90,91])
        self.spiral_snake['0'] = fuzz.trimf(self.spiral_snake.universe,[-1,0,1])

        self.rule12 = ctrl.Rule(self.spiral_snake['-90'], self.next_move_pm_left['up'])
        self.rule13= ctrl.Rule(self.spiral_snake['90'], self.next_move_pm_left['down'])
        self.rule14= ctrl.Rule(self.spiral_snake['0'], self.next_move_pm_left['left'])

        self.collison_brick_ang = ctrl.Antecedent(np.arange(-181, 181, 1), 'collison_brick_ang')
        '''Based on a clock with respect the the snake head'''
        self.collison_brick_ang['0'] = fuzz.trimf(self.collison_brick_ang.universe,[-1,0,1])
        self.collison_brick_ang['90'] = fuzz.trimf(self.collison_brick_ang.universe,[-25,90,135])
        self.collison_brick_ang['-90'] = fuzz.trimf(self.collison_brick_ang.universe, [-135,-90,25])

        self.rule15 = ctrl.Rule(self.collison_brick_ang['0'], self.next_move_pm_left['left'])
        self.rule16 = ctrl.Rule(self.collison_brick_ang['90'], self.next_move_pm_left['down'])
        self.rule17 = ctrl.Rule(self.collison_brick_ang['-90'], self.next_move_pm_left['up'])

        self.collison_brick_ang_2 = ctrl.Antecedent(np.arange(-181, 181, 1), 'collison_brick_ang_2')
        '''Based on a clock with respect the the snake head'''
        self.collison_brick_ang_2['0'] = fuzz.trapmf(self.collison_brick_ang_2.universe,[-50,-25,25,50])
        self.collison_brick_ang_2['90'] = fuzz.trimf(self.collison_brick_ang_2.universe,[25,90,135])
        self.collison_brick_ang_2['-90'] = fuzz.trimf(self.collison_brick_ang_2.universe, [-135,-90,-25])

        self.rule18 = ctrl.Rule(self.collison_brick_ang_2['0'], self.next_move_pm_left['left'])
        self.rule19 = ctrl.Rule(self.collison_brick_ang_2['90'], self.next_move_pm_left['down'])
        self.rule20 = ctrl.Rule(self.collison_brick_ang_2['-90'], self.next_move_pm_left['up'])

###############################################################################################
    '''Membership Function of the snake when the Snake is facing Up'''
    def mf_pm_up(self):
        '''if the previous move is UP, the only direciton
        you can move is UP, LEFT, RIGHT'''
        self.next_move_pm_up = ctrl.Consequent(np.arange(0, 101, 1), 'Next Direction')
        self.next_move_pm_up['left'] = fuzz.trapmf(self.next_move_pm_up.universe,[0,0,25, 50])
        self.next_move_pm_up['up'] = fuzz.trimf(self.next_move_pm_up.universe,[25,50,75])
        self.next_move_pm_up['right'] = fuzz.trapmf(self.next_move_pm_up.universe, [50,75,100,100])

        self.food_loc = ctrl.Antecedent(np.arange(-181, 181, 1), 'food_loc')
        '''Based on a clock with respect the the snake head'''
        self.food_loc['up'] = fuzz.trimf(self.food_loc.universe,[-50,0, 50])
        self.food_loc['right'] = fuzz.trimf(self.food_loc.universe,[45,135,181])
        self.food_loc['left'] = fuzz.trimf(self.food_loc.universe, [-181,-135,-45])

        self.rule1 = ctrl.Rule(self.food_loc['up'], self.next_move_pm_up['up'])
        self.rule2 = ctrl.Rule(self.food_loc['left'], self.next_move_pm_up['left'])
        self.rule3 = ctrl.Rule(self.food_loc['right'], self.next_move_pm_up['right'])

        # self.collison_ang = ctrl.Antecedent(np.arange(-181, 181, 1), 'collison_ang')
        # '''Based on a clock with respect the the snake head'''
        # self.collison_ang['0'] = fuzz.trapmf(self.collison_ang.universe,[-50,-25,25,50])
        # self.collison_ang['90'] = fuzz.trimf(self.collison_ang.universe,[25,90,135])
        # self.collison_ang['-90'] = fuzz.trimf(self.collison_ang.universe, [-135,-90,-25])
        #
        # self.rule4 = ctrl.Rule(self.collison_ang['0'], self.next_move_pm_up['up'])
        # self.rule5 = ctrl.Rule(self.collison_ang['90'], self.next_move_pm_up['left'])
        # self.rule6 = ctrl.Rule(self.collison_ang['-90'], self.next_move_pm_up['right'])

        self.collison_ang_2 = ctrl.Antecedent(np.arange(-181, 181, 1), 'collison_ang_2')
        '''Based on a clock with respect the the snake head'''
        self.collison_ang_2['0'] = fuzz.trapmf(self.collison_ang_2.universe,[-90,-45,45,90])
        self.collison_ang_2['90'] = fuzz.trimf(self.collison_ang_2.universe,[45,90,135])
        self.collison_ang_2['-90'] = fuzz.trimf(self.collison_ang_2.universe, [-135,-90,-45])

        self.rule7 = ctrl.Rule(self.collison_ang_2['0'], self.next_move_pm_up['up'])
        self.rule8 = ctrl.Rule(self.collison_ang_2['90'], self.next_move_pm_up['left'])
        self.rule9 = ctrl.Rule(self.collison_ang_2['-90'], self.next_move_pm_up['right'])

        self.weight_snake = ctrl.Antecedent(np.arange(-10,10,1),'weight_snake')
        self.weight_snake['left'] = fuzz.trapmf(self.weight_snake.universe,[-10,-10,-2,0])
        self.weight_snake['right'] = fuzz.trapmf(self.weight_snake.universe,[0,2,10,10])

        self.rule10 = ctrl.Rule(self.weight_snake['left'], self.next_move_pm_up['right'])
        self.rule11= ctrl.Rule(self.weight_snake['right'], self.next_move_pm_up['left'])

        self.spiral_snake = ctrl.Antecedent(np.arange(-91,91,1),'spiral_snake')
        self.spiral_snake['-90'] = fuzz.trimf(self.spiral_snake.universe,[-91,-90,-89])
        self.spiral_snake['90'] = fuzz.trimf(self.spiral_snake.universe,[89,90,91])
        self.spiral_snake['0'] = fuzz.trimf(self.spiral_snake.universe,[-1,0,1])

        self.rule12 = ctrl.Rule(self.spiral_snake['-90'], self.next_move_pm_up['right'])
        self.rule13= ctrl.Rule(self.spiral_snake['90'], self.next_move_pm_up['left'])
        self.rule14= ctrl.Rule(self.spiral_snake['0'], self.next_move_pm_up['up'])

        self.collison_brick_ang = ctrl.Antecedent(np.arange(-181, 181, 1), 'collison_brick_ang')
        '''Based on a clock with respect the the snake head'''
        self.collison_brick_ang['0'] = fuzz.trimf(self.collison_brick_ang.universe,[-1,0,1])
        self.collison_brick_ang['90'] = fuzz.trimf(self.collison_brick_ang.universe,[-25,90,135])
        self.collison_brick_ang['-90'] = fuzz.trimf(self.collison_brick_ang.universe, [-135,-90,25])

        self.rule15 = ctrl.Rule(self.collison_brick_ang['0'], self.next_move_pm_up['up'])
        self.rule16 = ctrl.Rule(self.collison_brick_ang['90'], self.next_move_pm_up['left'])
        self.rule17 = ctrl.Rule(self.collison_brick_ang['-90'], self.next_move_pm_up['right'])

        self.collison_brick_ang_2 = ctrl.Antecedent(np.arange(-181, 181, 1), 'collison_brick_ang_2')
        '''Based on a clock with respect the the snake head'''
        self.collison_brick_ang_2['0'] = fuzz.trapmf(self.collison_brick_ang_2.universe,[-50,-25,25,50])
        self.collison_brick_ang_2['90'] = fuzz.trimf(self.collison_brick_ang_2.universe,[25,90,135])
        self.collison_brick_ang_2['-90'] = fuzz.trimf(self.collison_brick_ang_2.universe, [-135,-90,-25])

        self.rule18 = ctrl.Rule(self.collison_brick_ang_2['0'], self.next_move_pm_up['up'])
        self.rule19 = ctrl.Rule(self.collison_brick_ang_2['90'], self.next_move_pm_up['left'])
        self.rule20 = ctrl.Rule(self.collison_brick_ang_2['-90'], self.next_move_pm_up['right'])
###############################################################################################
    '''Membership Function of the snake when the Snake is facing down'''
    def mf_pm_down(self):
        '''if the previous move is DOWN, the only direciton
        you can move is DOWN, LEFT, RIGHT'''
        self.next_move_pm_down = ctrl.Consequent(np.arange(0, 101, 1), 'Next Direction')
        self.next_move_pm_down['left'] = fuzz.trapmf(self.next_move_pm_down.universe,[0,0,25, 50])
        self.next_move_pm_down['down'] = fuzz.trimf(self.next_move_pm_down.universe,[25,50,75])
        self.next_move_pm_down['right'] = fuzz.trapmf(self.next_move_pm_down.universe,[50,75,100,100])

        self.food_loc = ctrl.Antecedent(np.arange(-181, 181, 1), 'food_loc')
        '''Based on a clock with respect the the snake head'''
        self.food_loc['up'] = fuzz.trimf(self.food_loc.universe,[-50,0, 50])
        self.food_loc['right'] = fuzz.trimf(self.food_loc.universe,[45,135,181])
        self.food_loc['left'] = fuzz.trimf(self.food_loc.universe, [-181,-135,-45])

        self.rule1 = ctrl.Rule(self.food_loc['up'], self.next_move_pm_down['down'])
        self.rule2 = ctrl.Rule(self.food_loc['left'], self.next_move_pm_down['right'])
        self.rule3 = ctrl.Rule(self.food_loc['right'], self.next_move_pm_down['left'])

        # self.collison_ang = ctrl.Antecedent(np.arange(-181, 181, 1), 'collison_ang')
        # '''Based on a clock with respect the the snake head'''
        # self.collison_ang['0'] = fuzz.trapmf(self.collison_ang.universe,[-50,-25,25,50])
        # self.collison_ang['90'] = fuzz.trimf(self.collison_ang.universe,[25,90,135])
        # self.collison_ang['-90'] = fuzz.trimf(self.collison_ang.universe, [-135,-90,-25])
        #
        # self.rule4 = ctrl.Rule(self.collison_ang['0'], self.next_move_pm_down['down'])
        # self.rule5 = ctrl.Rule(self.collison_ang['90'], self.next_move_pm_down['right'])
        # self.rule6 = ctrl.Rule(self.collison_ang['-90'], self.next_move_pm_down['left'])

        self.collison_ang_2 = ctrl.Antecedent(np.arange(-181, 181, 1), 'collison_ang_2')
        '''Based on a clock with respect the the snake head'''
        self.collison_ang_2['0'] = fuzz.trapmf(self.collison_ang_2.universe,[-90,-45,45,90])
        self.collison_ang_2['90'] = fuzz.trimf(self.collison_ang_2.universe,[45,90,135])
        self.collison_ang_2['-90'] = fuzz.trimf(self.collison_ang_2.universe, [-135,-90,-45])

        self.rule7 = ctrl.Rule(self.collison_ang_2['0'], self.next_move_pm_down['down'])
        self.rule8 = ctrl.Rule(self.collison_ang_2['90'], self.next_move_pm_down['right'])
        self.rule9 = ctrl.Rule(self.collison_ang_2['-90'], self.next_move_pm_down['left'])

#From the viewpoint of the snake
        self.weight_snake = ctrl.Antecedent(np.arange(-10,10,1),'weight_snake')
        self.weight_snake['left'] = fuzz.trapmf(self.weight_snake.universe,[-10,-10,0,0])
        self.weight_snake['right'] = fuzz.trapmf(self.weight_snake.universe,[0,0,10,10])

        self.rule10 = ctrl.Rule(self.weight_snake['left'], self.next_move_pm_down['left'])
        self.rule11= ctrl.Rule(self.weight_snake['right'], self.next_move_pm_down['right'])

        self.spiral_snake = ctrl.Antecedent(np.arange(-91,91,1),'spiral_snake')
        self.spiral_snake['-90'] = fuzz.trimf(self.spiral_snake.universe,[-91,-90,-89])
        self.spiral_snake['90'] = fuzz.trimf(self.spiral_snake.universe,[89,90,91])
        self.spiral_snake['0'] = fuzz.trimf(self.spiral_snake.universe,[-1,0,1])

        self.rule12 = ctrl.Rule(self.spiral_snake['-90'], self.next_move_pm_down['left'])
        self.rule13= ctrl.Rule(self.spiral_snake['90'], self.next_move_pm_down['right'])
        self.rule14= ctrl.Rule(self.spiral_snake['0'], self.next_move_pm_down['down'])

        self.collison_brick_ang = ctrl.Antecedent(np.arange(-181, 181, 1), 'collison_brick_ang')
        '''Based on a clock with respect the the snake head'''
        self.collison_brick_ang['0'] = fuzz.trimf(self.collison_brick_ang.universe,[-1,0,1])
        self.collison_brick_ang['90'] = fuzz.trimf(self.collison_brick_ang.universe,[-25,90,135])
        self.collison_brick_ang['-90'] = fuzz.trimf(self.collison_brick_ang.universe, [-135,-90,25])

        self.rule15 = ctrl.Rule(self.collison_brick_ang['0'], self.next_move_pm_down['down'])
        self.rule16 = ctrl.Rule(self.collison_brick_ang['90'], self.next_move_pm_down['right'])
        self.rule17 = ctrl.Rule(self.collison_brick_ang['-90'], self.next_move_pm_down['left'])

        self.collison_brick_ang_2 = ctrl.Antecedent(np.arange(-181, 181, 1), 'collison_brick_ang_2')
        '''Based on a clock with respect the the snake head'''
        self.collison_brick_ang_2['0'] = fuzz.trapmf(self.collison_brick_ang_2.universe,[-50,-25,25,50])
        self.collison_brick_ang_2['90'] = fuzz.trimf(self.collison_brick_ang_2.universe,[25,90,135])
        self.collison_brick_ang_2['-90'] = fuzz.trimf(self.collison_brick_ang_2.universe, [-135,-90,-25])

        self.rule18 = ctrl.Rule(self.collison_brick_ang_2['0'], self.next_move_pm_down['down'])
        self.rule19 = ctrl.Rule(self.collison_brick_ang_2['90'], self.next_move_pm_down['right'])
        self.rule20 = ctrl.Rule(self.collison_brick_ang_2['-90'], self.next_move_pm_down['left'])
###############################################################################################

    def get_angle_pm_right(self,food_y, food_x, snake_y,snake_x):
        '''Angle is based on the 4 quadrant
        We require to convert it back where 0 is the y-axis'''
        #print(str(food_y) + " " + str(food_x) + " " + str(snake_y) +" " + str(snake_x))
        angle = m.degrees(m.atan2((food_y-snake_y),(food_x - snake_x)))
        if angle <= 90 and angle >= 0:
            final_angle = angle
        if angle >= 90 and angle <= 180:
            final_angle = angle
        if  -90 <=angle <= 0:
            final_angle = angle
        if angle >= -180 and angle <= -90:
            final_angle = angle
        return int(final_angle)

    def get_angle_pm_left(self,food_y, food_x, snake_y,snake_x):
        '''Angle is based on the 4 quadrant
        We require to convert it back where 0 is the y-axis'''
        #print(str(food_y) + " " + str(food_x) + " " + str(snake_y) +" " + str(snake_x))
        angle = m.degrees(m.atan2((food_y-snake_y),(food_x - snake_x)))
        if angle <= 90 and angle >= 0:
            final_angle = -(180-angle)
        if angle >= 90 and angle <= 180:
            final_angle = -(180-angle)
        if  -90 <=angle <= 0:
            final_angle = 180 + angle
        if angle >= -180 and angle <= -90:
            final_angle = 180 + angle
        return int(final_angle)

    def get_angle_pm_up(self,food_y, food_x, snake_y,snake_x):
        '''Angle is based on the 4 quadrant
        We require to convert it back where 0 is the y-axis'''
        #print(str(food_y) + " " + str(food_x) + " " + str(snake_y) +" " + str(snake_x))
        angle = m.degrees(m.atan2((food_y-snake_y),(food_x - snake_x)))
        if angle <= 90 and angle >= 0:
            final_angle = 90 + angle
        if angle >= 90 and angle <= 180:
            final_angle = (angle - 90)-180
        if  -90 <=angle <= 0:
            final_angle = 90 + angle
        if angle >= -180 and angle <= -90:
            final_angle = angle + 90
        return int(final_angle)

    def get_angle_pm_down(self,food_y, food_x, snake_y,snake_x):
        '''Angle is based on the 4 quadrant
        We require to convert it back where 0 is the y-axis'''
        #print(str(food_y) + " " + str(food_x) + " " + str(snake_y) +" " + str(snake_x))
        angle = m.degrees(m.atan2((food_y-snake_y),(food_x - snake_x)))
        if angle <= 90 and angle >= 0:
            final_angle = -(90 - angle)
        if angle >= 90 and angle <= 180:
            final_angle = angle - 90
        if  -90 <=angle <= 0:
            final_angle = angle-90
        if angle >= -180 and angle <= -90:
            final_angle = 270+angle
        return int(final_angle)

    #Calculate Mahatten Distance
    #Put in a list of x and y values
    def manhatten_distance(self, snake_x , snake_y):
        overall_man_dist = []
        for i in range(0,len(snake_x)):
            x_head = snake_x[0]
            y_head = snake_y[0]
            manhatten_distance = int((abs(x_head - snake_x[i]) + abs(y_head - snake_y[i]))/44)
            overall_man_dist.append(manhatten_distance)
        return overall_man_dist

        '''To check the last position of the snake if it contains this number -100. It happens when
        the snake eats the food and the game appends one more element to the list immediately'''
    def check_snake(self,snake_x , snake_y):
        length_of_snake = len(snake_x)
        if snake_x[-1] == -100:
            snake_x.pop()
            snake_y.pop()
        else:
            pass
        print(snake_x)
        print(snake_y)
        return snake_x,snake_y



    def weight_snake_pm_up(self,snake_x , snake_y):
        snake_pos = []
        left = 0
        right = 0
        center = 0
        for i in range(0,len(snake_x)):
            x_head = snake_x[0]
            y_head = snake_y[0]
            left_right = int((x_head - snake_x[i])/44)
            snake_pos.append(left_right)
        print(snake_pos)
        for x in snake_pos:
    #         print(x)
            if x > 0:
                left = left + 1
            if x < 0:
                right = right + 1
            if x ==0:
                center = center + 1
        print(left)
        print(right)
        print(center)
        check_left_right = left - right

        if (left == 0 and right == 0) or check_left_right == 0:
            x = random.randint(1,3)
            if x == 1:
                print('Snek is in a straight line so RNG God says move to the Left (-10)')
                overall = -10
                return overall
            else:
                print('Snek is in a straight line so RNG God says move to the  right (10)')
                overall = 10
                return overall
        else:
            overall = ((right-left)/(right + left)) * 10
            print(overall)
            return overall

    def weight_snake_pm_down(self,snake_x , snake_y):
        snake_pos = []
        left = 0
        right = 0
        center = 0
        for i in range(0,len(snake_x)):
            x_head = snake_x[0]
            y_head = snake_y[0]
            left_right = int((x_head - snake_x[i])/44)
            snake_pos.append(left_right)
        print(snake_pos)
        for x in snake_pos:
    #         print(x)
            if x < 0:
                left = left + 1
            if x >0:
                right = right + 1
            if x ==0:
                center = center + 1
        print(left)
        print(right)
        print(center)
        check_left_right = left - right

        if (left == 0 and right == 0) or check_left_right == 0:
            x = random.randint(1,3)
            if x == 1:
                print('Snek is in a straight line so RNG God says move to the Left (-10)')
                overall = -10
                return overall
            else:
                print('Snek is in a straight line so RNG God says move to the  right (10)')
                overall = 10
                return overall
        else:
            overall = ((right-left)/(right + left)) * 10
            print(overall)
            return overall

    def weight_snake_pm_left(self,snake_x , snake_y):
        snake_pos = []
        left = 0
        right = 0
        center = 0
        for i in range(0,len(snake_x)):
            x_head = snake_x[0]
            y_head = snake_y[0]
            left_right = int((y_head - snake_y[i])/44)
            snake_pos.append(left_right)
        print(snake_pos)
        for y in snake_pos:
            if y < 0:
                left = left + 1
            if y > 0:
                right = right + 1
            if y ==0:
                center = center + 1
        print(left)
        print(right)
        print(center)
        check_left_right = left - right

        if (left == 0 and right == 0) or check_left_right == 0:
            x = random.randint(1,3)
            if x == 1:
                print('Snek is in a straight line so RNG God says move to the Left (-10)')
                overall = -10
                return overall
            else:
                print('Snek is in a straight line so RNG God says move to the  right (10)')
                overall = 10
                return overall
        else:
            overall = ((right-left)/(right + left)) * 10
            print(overall)
            return overall


    def weight_snake_pm_right(self,snake_x , snake_y):
        snake_pos = []
        left = 0
        right = 0
        center = 0
        for i in range(0,len(snake_x)):
            x_head = snake_x[0]
            y_head = snake_y[0]
            left_right = int((y_head - snake_y[i])/44)
            snake_pos.append(left_right)
        print(snake_pos)
        for y in snake_pos:
            if y > 0:
                left = left + 1
            if y < 0:
                right = right + 1
            if y ==0:
                center = center + 1
        print(left)
        print(right)
        print(center)
        check_left_right = left - right

        if (left == 0 and right == 0) or check_left_right == 0:
            x = random.randint(1,3)
            if x == 1:
                print('Snek is in a straight line so RNG God says move to the Left (-10)')
                overall = -10
                return overall
            else:
                print('Snek is in a straight line so RNG God says move to the  right (10)')
                overall = 10
                return overall
        else:
            overall = ((right-left)/(right + left)) * 10
            print(overall)
            return overall

    def spiral_pm_right(self,snake_x , snake_y):
        angle_of_snake_body = []
        x_head = snake_x[0]
        y_head = snake_y[0]
        man_distance = self.manhatten_distance(snake_x , snake_y)
        for i in range(2, len(man_distance)):
            angle = self.get_angle_pm_right(snake_y[i], snake_x[i], y_head,x_head)
            angle_of_snake_body.append(angle)
        print(angle_of_snake_body)
        for angle in angle_of_snake_body:
            if angle == 90:
                print('Spiral Angle is' + str(angle))
                return angle
            elif angle == -90:
                print('Spiral Angle is' + str(angle))
                return angle
            elif angle ==0:
                print('Spiral Angle is' + str(angle))
                return angle
    def spiral_pm_left(self,snake_x , snake_y):
        angle_of_snake_body = []
        x_head = snake_x[0]
        y_head = snake_y[0]
        man_distance = self.manhatten_distance(snake_x , snake_y)
        for i in range(2, len(man_distance)):
            angle = self.get_angle_pm_left(snake_y[i], snake_x[i], y_head,x_head)
            angle_of_snake_body.append(angle)
        print(angle_of_snake_body)
        for angle in angle_of_snake_body:
            if angle == 90:
                print('Spiral Angle is' + str(angle))
                return angle
            elif angle == -90:
                print('Spiral Angle is' + str(angle))
                return angle
            elif angle ==0:
                print('Spiral Angle is' + str(angle))
                return angle

    def spiral_pm_up(self,snake_x , snake_y):
        angle_of_snake_body = []
        x_head = snake_x[0]
        y_head = snake_y[0]
        man_distance = self.manhatten_distance(snake_x , snake_y)
        for i in range(2, len(man_distance)):
            angle = self.get_angle_pm_up(snake_y[i], snake_x[i], y_head,x_head)
            angle_of_snake_body.append(angle)
        print(angle_of_snake_body)
        for angle in angle_of_snake_body:
            if angle == 90:
                return angle
                print('Spiral Angle is' + str(angle))
            elif angle == -90:
                print('Spiral Angle is' + str(angle))
                return angle
            elif angle ==0:
                print('Spiral Angle is' + str(angle))
                return angle

    def spiral_pm_down(self,snake_x , snake_y):
        angle_of_snake_body = []
        x_head = snake_x[0]
        y_head = snake_y[0]
        man_distance = self.manhatten_distance(snake_x , snake_y)
        for i in range(2, len(man_distance)):
            angle = self.get_angle_pm_down(snake_y[i], snake_x[i], y_head,x_head)
            angle_of_snake_body.append(angle)
        print(angle_of_snake_body)
        for angle in angle_of_snake_body:
            if angle == 90:
                print('Spiral Angle is' + str(angle))
                return angle
            elif angle == -90:
                print('Spiral Angle is' + str(angle))
                return angle
            elif angle ==0:
                print('Spiral Angle is' + str(angle))
                return angle

    def manhatten_distance_brick(self, snake_x , snake_y, brick_x, brick_y):
        overall_man_dist_brick = []
        x_head = snake_x[0]
        y_head = snake_y[0]
        for i in range(0,len(brick_x)):
            manhatten_distance = int((abs(x_head - brick_x[i]) + abs(y_head - brick_y[i]))/44)
            overall_man_dist_brick.append(manhatten_distance)
        return overall_man_dist_brick

    def perform_next_move(self, snake, food, bricks):
        overall_rules = []
        indicator = 0 #counter for offending angle
        ind_brick = 0
        if self.current_move_number < self.max_moves:
            if self.old_snake_pos_y ==  snake.y[0] and self.old_snake_pos_x == snake.x[0] and self.current_move_number != 0:
                if snake.direction == constants.LEFT:
                    snake.moveLeft()
                if snake.direction == constants.RIGHT:
                    snake.moveRight()
                if snake.direction == constants.UP:
                    snake.moveUp()
                if snake.direction == constants.DOWN:
                    snake.moveDown()
                self.current_move_number += 1
            else:

                if snake.direction == constants.RIGHT:
                    self.mf_pm_right()
                    # overall_rules = [self.rule1, self.rule2, self.rule3]
                    overall_rules = []


                    angle = self.get_angle_pm_right(food.y, food.x, snake.y[0], snake.x[0])
                    print("Food Angle :" +str(angle))
                    snake_x,snake_y = self.check_snake(snake.x[0:snake.length],snake.y[0:snake.length])
                    overall_man_dist = self.manhatten_distance(snake_x,snake_y)
                    print(overall_man_dist)
                    print("Checking the Bricks Distance")
                    manhatten_distance_brick = self.manhatten_distance_brick(snake_x,snake_y,bricks.x,bricks.y)
                    print(manhatten_distance_brick)

                    for i in range(0, len(manhatten_distance_brick)):
                        if manhatten_distance_brick[i] == 1:
                            ind_brick = ind_brick +1
                            if ind_brick ==1:
                                print('Offending Brick part is:' + " " +str(snake.y[0]) + " " +str(snake.x[0]) + " " +
                                        str(bricks.y[i]) + " " +str(bricks.x[i]))
                                brick_collison_angle = self.get_angle_pm_right(bricks.y[i], bricks.x[i],snake.y[0], snake.x[0])
                                print('1st Brick Collison angle is :' + str(brick_collison_angle))
                                print(i)
                                print(ind_brick)
                            elif ind_brick == 2:
                                print(i)
                                print(ind_brick)
                                print('2nd Offending Brick part is:' + " " +str(snake.y[0]) + " " +str(snake.x[0]) + " " +
                                        str(bricks.y[i]) + " " +str(bricks.x[i]))
                                brick_collison_angle_2 = self.get_angle_pm_right(bricks.y[i], bricks.x[i],snake.y[0], snake.x[0])
                                print('2nd Brick Collison angle is :' + str(brick_collison_angle_2))
                            else:
                                pass

                    if len(snake_x) > 4:
                        for i in range(3, len(overall_man_dist)):
                            if overall_man_dist[i] == 1:
                                indicator = indicator + 1
                                if indicator ==1:
                                    print('Offending part is:' + " " +str(snake.y[0]) + " " +str(snake.x[0]) + " " +
                                            str(snake_y[i]) + " " +str(snake_x[i]))
                                    collison_angle = self.get_angle_pm_right(snake_y[i], snake_x[i],snake.y[0], snake.x[0])
                                    print('Collison angle is :' + str(collison_angle))
                                elif indicator == 2:
                                    print('2nd Offending part is:' + " " +str(snake.y[0]) + " " +str(snake.x[0]) + " " +
                                            str(snake_y[i]) + " " +str(snake_x[i]))
                                    collison_angle_2 = self.get_angle_pm_right(snake_y[i], snake_x[i],snake.y[0], snake.x[0])
                                    print('2nd Collison angle is :' + str(collison_angle_2))
                                else:
                                    pass

                    print("Brick Indicator is " + str(ind_brick) + " Indicator is " + str(indicator))
                    if indicator == 1  and ind_brick == 1:
                        print('yeah')
                        overall_weight = self.weight_snake_pm_right(snake_x,snake_y)
                        print("Overall Weight is " + str(overall_weight))
                        spiral_angle = self.spiral_pm_right(snake_x,snake_y)
                        overall_rules.extend((self.rule1, self.rule2, self.rule3,
                                            self.rule10,self.rule11,self.rule12,self.rule13,self.rule14,
                                            self.rule15,self.rule16,self.rule17))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle

                    elif indicator == 1  and ind_brick > 1:
                        print('yeah')
                        overall_weight = self.weight_snake_pm_right(snake_x,snake_y)
                        print("Overall Weight is " + str(overall_weight))
                        spiral_angle = self.spiral_pm_right(snake_x,snake_y)
                        overall_rules.extend((self.rule1, self.rule2, self.rule3,
                                            self.rule10,self.rule11,self.rule12,self.rule13,self.rule14,
                                            self.rule18,self.rule19,self.rule20))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator == 1  and ind_brick == 0:
                        overall_weight = self.weight_snake_pm_right(snake_x,snake_y)
                        print("Overall Weight is " + str(overall_weight))
                        spiral_angle = self.spiral_pm_right(snake_x,snake_y)
                        overall_rules.extend((self.rule1, self.rule2, self.rule3,
                                            self.rule10,self.rule11,self.rule12,self.rule13,self.rule14))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator >= 2 and ind_brick == 1:
                        print('bah')
                        overall_weight = self.weight_snake_pm_right(snake_x,snake_y)
                        spiral_angle = self.spiral_pm_right(snake_x,snake_y)
                        overall_rules.extend((self.rule7, self.rule8, self.rule9,
                                            self.rule12,self.rule13,self.rule14,
                                            self.rule15,self.rule16,self.rule17))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        # next_move_crtl_fuzzy.input['food_loc'] = angle
                        next_move_crtl_fuzzy.input['collison_ang_2'] = collison_angle_2 + collison_angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        # next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator >= 2 and ind_brick > 1:
                        print('bah')
                        overall_weight = self.weight_snake_pm_right(snake_x,snake_y)
                        spiral_angle = self.spiral_pm_right(snake_x,snake_y)
                        overall_rules.extend((self.rule7, self.rule8, self.rule9,
                                            self.rule12,self.rule13,self.rule14,
                                            self.rule18,self.rule19,self.rule20))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        # next_move_crtl_fuzzy.input['food_loc'] = angle
                        next_move_crtl_fuzzy.input['collison_ang_2'] = collison_angle_2 + collison_angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        # next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator >= 2 and ind_brick == 0:
                        print('bah')
                        overall_weight = self.weight_snake_pm_right(snake_x,snake_y)
                        spiral_angle = self.spiral_pm_right(snake_x,snake_y)
                        overall_rules.extend((self.rule7, self.rule8, self.rule9,
                                            self.rule12,self.rule13,self.rule14))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        # next_move_crtl_fuzzy.input['food_loc'] = angle
                        next_move_crtl_fuzzy.input['collison_ang_2'] = collison_angle_2 + collison_angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        # next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator == 0 and ind_brick == 1:
                        overall_weight = self.weight_snake_pm_right(snake_x,snake_y)
                        print("Overall Weight is " + str(overall_weight))
                        next_move_crtl = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3,
                                                            self.rule10,self.rule11,
                                                            self.rule15,self.rule16,self.rule17])
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle

                        #This is to artically force the snake to move away from the overall snake body
                        if brick_collison_angle == 0:
                                print('Snek heading straight on so we depend on our Weight Goddess')
                                brick_collison_angle = (overall_weight -0) *9
                        print(brick_collison_angle)
                        next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        next_move_crtl_fuzzy.input['weight_snake'] = overall_weight

                    elif indicator == 0 and ind_brick > 1:
                        next_move_crtl = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3,
                                                            self.rule18,self.rule19,self.rule20])
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    else:
                        next_move_crtl = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3])
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle


                    result = next_move_crtl_fuzzy.compute()
                    result = int(next_move_crtl_fuzzy.output['Next Direction'])
                    print(str(result)+" is the output score." )
                    if result >= 0 and result < 40:
                        snake.moveUp()
                        print("Move up1")
                        print("################")
                    if result >=40 and result <=60:
                        snake.moveRight()
                        print("Move right2")
                        print("################")
                    if result >60 and result <= 100:
                        snake.moveDown()
                        print("Move down3")
                        print("################")


                elif snake.direction == constants.LEFT:
                    self.mf_pm_left()
                    # overall_rules = [self.rule1, self.rule2, self.rule3]
                    overall_rules = []
                    angle = self.get_angle_pm_left(food.y, food.x, snake.y[0], snake.x[0])

                    print("Food Angle :" +str(angle))
                    snake_x,snake_y = self.check_snake(snake.x[0:snake.length],snake.y[0:snake.length])
                    overall_man_dist = self.manhatten_distance(snake_x,snake_y)
                    print(overall_man_dist)
                    print("Checking the Bricks Distance")
                    manhatten_distance_brick = self.manhatten_distance_brick(snake_x,snake_y,bricks.x,bricks.y)
                    print(manhatten_distance_brick)

                    for i in range(0, len(manhatten_distance_brick)):
                        if manhatten_distance_brick[i] == 1:
                            ind_brick = ind_brick +1
                            if ind_brick ==1:
                                print('Offending Brick part is:' + " " +str(snake.y[0]) + " " +str(snake.x[0]) + " " +
                                        str(bricks.y[i]) + " " +str(bricks.x[i]))
                                brick_collison_angle = self.get_angle_pm_left(bricks.y[i], bricks.x[i],snake.y[0], snake.x[0])
                                print('1st Brick Collison angle is :' + str(brick_collison_angle))
                                print(i)
                                print(ind_brick)
                            elif ind_brick == 2:
                                print(i)
                                print(ind_brick)
                                print('2nd Offending Brick part is:' + " " +str(snake.y[0]) + " " +str(snake.x[0]) + " " +
                                        str(bricks.y[i]) + " " +str(bricks.x[i]))
                                brick_collison_angle_2 = self.get_angle_pm_left(bricks.y[i], bricks.x[i],snake.y[0], snake.x[0])
                                print('2nd Brick Collison angle is :' + str(brick_collison_angle_2))
                            else:
                                pass

                    if len(snake_x) > 4:
                        for i in range(3, len(overall_man_dist)):
                            if overall_man_dist[i] == 1:
                                indicator = indicator + 1
                                if indicator ==1:
                                    print('Offending part is:' + " " +str(snake.y[0]) + " " +str(snake.x[0]) + " " +
                                            str(snake_y[i]) + " " +str(snake_x[i]))
                                    collison_angle = self.get_angle_pm_left(snake_y[i], snake_x[i],snake.y[0], snake.x[0])
                                    print('Collison angle is :' + str(collison_angle))
                                elif indicator == 2:
                                    print('2nd Offending part is:' + " " +str(snake.y[0]) + " " +str(snake.x[0]) + " " +
                                            str(snake_y[i]) + " " +str(snake_x[i]))
                                    collison_angle_2 = self.get_angle_pm_left(snake_y[i], snake_x[i],snake.y[0], snake.x[0])
                                    print('2nd Collison angle is :' + str(collison_angle_2))
                                else:
                                    pass

                    print("Brick Indicator is " + str(ind_brick) + " Indicator is " + str(indicator))
                    if indicator == 1  and ind_brick == 1:
                        print('yeah')
                        overall_weight = self.weight_snake_pm_left(snake_x,snake_y)
                        print("Overall Weight is " + str(overall_weight))
                        spiral_angle = self.spiral_pm_left(snake_x,snake_y)
                        overall_rules.extend((self.rule1, self.rule2, self.rule3,
                                            self.rule10,self.rule11,self.rule12,self.rule13,self.rule14,
                                            self.rule15,self.rule16,self.rule17))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle

                    elif indicator == 1  and ind_brick > 1:
                        print('yeah')
                        overall_weight = self.weight_snake_pm_left(snake_x,snake_y)
                        print("Overall Weight is " + str(overall_weight))
                        spiral_angle = self.spiral_pm_left(snake_x,snake_y)
                        overall_rules.extend((self.rule1, self.rule2, self.rule3,
                                            self.rule10,self.rule11,self.rule12,self.rule13,self.rule14,
                                            self.rule18,self.rule19,self.rule20))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator == 1  and ind_brick == 0:
                        overall_weight = self.weight_snake_pm_left(snake_x,snake_y)
                        print("Overall Weight is " + str(overall_weight))
                        spiral_angle = self.spiral_pm_left(snake_x,snake_y)
                        overall_rules.extend((self.rule1, self.rule2, self.rule3,
                                            self.rule10,self.rule11,self.rule12,self.rule13,self.rule14))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator >= 2 and ind_brick == 1:
                        print('bah')
                        overall_weight = self.weight_snake_pm_left(snake_x,snake_y)
                        spiral_angle = self.spiral_pm_left(snake_x,snake_y)
                        overall_rules.extend((self.rule7, self.rule8, self.rule9,
                                            self.rule12,self.rule13,self.rule14,
                                            self.rule15,self.rule16,self.rule17))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        # next_move_crtl_fuzzy.input['food_loc'] = angle
                        next_move_crtl_fuzzy.input['collison_ang_2'] = collison_angle_2 + collison_angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        # next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator >= 2 and ind_brick > 1:
                        print('bah')
                        overall_weight = self.weight_snake_pm_left(snake_x,snake_y)
                        spiral_angle = self.spiral_pm_left(snake_x,snake_y)
                        overall_rules.extend((self.rule7, self.rule8, self.rule9,
                                            self.rule12,self.rule13,self.rule14,
                                            self.rule18,self.rule19,self.rule20))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        # next_move_crtl_fuzzy.input['food_loc'] = angle
                        next_move_crtl_fuzzy.input['collison_ang_2'] = collison_angle_2 + collison_angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        # next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator >= 2 and ind_brick == 0:
                        print('bah')
                        overall_weight = self.weight_snake_pm_left(snake_x,snake_y)
                        spiral_angle = self.spiral_pm_left(snake_x,snake_y)
                        overall_rules.extend((self.rule7, self.rule8, self.rule9,
                                            self.rule12,self.rule13,self.rule14))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        # next_move_crtl_fuzzy.input['food_loc'] = angle
                        next_move_crtl_fuzzy.input['collison_ang_2'] = collison_angle_2 + collison_angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        # next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator == 0 and ind_brick == 1:
                        overall_weight = self.weight_snake_pm_left(snake_x,snake_y)
                        print("Overall Weight is " + str(overall_weight))
                        next_move_crtl = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3,
                                                            self.rule10,self.rule11,
                                                            self.rule15,self.rule16,self.rule17])
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        if brick_collison_angle == 0:
                                print('Snek heading straight on so we depend on our Weight Goddess')
                                brick_collison_angle = (overall_weight -0) *9
                        print(brick_collison_angle)


                        next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        next_move_crtl_fuzzy.input['weight_snake'] = overall_weight

                    elif indicator == 0 and ind_brick > 1:
                        next_move_crtl = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3,
                                                            self.rule18,self.rule19,self.rule20])
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    else:
                        next_move_crtl = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3])
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle

                    result = next_move_crtl_fuzzy.compute()
                    result = int(next_move_crtl_fuzzy.output['Next Direction'])

                    print(str(result)+" is the output score." )
                    if result >= 0 and result < 40:
                        snake.moveUp()
                        print("Move up4")
                        print("################")
                    if result >=40 and result <=60:
                        snake.moveLeft()
                        print("Move Left5")
                        print("################")
                    if result >60 and result <= 100:
                        snake.moveDown()
                        print("Move Down6")
                        print("################")


                elif snake.direction == constants.UP:
                    self.mf_pm_up()
                    # overall_rules = [self.rule1, self.rule2, self.rule3]
                    overall_rules = []
                    angle = self.get_angle_pm_up(food.y, food.x, snake.y[0], snake.x[0])
                    print("Food Angle :" +str(angle))
                    snake_x,snake_y = self.check_snake(snake.x[0:snake.length],snake.y[0:snake.length])
                    overall_man_dist = self.manhatten_distance(snake_x,snake_y)
                    print(overall_man_dist)
                    print("Checking the Bricks Distance")
                    manhatten_distance_brick = self.manhatten_distance_brick(snake_x,snake_y,bricks.x,bricks.y)
                    print(manhatten_distance_brick)

                    for i in range(0, len(manhatten_distance_brick)):
                        if manhatten_distance_brick[i] == 1:
                            ind_brick = ind_brick +1
                            if ind_brick ==1:
                                print('Offending Brick part is:' + " " +str(snake.y[0]) + " " +str(snake.x[0]) + " " +
                                        str(bricks.y[i]) + " " +str(bricks.x[i]))
                                brick_collison_angle = self.get_angle_pm_up(bricks.y[i], bricks.x[i],snake.y[0], snake.x[0])
                                print('1st Brick Collison angle is :' + str(brick_collison_angle))
                                print(i)
                                print(ind_brick)
                            elif ind_brick == 2:
                                print(i)
                                print(ind_brick)
                                print('2nd Offending Brick part is:' + " " +str(snake.y[0]) + " " +str(snake.x[0]) + " " +
                                        str(bricks.y[i]) + " " +str(bricks.x[i]))
                                brick_collison_angle_2 = self.get_angle_pm_up(bricks.y[i], bricks.x[i],snake.y[0], snake.x[0])
                                print('2nd Brick Collison angle is :' + str(brick_collison_angle_2))
                            else:
                                pass

                    if len(snake_x) > 4:
                        for i in range(3, len(overall_man_dist)):
                            if overall_man_dist[i] == 1:
                                indicator = indicator + 1
                                if indicator ==1:
                                    print('Offending part is:' + " " +str(snake.y[0]) + " " +str(snake.x[0]) + " " +
                                            str(snake_y[i]) + " " +str(snake_x[i]))
                                    collison_angle = self.get_angle_pm_up(snake_y[i], snake_x[i],snake.y[0], snake.x[0])
                                    print('Collison angle is :' + str(collison_angle))
                                elif indicator == 2:
                                    print('2nd Offending part is:' + " " +str(snake.y[0]) + " " +str(snake.x[0]) + " " +
                                            str(snake_y[i]) + " " +str(snake_x[i]))
                                    collison_angle_2 = self.get_angle_pm_up(snake_y[i], snake_x[i],snake.y[0], snake.x[0])
                                    print('2nd Collison angle is :' + str(collison_angle_2))
                                else:
                                    pass
                    print("Brick Indicator is " + str(ind_brick) + " Indicator is " + str(indicator))

                    if indicator == 1  and ind_brick == 1:
                        print('yeah')
                        overall_weight = self.weight_snake_pm_up(snake_x,snake_y)
                        print("Overall Weight is " + str(overall_weight))
                        spiral_angle = self.spiral_pm_up(snake_x,snake_y)
                        overall_rules.extend((self.rule1, self.rule2, self.rule3,
                                            self.rule10,self.rule11,self.rule12,self.rule13,self.rule14,
                                            self.rule15,self.rule16,self.rule17))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle

                    elif indicator == 1  and ind_brick > 1:
                        print('yeah')
                        overall_weight = self.weight_snake_pm_up(snake_x,snake_y)
                        print("Overall Weight is " + str(overall_weight))
                        spiral_angle = self.spiral_pm_up(snake_x,snake_y)
                        overall_rules.extend((self.rule1, self.rule2, self.rule3,
                                            self.rule10,self.rule11,self.rule12,self.rule13,self.rule14,
                                            self.rule18,self.rule19,self.rule20))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator == 1  and ind_brick == 0:
                        overall_weight = self.weight_snake_pm_up(snake_x,snake_y)
                        print("Overall Weight is " + str(overall_weight))
                        spiral_angle = self.spiral_pm_up(snake_x,snake_y)
                        overall_rules.extend((self.rule1, self.rule2, self.rule3,
                                            self.rule10,self.rule11,self.rule12,self.rule13,self.rule14))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator >= 2 and ind_brick == 1:
                        print('bah')
                        overall_weight = self.weight_snake_pm_up(snake_x,snake_y)
                        spiral_angle = self.spiral_pm_up(snake_x,snake_y)
                        overall_rules.extend((self.rule7, self.rule8, self.rule9,
                                            self.rule12,self.rule13,self.rule14,
                                            self.rule15,self.rule16,self.rule17))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        # next_move_crtl_fuzzy.input['food_loc'] = angle
                        next_move_crtl_fuzzy.input['collison_ang_2'] = collison_angle_2 + collison_angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        # next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator >= 2 and ind_brick > 1:
                        print('bah')
                        overall_weight = self.weight_snake_pm_up(snake_x,snake_y)
                        spiral_angle = self.spiral_pm_up(snake_x,snake_y)
                        overall_rules.extend((self.rule7, self.rule8, self.rule9,
                                            self.rule12,self.rule13,self.rule14,
                                            self.rule18,self.rule19,self.rule20))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        # next_move_crtl_fuzzy.input['food_loc'] = angle
                        next_move_crtl_fuzzy.input['collison_ang_2'] = collison_angle_2 + collison_angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        # next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator >= 2 and ind_brick == 0:
                        print('bah')
                        overall_weight = self.weight_snake_pm_up(snake_x,snake_y)
                        spiral_angle = self.spiral_pm_up(snake_x,snake_y)
                        overall_rules.extend((self.rule7, self.rule8, self.rule9,
                                            self.rule12,self.rule13,self.rule14))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        # next_move_crtl_fuzzy.input['food_loc'] = angle
                        next_move_crtl_fuzzy.input['collison_ang_2'] = collison_angle_2 + collison_angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        # next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator == 0 and ind_brick == 1:
                        overall_weight = self.weight_snake_pm_up(snake_x,snake_y)
                        print("Overall Weight is " + str(overall_weight))
                        next_move_crtl = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3,
                                                            self.rule10,self.rule11,
                                                            self.rule15,self.rule16,self.rule17])
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        if brick_collison_angle == 0:
                                print('Snek heading straight on so we depend on our Weight Goddess')
                                brick_collison_angle = (overall_weight -0) *9
                        print(brick_collison_angle)
                        next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        next_move_crtl_fuzzy.input['weight_snake'] = overall_weight

                    elif indicator == 0 and ind_brick > 1:
                        next_move_crtl = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3,
                                                            self.rule18,self.rule19,self.rule20])
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    else:
                        next_move_crtl = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3])
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle


                    result = next_move_crtl_fuzzy.compute()
                    result = int(next_move_crtl_fuzzy.output['Next Direction'])
                    print(str(result)+" is the output score." )
                    if result >= 0 and result <40:
                        snake.moveLeft()
                        print("Move Left7")
                        print("################")
                    if result >=40 and result <=60:
                        snake.moveUp()
                        print("Move up8")
                        print("################")
                    if result >60 and result <= 100:
                        snake.moveRight()
                        print("Move Right9")
                        print("################")


                elif snake.direction == constants.DOWN:
                    self.mf_pm_down()
                    # overall_rules = [self.rule1, self.rule2, self.rule3]
                    overall_rules = []
                    angle = self.get_angle_pm_down(food.y, food.x, snake.y[0], snake.x[0])
                    print("Food Angle :" +str(angle))
                    snake_x,snake_y = self.check_snake(snake.x[0:snake.length],snake.y[0:snake.length])
                    overall_man_dist = self.manhatten_distance(snake_x,snake_y)
                    print(overall_man_dist)
                    print("Checking the Bricks Distance")
                    manhatten_distance_brick = self.manhatten_distance_brick(snake_x,snake_y,bricks.x,bricks.y)
                    print(manhatten_distance_brick)

                    for i in range(0, len(manhatten_distance_brick)):
                        if manhatten_distance_brick[i] == 1:
                            ind_brick = ind_brick +1
                            if ind_brick ==1:
                                print('Offending Brick part is:' + " " +str(snake.y[0]) + " " +str(snake.x[0]) + " " +
                                        str(bricks.y[i]) + " " +str(bricks.x[i]))
                                brick_collison_angle = self.get_angle_pm_down(bricks.y[i], bricks.x[i],snake.y[0], snake.x[0])
                                print('1st Brick Collison angle is :' + str(brick_collison_angle))
                                print(i)
                                print(ind_brick)
                            elif ind_brick == 2:
                                print(i)
                                print(ind_brick)
                                print('2nd Offending Brick part is:' + " " +str(snake.y[0]) + " " +str(snake.x[0]) + " " +
                                        str(bricks.y[i]) + " " +str(bricks.x[i]))
                                brick_collison_angle_2 = self.get_angle_pm_down(bricks.y[i], bricks.x[i],snake.y[0], snake.x[0])
                                print('2nd Brick Collison angle is :' + str(brick_collison_angle_2))
                            else:
                                pass

                    if len(snake_x) > 4:
                        for i in range(3, len(overall_man_dist)):
                            if overall_man_dist[i] == 1:
                                indicator = indicator + 1
                                if indicator ==1:
                                    print('Offending part is:' + " " +str(snake.y[0]) + " " +str(snake.x[0]) + " " +
                                            str(snake_y[i]) + " " +str(snake_x[i]))
                                    collison_angle = self.get_angle_pm_down(snake_y[i], snake_x[i],snake.y[0], snake.x[0])
                                    print('Collison angle is :' + str(collison_angle))
                                elif indicator == 2:
                                    print('2nd Offending part is:' + " " +str(snake_y[0]) + " " +str(snake_x[0]) + " " +
                                            str(snake_y[i]) + " " +str(snake_x[i]))
                                    collison_angle_2 = self.get_angle_pm_down(snake_y[i], snake_x[i],snake.y[0], snake.x[0])
                                    print('2nd Collison angle is :' + str(collison_angle_2))
                                else:
                                    pass

                    print("Brick Indicator is " + str(ind_brick) + " Indicator is " + str(indicator))

                    if indicator == 1  and ind_brick == 1:
                        print('yeah')
                        overall_weight = self.weight_snake_pm_down(snake_x,snake_y)
                        print("Overall Weight is " + str(overall_weight))
                        spiral_angle = self.spiral_pm_down(snake_x,snake_y)
                        overall_rules.extend((self.rule1, self.rule2, self.rule3,
                                            self.rule10,self.rule11,self.rule12,self.rule13,self.rule14,
                                            self.rule15,self.rule16,self.rule17))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle

                    elif indicator == 1  and ind_brick > 1:
                        print('yeah')
                        overall_weight = self.weight_snake_pm_down(snake_x,snake_y)
                        print("Overall Weight is " + str(overall_weight))
                        spiral_angle = self.spiral_pm_down(snake_x,snake_y)
                        overall_rules.extend((self.rule1, self.rule2, self.rule3,
                                            self.rule10,self.rule11,self.rule12,self.rule13,self.rule14,
                                            self.rule18,self.rule19,self.rule20))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator == 1  and ind_brick == 0:
                        overall_weight = self.weight_snake_pm_down(snake_x,snake_y)
                        print("Overall Weight is " + str(overall_weight))
                        spiral_angle = self.spiral_pm_down(snake_x,snake_y)
                        overall_rules.extend((self.rule1, self.rule2, self.rule3,
                                            self.rule10,self.rule11,self.rule12,self.rule13,self.rule14))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator >= 2 and ind_brick == 1:
                        print('bah')
                        overall_weight = self.weight_snake_pm_down(snake_x,snake_y)
                        spiral_angle = self.spiral_pm_down(snake_x,snake_y)
                        overall_rules.extend((self.rule7, self.rule8, self.rule9,
                                            self.rule12,self.rule13,self.rule14,
                                            self.rule15,self.rule16,self.rule17))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        # next_move_crtl_fuzzy.input['food_loc'] = angle
                        next_move_crtl_fuzzy.input['collison_ang_2'] = collison_angle_2 + collison_angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        # next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator >= 2 and ind_brick > 1:
                        print('bah')
                        overall_weight = self.weight_snake_pm_down(snake_x,snake_y)
                        spiral_angle = self.spiral_pm_down(snake_x,snake_y)
                        overall_rules.extend((self.rule7, self.rule8, self.rule9,
                                            self.rule12,self.rule13,self.rule14,
                                            self.rule18,self.rule19,self.rule20))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        # next_move_crtl_fuzzy.input['food_loc'] = angle
                        next_move_crtl_fuzzy.input['collison_ang_2'] = collison_angle_2 + collison_angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        # next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator >= 2 and ind_brick == 0:
                        print('bah')
                        overall_weight = self.weight_snake_pm_down(snake_x,snake_y)
                        spiral_angle = self.spiral_pm_down(snake_x,snake_y)
                        overall_rules.extend((self.rule7, self.rule8, self.rule9,
                                            self.rule12,self.rule13,self.rule14))
                        next_move_crtl = ctrl.ControlSystem(overall_rules)
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        # next_move_crtl_fuzzy.input['food_loc'] = angle
                        next_move_crtl_fuzzy.input['collison_ang_2'] = collison_angle_2 + collison_angle
                        # next_move_crtl_fuzzy.input['collison_ang'] = collison_angle
                        # next_move_crtl_fuzzy.input['weight_snake'] = overall_weight
                        next_move_crtl_fuzzy.input['spiral_snake'] = spiral_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        # next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    elif indicator == 0 and ind_brick == 1:
                        overall_weight = self.weight_snake_pm_down(snake_x,snake_y)
                        print("Overall Weight is " + str(overall_weight))
                        next_move_crtl = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3,
                                                            self.rule10,self.rule11,
                                                            self.rule15,self.rule16,self.rule17])
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        if brick_collison_angle == 0:
                                print('Snek heading straight on so we depend on our Weight Goddess')
                                brick_collison_angle = (overall_weight -0) *9
                        print(brick_collison_angle)
                        next_move_crtl_fuzzy.input['collison_brick_ang'] = brick_collison_angle
                        next_move_crtl_fuzzy.input['weight_snake'] = overall_weight

                    elif indicator == 0 and ind_brick > 1:
                        next_move_crtl = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3,
                                                            self.rule18,self.rule19,self.rule20])
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle
                        next_move_crtl_fuzzy.input['collison_brick_ang_2'] = brick_collison_angle_2 + brick_collison_angle

                    else:
                        next_move_crtl = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3])
                        next_move_crtl_fuzzy = ctrl.ControlSystemSimulation(next_move_crtl)
                        next_move_crtl_fuzzy.input['food_loc'] = angle


                    result = next_move_crtl_fuzzy.compute()
                    result = int(next_move_crtl_fuzzy.output['Next Direction'])
                    print(str(result)+" is the output score." )
                    if result >= 0 and result < 40:
                        snake.moveLeft()
                        print("Move Left10")
                        print("################")
                    if result >=40 and result <=60:
                        snake.moveDown()
                        print("Move Down11")
                        print("################")
                    if result >60 and result <= 100:
                        snake.moveRight()
                        print("Move Right12")
                        print("################")

                self.old_snake_pos_y = snake.y[0]
                self.old_snake_pos_x = snake.x[0]

                self.current_move_number += 1
            return snake, True
        return snake, False
