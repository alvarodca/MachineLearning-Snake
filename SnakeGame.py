"""
Snake Eater
Made with PyGame
Last modification in January 2024 by José Carlos Pulido
Machine Learning Classes - University Carlos III of Madrid
"""

import pygame, sys, time, random, csv, os
from wekaI import Weka

# DIFFICULTY settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
DIFFICULTY = 25

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
        self.change_to = self.direction
        self.score = 0
        self.first_tick = True
        self.prev_length = len(self.snake_body)

# Game Over
def game_over(game):
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

# TODO: IMPLEMENT HERE THE NEW INTELLIGENT METHOD
def move_tutorial_1(game):
    '''
    Hard-coded method to move the snake automatically. It mainly takes into account
    the position of the food, the directions that is being blocked and the weights 
    of the snake in both axis
    '''
    
    # Get the most recent data
    data = print_line_data(game)
    
    

    # Saving the data
    head_x = data[0]
    head_y = data[1]
    food_x = data[2]
    food_y = data[3]
    #body_x = [data[10], data[12], data[14], data[16]]
    #body_y = [data[11], data[13], data[15], data[17]]
    dist_border = [data[5], data[6], data[7], data[8]]
    tail_x = data[17]
    tail_y = data[18]
    hor_weight = data[19]
    ver_weight = data[20]

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
    for i in range(len(body)):
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


# PRINTING DATA FROM GAME STATE
def print_state(game):
    print("--------GAME STATE--------")
    print("FrameSize:", FRAME_SIZE_X, FRAME_SIZE_Y)
    print("Direction:", game.direction)
    print("Snake X:", game.snake_pos[0], ", Snake Y:", game.snake_pos[1])
    print("Snake Body:", game.snake_body)
    print("Food X:", game.food_pos[0], ", Food Y:", game.food_pos[1])
    print("Score:", game.score)
    

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

    # Tail position
    tail_x, tail_y = game.snake_body[-1]

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

    # Defining ARFF header
    arff_file = "training2_keyboard.arff"
    header = """@RELATION snake_game

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
    @ATTRIBUTE Horizontal_weight NUMERIC
    @ATTRIBUTE Vertical_weight NUMERIC
    @ATTRIBUTE Length NUMERIC
    @ATTRIBUTE future_score NUMERIC

    @ATTRIBUTE direction {UP, DOWN, LEFT, RIGHT}

    @DATA"""

    # If the ARFF file does not exist, create it with the header
    if not os.path.exists(arff_file):
        with open(arff_file, "w") as f:
            f.write(header.strip() + "\n\n")

    # Prepare the current row data, without the future score
    game_data = [
        head_x, head_y, food_x, food_y, score,
        dist_left_border, dist_right_border, dist_up_border, dist_down_border,
        dist_body_x1, dist_body_y1,dist_body_x2, dist_body_y2,dist_body_x3, dist_body_y3,
        dist_body_x4, dist_body_y4,tail_x, tail_y, horizontal_weight, vertical_weight, length, 0,  
        direction
    ]
                 

    # If there is a row that has not been written yet, updates it
    if hasattr(game, "pending_row"):
        game.pending_row[-2] = score  # Update previous tick's future_score with the current score
        with open(arff_file, "a") as f:
            f.write(",".join(map(str, game.pending_row)) + "\n")

    # Save the current row as pending for the next tick
    game.pending_row = game_data

    # Return the current row as a CSV string for debugging/logging purposes
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

weka = Weka()
weka.start_jvm()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # Esc -> Create event to quit the game
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
    #game.direction = move_tutorial_1(game)
    game.direction = move_keyboard(game, event)    
    
    
    #game.direction = move_tutorial_1(game)
    # Printing the data
    print_line_data(game)
    

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
    print_state(game)
