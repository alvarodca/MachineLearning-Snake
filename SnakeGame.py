"""
Snake Eater
Made with PyGame
Last modification in January 2024 by José Carlos Pulido
Machine Learning Classes - University Carlos III of Madrid
"""

import pygame, sys, time, random, csv, os
from wekaI import Weka
import pandas as pd
from scipy.io import arff

weka = Weka()
weka.start_jvm()
# DIFFICULTY settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
DIFFICULTY = 100

# Window size
FRAME_SIZE_X = 480
FRAME_SIZE_Y = 480

# Colors (R, G, B)
BLACK = pygame.Color(51, 51, 51)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(204, 51, 0)
GREEN = pygame.Color(204, 255, 153)
BLUE = pygame.Color(0, 51, 102)

# GAME STATE CLASS
class GameState:
    def __init__(self, FRAME_SIZE):
        self.snake_pos = [100, 50]
        self.snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]]
        self.food_pos = [random.randrange(1, (FRAME_SIZE[0]//10)) * 10, random.randrange(1, (FRAME_SIZE[1]//10)) * 10]
        self.food_spawn = True
        self.direction = 'RIGHT'
        self.prev_direction = self.direction
        self.change_to = self.direction
        self.score = 0
        self.first_tick = True
        self.prev_length = len(self.snake_body)
        # Storing the previous line of data for storing the score 
        self.previous_data = None

        #self.min_vals, self.max_vals = load_min_max("training_keyboard.arff")


        self.file = "training4_computer.arff"

        header = """@RELATION snake_game

    @ATTRIBUTE Head_x NUMERIC
    @ATTRIBUTE Head_y NUMERIC
    @ATTRIBUTE Food_x NUMERIC
    @ATTRIBUTE Food_y NUMERIC
    @ATTRIBUTE Dist_Food_x NUMERIC
    @ATTRIBUTE Dist_Food_y NUMERIC

    @ATTRIBUTE Dist_left_border NUMERIC
    @ATTRIBUTE Dist_right_border NUMERIC
    @ATTRIBUTE Dist_top_border NUMERIC
    @ATTRIBUTE Dist_bottom_border NUMERIC

    @ATTRIBUTE Dist_body_x1 NUMERIC
    @ATTRIBUTE Dist_body_y1 NUMERIC
    @ATTRIBUTE Dist_body_x2 NUMERIC
    @ATTRIBUTE Dist_body_y2 NUMERIC
    
    @ATTRIBUTE Prev_UP NUMERIC
    @ATTRIBUTE Prev_DOWN NUMERIC
    @ATTRIBUTE Prev_RIGHT NUMERIC
 
    @ATTRIBUTE direction {UP, DOWN, LEFT, RIGHT}
    @ATTRIBUTE future_score NUMERIC

    @DATA"""

        # If the ARFF file does not exist, create it with the header
        if not os.path.exists(self.file):
            with open(self.file, "w") as f:
                f.write(header.strip() + "\n\n")

        # Open the ARFF file
        self.arff_file = open(self.file, 'a')

# Game Over
def game_over(game):

    if game.previous_data:
        game.previous_data.append(-1)  
        game.arff_file.write(','.join(map(str, game.previous_data)) + '\n')


    my_font = pygame.font.SysFont('times new roman', 90)
    game_over_surface = my_font.render('YOU DIED', True, WHITE)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (FRAME_SIZE_X/2, FRAME_SIZE_Y/4)
    game_window.fill(BLUE)
    game_window.blit(game_over_surface, game_over_rect)
    show_score(game, 0, WHITE, 'times', 20)
    pygame.display.flip()
    time.sleep(3)
    weka.stop_jvm() # Stopping weka
    pygame.quit()
    sys.exit()

# Score
def show_score(game, choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(game.score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (FRAME_SIZE_X/8, 15)
    else:
        score_rect.midtop = (FRAME_SIZE_X/2, FRAME_SIZE_Y/1.25)
    game_window.blit(score_surface, score_rect)
    # pygame.display.flip()

# Move the snake
def move_keyboard(game, event):
    # Whenever a key is pressed down
    change_to = game.direction
    if event.type == pygame.KEYDOWN:
        game.prev_direction = game.direction
        # W -> Up; S -> Down; A -> Left; D -> Right
        if (event.key == pygame.K_UP or event.key == ord('w')) and game.direction != 'DOWN':
            change_to = 'UP'
        if (event.key == pygame.K_DOWN or event.key == ord('s')) and game.direction != 'UP':
            change_to = 'DOWN'
        if (event.key == pygame.K_LEFT or event.key == ord('a')) and game.direction != 'RIGHT':
            change_to = 'LEFT'
        if (event.key == pygame.K_RIGHT or event.key == ord('d')) and game.direction != 'LEFT':
            change_to = 'RIGHT'
    return change_to


def load_min_max(arff_file):
    data, meta = arff.loadarff(arff_file)
    df = pd.DataFrame(data)
    return df.min().values, df.max().values

def normalize_data(data, min_vals, max_vals):
    """ Normalize numerical values, keep strings unchanged. """
    return [
        (i - min_v) / (max_v - min_v) if isinstance(i, (int, float)) and max_v != min_v else i
        for i, min_v, max_v in zip(data, min_vals, max_vals)
    ]


def move_ml(game):
    # Gather relevant game state data
    head_x, head_y = game.snake_body[0]
    food_x, food_y = game.food_pos
    tail_x, tail_y = game.snake_body[-1]
    score = game.score

    dist_food_x = food_x - head_x
    dist_food_y = food_y - head_y

    # Distance to borders
    dist_left_border = head_x
    dist_right_border = FRAME_SIZE_X - head_x
    dist_up_border = head_y
    dist_down_border = FRAME_SIZE_Y - head_y

    # Distance to closest body parts
    distances = distances_to_head(head_x, head_y, game.snake_body)
    body_x1, body_y1 = distances[0][1], distances[0][2]
    body_x2, body_y2 = distances[1][1], distances[1][2]

    # Handle missing body parts
    if len(distances) < 4:
        dist_body_x3, dist_body_y3 = 500, 500
        dist_body_x4, dist_body_y4 = 500, 500
    else:
        body_x3, body_y3 = distances[2][1], distances[2][2]
        body_x4, body_y4 = distances[3][1], distances[3][2]
        dist_body_x3 = head_x - body_x3
        dist_body_y3 = head_y - body_y3
        dist_body_x4 = head_x - body_x4
        dist_body_y4 = head_y - body_y4

    # Distance to body parts
    dist_body_x1 = head_x - body_x1
    dist_body_y1 = head_y - body_y1
    dist_body_x2 = head_x - body_x2
    dist_body_y2 = head_y - body_y2

    # Snake weights
    horizontal_weight, vertical_weight = calculate_weights(game)

    # Length
    length = len(game.snake_body)


    # Prepare game data for model prediction
    # One hot encoding previous direction
    prev_direction = game.prev_direction
    if prev_direction == "UP":
        prev_up,prev_down,prev_right = 1,0,0

    elif prev_direction == "DOWN":
        prev_up, prev_down, prev_right = 0,1,0

    elif prev_direction == "RIGHT":
        prev_up,prev_down,prev_right = 0,0,1

    else:
        prev_up,prev_down,prev_right = 0,0,0

    # Distance to tail
    dist_tail_x = head_x - tail_x
    dist_tail_y = head_y - tail_y

    # Prepare the current row data, without the future score
    """game_data = [
        head_x, head_y, food_x, food_y, score,
        dist_left_border, dist_right_border, dist_up_border, dist_down_border,
        dist_body_x1, dist_body_y1,dist_body_x2, dist_body_y2,dist_body_x3, dist_body_y3,
        dist_body_x4, dist_body_y4,tail_x, tail_y,dist_tail_x, dist_tail_y, 
        horizontal_weight, vertical_weight, length, prev_up, prev_down,prev_right
    ]"""

    game_data = [
        head_x, head_y, food_x, food_y, dist_food_x, dist_food_y,
        dist_left_border, dist_right_border, dist_up_border, dist_down_border,
        dist_body_x1, dist_body_y1,dist_body_x2, dist_body_y2, prev_up, prev_down,prev_right
    ]

    # Normalize data
    #game_data = normalize_data(game_data, game.min_vals, game.max_vals)


    # Predict using the trained model
    prediction = weka.predict("./nn_iter2.model", game_data, "./training_computer.arff")

    return prediction

# TODO: IMPLEMENT HERE THE NEW INTELLIGENT METHOD
def move_tutorial_1(game):
    '''
    Hard-coded method to move the snake automatically. It mainly takes into account
    the position of the food, the directions that is being blocked and the weights 
    of the snake in both axis
    ''' 
    game.prev_direction = game.direction 

    # Head position
  
    head_x = game.snake_body[0][0]
    head_y = game.snake_body[0][1]
    
    # Food position
    food_x, food_y = game.food_pos

    # Tail position
    tail_x, tail_y = game.snake_body[-1]

    # Distance to borders
    dist_left_border = head_x
    dist_right_border = FRAME_SIZE_X - head_x
    dist_up_border = head_y
    dist_down_border = FRAME_SIZE_Y - head_y

    # Saving the distance to borders in a list
    dist_border = [dist_left_border, dist_right_border, dist_up_border, dist_down_border] 

    # Snake weights
    hor_weight, ver_weight = calculate_weights(game)


    # Direction
    direction = game.direction
     

    # Closest body points
    body_x,body_y = closest_body_points(head_x, head_y, game.snake_body)
     


    # Calculate the blockings
    blocked = calculate_blocking(head_x, head_y, body_x, body_y, dist_border, tail_x, tail_y)
    


    # Getting the preferred directions to go depending on where the food is
    preferred_directions = []
    if head_x < food_x:
        preferred_directions.append("RIGHT")
    if head_x > food_x:
        preferred_directions.append("LEFT")
    if head_y > food_y:
        preferred_directions.append("UP")
    if head_y < food_y:
        preferred_directions.append("DOWN")
    


    # Getting the number of blocked directions
    blocked_directions = 0
    for direction in ["RIGHT", "LEFT", "UP", "DOWN"]:
        if blocked[direction]:
            blocked_directions += 1

    # When there are only two directions left, choose randomly based on
    # not being blocked and the weight of the snake in each axis
    if blocked_directions == 2 and min(dist_border) > 15: 
        possible_directions = []

        if not blocked["RIGHT"] and hor_weight <= 0:
            possible_directions.append("RIGHT")
        if not blocked["LEFT"] and hor_weight >= 0:
            possible_directions.append("LEFT")
        if not blocked["UP"] and ver_weight <= 0:
            possible_directions.append("UP")
        if not blocked["DOWN"] and ver_weight >= 0:
            possible_directions.append("DOWN")
        if possible_directions:
            return random.choice(possible_directions)

   

    # Choose the preferred direction if it is not being blocked
    for direction in preferred_directions:
        if not blocked[direction]:
            return direction

    # If all preferred directions are blocked, choose any available direction
    for direction in ["RIGHT", "LEFT", "UP", "DOWN"]:
        if not blocked[direction]:
            return direction
        
    return direction


def calculate_blocking(head_x: int, head_y: int, body_x: list, body_y: list, dist_border: list, tail_x: int, tail_y: int) -> dict: 
    """
    Takes inputs from the snake and calculates whether it has been blocked in every direction
    """

    blocked = {"LEFT": False, "RIGHT": False, "UP": False, "DOWN": False}
    

    # Calculating which directions are blocked
    for i in range(len(body_x)): 
               
        if body_x[i] == head_x:
            if abs(body_y[i] - 10 - head_y) <= 5:
                blocked["DOWN"] = True
            if abs(body_y[i] + 10 - head_y) <= 5:
                blocked["UP"] = True

        # Left and right blocking
        if body_y[i] == head_y: 
            if abs(body_x[i] - 10 - head_x) <= 5:
                blocked["RIGHT"] = True
            if abs(body_x[i] + 10 - head_x) <= 5:
                blocked["LEFT"] = True

    # Compares with the tail position if the snakes length is higher than 4
    if len(game.snake_body) > 4:
        # Top and bottom blocking
        if tail_x == head_x:
            if abs(tail_y - 10 - head_y) <= 5:
                blocked["DOWN"] = True
            if abs(tail_y + 10 - head_y) <= 5:
                blocked["UP"] = True
        
        # Left and right blocking
        if tail_y == head_y:
            if abs(tail_x - 10 - head_x) <= 5:
                blocked["RIGHT"] = True
            if abs(tail_x + 10 - head_x) <= 5:
                blocked["LEFT"] = True

    # Blocking with the borders
    if dist_border[0] < 15: 
        blocked["LEFT"] = True
    if dist_border[1] < 15: 
        blocked["RIGHT"] = True
    if dist_border[2] < 15: 
        blocked["UP"] = True
    if dist_border[3] < 15: 
        blocked["DOWN"] = True

    

    return blocked

def calculate_weights(game) -> tuple:
    """
    Calculates in which direction there are more snake body parts in order to avoid going these direction 
    and potential inner loops
    """

    # Initializing the different directions with their values
    horizontal = 0
    vertical = 0

    # Getting the closest body points to the head
    body = game.snake_body[:int(len(game.snake_body))]
    head_x = game.snake_body[0][0]
    head_y = game.snake_body[0][1]

    # Looping thorugh all body parts
    for i in range(len(body)//2):
        # Adding 1 to the horizontal weight if the body part is to the right 
        # of the head and -1 if it is to the left
        if body[i][0] > head_x: 
            horizontal += 1
        elif body[i][0] < head_x:
            horizontal -= 1

        # Adding 1 to the vertical weight if the body part is higher
        # than the head and -1 if it is lower
        if body[i][1] < head_y:
            vertical += 1
        elif body[i][1] > head_y:
            vertical -= 1

    # Bounding the weights between -1 and 1
    horizontal = horizontal / len(body)
    vertical = vertical / len(body)
    
    return horizontal, vertical    


"""# PRINTING DATA FROM GAME STATE
def print_state(game):
    print("--------GAME STATE--------")
    print("FrameSize:", FRAME_SIZE_X, FRAME_SIZE_Y)
    print("Direction:", game.direction)
    print("Snake X:", game.snake_pos[0], ", Snake Y:", game.snake_pos[1])
    print("Snake Body:", game.snake_body)
    print("Food X:", game.food_pos[0], ", Food Y:", game.food_pos[1])
    print("Score:", game.score)"""
    

# TODO: IMPLEMENT HERE THE NEW INTELLIGENT METHOD
def print_line_data(game):
    """
    Saves game state focusing on relevant attributes including score changes.
    The function ensures that each row's future_score is updated in the next tick.
    """
    # Score
    score = game.score

    # Head position
  
    head_x = game.snake_body[0][0]
    head_y = game.snake_body[0][1]
    
    
    # Food position
    food_x, food_y = game.food_pos

    dist_food_x = food_x - head_x
    dist_food_y = food_y - head_y

    # Tail position
    tail_x, tail_y = game.snake_body[-1]

    # Distance to tail
    dist_tail_x = head_x - tail_x
    dist_tail_y = head_y - tail_y


    # Distance to borders
    dist_left_border = head_x
    dist_right_border = FRAME_SIZE_X - head_x
    dist_up_border = head_y
    dist_down_border = FRAME_SIZE_Y - head_y

    # Distance to the closest body parts
    distances = distances_to_head(head_x, head_y, game.snake_body)
    body_x1, body_y1 = distances[0][1], distances[0][2]
    body_x2, body_y2 = distances[1][1], distances[1][2]


    if len(distances) < 4:
        dist_body_x3, dist_body_y3 = 500, 500
        dist_body_x4, dist_body_y4 = 500, 500

    else:
        body_x3, body_y3 = distances[2][1], distances[2][2]
        body_x4, body_y4 = distances[3][1], distances[3][1]

        dist_body_x3 = head_x - body_x3
        dist_body_y3 = head_y - body_y3

        dist_body_x4 = head_x - body_x4
        dist_body_y4 = head_y - body_y4
    

    # Distance to the body points
    dist_body_x1 = head_x - body_x1 
    dist_body_y1 = head_y - body_y1

    dist_body_x2 = head_x - body_x2
    dist_body_y2 = head_y - body_y2

    # Snake weights
    horizontal_weight, vertical_weight = calculate_weights(game)

    # Length of the snake
    length = len(game.snake_body)

    # Direction
    direction = game.direction

    # One hot encoding previous direction
    prev_direction = game.prev_direction
    if prev_direction == "UP":
        prev_up,prev_down,prev_right = 1,0,0

    elif prev_direction == "DOWN":
        prev_up, prev_down, prev_right = 0,1,0

    elif prev_direction == "RIGHT":
        prev_up,prev_down,prev_right = 0,0,1

    else:
        prev_up,prev_down,prev_right = 0,0,0

    # Prepare the current row data, without the future score
    """game_data = [
        head_x, head_y, food_x, food_y, score,
        dist_left_border, dist_right_border, dist_up_border, dist_down_border,
        dist_body_x1, dist_body_y1,dist_body_x2, dist_body_y2,dist_body_x3, dist_body_y3,
        dist_body_x4, dist_body_y4,tail_x, tail_y,dist_tail_x, dist_tail_y, 
        horizontal_weight, vertical_weight, length, prev_up, prev_down,prev_right,
        direction
    ]"""

    game_data = [
        head_x, head_y, food_x, food_y, dist_food_x, dist_food_y,
        dist_left_border, dist_right_border, dist_up_border, dist_down_border,
        dist_body_x1, dist_body_y1,dist_body_x2, dist_body_y2, prev_up, prev_down,prev_right,direction
    ]
                 

    
    if game.previous_data:
        game.previous_data.append(game.score) 
        game.arff_file.write(','.join(map(str, game.previous_data)) + '\n')

    game.previous_data = game_data

    return game_data


def distances_to_head(head_x: int, head_y: int, snake_body: list[int]) -> tuple:
    """
    Computes the distance of each of the body parts of the snake to the head
    """
    # Initializing an empty list
    distances = []

    # Obtaining the distance between the body to each point
    for x,y in snake_body:
        dist = (x-head_x)**2 + (y-head_y)**2 # Calculating squared distance
        # Ensures the distance of the head is not saved as closest point
        if dist != 0:
            distances.append((dist,x,y))


    return distances
    

def closest_body_points(head_x: int, head_y: int, snake_body: list[int]) -> tuple:
    """
    Takes the position of the head of the snake and its body and returns the distance to
    4 closest body points to the head
    """
    # Initializing an empty list
    distances = distances_to_head(head_x, head_y, snake_body)

    # Obtaining the 4 closest distances, if the list is smaller it will only return the existent values
    closest = distances[:4]

    # Returning the x and y coordinates
    closest_x = []
    closest_y = []

    for elem in closest:
        if elem: # Checks the element is not none
            dist, x, y = elem
            closest_x.append(x)
            closest_y.append(y)
        
    # Makes sure the list is of length of 4
    while len(closest_x) < 4:
       closest_x.append(100_000)
       closest_y.append(100_000)   

    return closest_x, closest_y




# Checks for errors encountered
check_errors = pygame.init()
# pygame.init() example output -> (6, 0)
# second number in tuple gives number of errors
if check_errors[1] > 0:
    print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')

# Initialise game window
pygame.display.set_caption('Snake Eater - Machine Learning (UC3M)')
game_window = pygame.display.set_mode((FRAME_SIZE_X, FRAME_SIZE_Y))

# FPS (frames per second) controller
fps_controller = pygame.time.Clock()

# Main logic
game = GameState((FRAME_SIZE_X,FRAME_SIZE_Y))


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # Esc -> Create event to quit the game
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    
    game.prev_direction = game.direction
    game.direction = move_tutorial_1(game)
    #game.direction = move_keyboard(game, event)  
    #game.direction = move_ml(game)  
    print_line_data(game)
    
    
    # Printing the data
    #print_line_data(game)
    

    # Moving the snake
    if game.direction == 'UP':
        game.snake_pos[1] -= 10
    if game.direction == 'DOWN':
        game.snake_pos[1] += 10
    if game.direction == 'LEFT':
        game.snake_pos[0] -= 10
    if game.direction == 'RIGHT':
        game.snake_pos[0] += 10
    
    

    # Snake body growing mechanism
    game.snake_body.insert(0, list(game.snake_pos))
    if game.snake_pos[0] == game.food_pos[0] and game.snake_pos[1] == game.food_pos[1]:
        game.score += 100
        game.food_spawn = False
    else:
        game.snake_body.pop()
        game.score -= 1

    # Spawning food on the screen
    if not game.food_spawn:
        found =  False # Flag for checking if an available food position has been found
        while not found:
            game.food_pos = [random.randrange(1, (FRAME_SIZE_X//10)) * 10, random.randrange(1, (FRAME_SIZE_Y//10)) * 10]
            # Ensures it does not spawn in the body
            if game.food_pos not in game.snake_body:
                game.food_spawn = True
                found = True
            
    # GFX
    game_window.fill(BLUE)
    for pos in game.snake_body:
        # Snake body
        # .draw.rect(play_surface, color, xy-coordinate)
        # xy-coordinate -> .Rect(x, y, size_x, size_y)
        pygame.draw.rect(game_window, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))

    # Snake food
    pygame.draw.rect(game_window, RED, pygame.Rect(game.food_pos[0], game.food_pos[1], 10, 10))

    # Game Over conditions
    # Getting out of bounds
    if game.snake_pos[0] < 0 or game.snake_pos[0] > FRAME_SIZE_X-10:
        game_over(game)
    if game.snake_pos[1] < 0 or game.snake_pos[1] > FRAME_SIZE_Y-10:
        game_over(game)
    # Touching the snake body
    for block in game.snake_body[1:]:
        if game.snake_pos[0] == block[0] and game.snake_pos[1] == block[1]:
            game_over(game)

    show_score(game, 1, WHITE, 'consolas', 15)
    # Refresh game screen
    pygame.display.update()
    # Refresh rate
    fps_controller.tick(DIFFICULTY)
    # PRINTING STATE
    #print_state(game)

header2 = """@RELATION snake_game

    @ATTRIBUTE Head_x NUMERIC
    @ATTRIBUTE Head_y NUMERIC
    @ATTRIBUTE Food_x NUMERIC
    @ATTRIBUTE Food_y NUMERIC
    @ATTRIBUTE Score NUMERIC

    @ATTRIBUTE Dist_left_border NUMERIC
    @ATTRIBUTE Dist_right_border NUMERIC
    @ATTRIBUTE Dist_top_border NUMERIC
    @ATTRIBUTE Dist_bottom_border NUMERIC

    @ATTRIBUTE Dist_body_x1 NUMERIC
    @ATTRIBUTE Dist_body_y1 NUMERIC
    @ATTRIBUTE Dist_body_x2 NUMERIC
    @ATTRIBUTE Dist_body_y2 NUMERIC
    @ATTRIBUTE Dist_body_x3 NUMERIC
    @ATTRIBUTE Dist_body_y3 NUMERIC
    @ATTRIBUTE Dist_body_x4 NUMERIC
    @ATTRIBUTE Dist_body_y4 NUMERIC
   
    
    @ATTRIBUTE Tail_x NUMERIC
    @ATTRIBUTE Tail_y NUMERIC
    @ATTRIBUTE Dist_Tail_x NUMERIC
    @ATTRIBUTE Dist_Tail_y NUMERIC
    @ATTRIBUTE Horizontal_weight NUMERIC
    @ATTRIBUTE Vertical_weight NUMERIC
    @ATTRIBUTE Length NUMERIC
    @ATTRIBUTE Prev_UP NUMERIC
    @ATTRIBUTE Prev_DOWN NUMERIC
    @ATTRIBUTE Prev_RIGHT NUMERIC
 
    @ATTRIBUTE direction {UP, DOWN, LEFT, RIGHT}
    @ATTRIBUTE future_score NUMERIC

    @DATA"""