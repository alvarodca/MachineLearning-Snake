"""
Snake Eater
Made with PyGame
Last modification in January 2024 by José Carlos Pulido
Machine Learning Classes - University Carlos III of Madrid
"""

import pygame, sys, time, random, csv
import pandas as pd


# DIFFICULTY settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
DIFFICULTY = 80

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
    YOUR CODE HERE
    '''
    data = print_line_data(game)

    head_x = data[1]
    head_y = data[2]
    food_x = data[3]
    food_y = data[4]
    score = data[5]
    body_x = [data[10], data[12], data[14], data[16]]
    body_y = [data[11], data[13], data[15], data[17]]
    dist_border = [data[6], data[7], data[8], data[9]]
    tail_x = data[18]
    tail_y = data[19]
    hor_weight = data[20]
    ver_weight = data[21]

    # Calculate the blockings
    blocked = calculate_blocking(head_x, head_y, body_x, body_y, dist_border, tail_x, tail_y)
    
    preferred_directions = []
    if head_x < food_x:
        preferred_directions.append("RIGHT")
    if head_x > food_x:
        preferred_directions.append("LEFT")
    if head_y > food_y:
        preferred_directions.append("UP")
    if head_y < food_y:
        preferred_directions.append("DOWN")

    blocked_directions = 0
    for direction in ["RIGHT", "LEFT", "UP", "DOWN"]:
        if blocked[direction]:
            blocked_directions += 1

    if blocked_directions == 2: 
        possible_directions = []

        """if not blocked["RIGHT"] and score < 0 and hor_weight >= 0:
            return "RIGHT"
        if not blocked["LEFT"] and score < 0 and hor_weight < 0:
            return "LEFT"
        if not blocked["UP"] and score < 0 and ver_weight >= 0:
            return "UP"
        if not blocked["DOWN"] and score < 0 and ver_weight < 0:
            return "DOWN"""

        if not blocked["RIGHT"] and hor_weight <= 0:
            possible_directions.append("RIGHT")
        if not blocked["LEFT"] and hor_weight > 0:
            possible_directions.append("LEFT")
        if not blocked["UP"] and ver_weight <= 0:
            possible_directions.append("UP")
        if not blocked["DOWN"] and ver_weight > 0:
            possible_directions.append("DOWN")
        if possible_directions:
            return random.choice(possible_directions)

    # Check preferred directions first
    for direction in preferred_directions:
        if not blocked[direction]:
            return direction

    # If all preferred directions are blocked, choose any available direction
    for direction in ["RIGHT", "LEFT", "UP", "DOWN"]:
        if not blocked[direction]:
            return direction


def calculate_blocking(head_x: int, head_y: int, body_x: list, body_y: list, dist_border: list, tail_x: int, tail_y: int) -> dict: 
    """
    Takes inputs from the snake and calculates whether it has been blocked in every direction
    """

    blocked = {"LEFT": False, "RIGHT": False, "UP": False, "DOWN": False}

    # Calculating which directions are blocked
    for i in range(len(body_x)): 
        # Top and bottom blocking
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
        if tail_x == head_x:
            if abs(tail_y - 10 - head_y) <= 5:
                blocked["DOWN"] = True
            if abs(tail_y + 10 - head_y) <= 5:
                blocked["UP"] = True
        
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

def calculate_weights(game):
    """Function which calculates to which direction there are more snake body parts in order to avoid going these direction 
    and potential inner loops"""

    # Initializing the different directions with their values
    horizontal = 0
    vertical = 0

    body = game.snake_body[:int(len(game.snake_body)/1.2)]
    head_x = game.snake_pos[0]
    head_y = game.snake_pos[1]

    for i in range(len(body)):
        if body[i][0] > head_x: 
            horizontal += 1
        elif body[i][0] < head_x:
            horizontal -= 1

        if body[i][1] > head_y:
            vertical += 1
        elif body[i][1] < head_y:
            vertical -= 1

    horizontal = horizontal / len(body)
    vertical = vertical / len(body) 
    
    return horizontal, vertical

    """# Obtaining the necessary variables for obtaining the blocked dictionary
    head_x = data[1]
    head_y = data[2]
    body_x = [data[10], data[12], data[14], data[16]]
    body_y = [data[11], data[13], data[15], data[17]]
    dist_border = [data[6], data[7], data[8], data[9]]
    tail_x = data[18]
    tail_y = data[19]

    # Calculate the blockings
    blocked = calculate_blocking(head_x, head_y, body_x, body_y, dist_border, tail_x, tail_y)

    if list(blocked.values()).count(False) == 3:
        return blocked
    
    for x,y in game.snake_body:
        # For the head of the snake
        if x != head_x or y != head_y:
            if x < head_x and y < head_y:
                down_left += 1
            elif x <= head_x and y >= head_y:
                up_left += 1
            elif x > head_x and y >= head_y:
                up_right += 1
            else:
                down_right += 1

    weights = [up_left, up_right, down_left, down_right]

    max_index = weights.index(max(weights))

    # Only block the most dangerous direction if at most 2 are blocked
    if sum(blocked.values()) < 2:

        if max_index == 0:
            blocked["UP"] = True
            blocked["LEFT"] = True
        elif max_index == 1:
            blocked["UP"] = True
            blocked["RIGHT"] = True
        elif max_index == 2:
            blocked["DOWN"] = True
            blocked["LEFT"] = True
        else:
            blocked["DOWN"] = True
            blocked["RIGHT"] = True"""
    

# PRINTING DATA FROM GAME STATE
def print_state(game):
    print("--------GAME STATE--------")
    """print("FrameSize:", FRAME_SIZE_X, FRAME_SIZE_Y)
    print("Direction:", game.direction)
    print("Snake X:", game.snake_pos[0], ", Snake Y:", game.snake_pos[1])
    print("Snake Body:", game.snake_body)
    print("Food X:", game.food_pos[0], ", Food Y:", game.food_pos[1])
    print("Score:", game.score)"""
    data = print_line_data(game)

    head_x = data[1]
    head_y = data[2]
    food_x = data[3]
    food_y = data[4]
    body_x = [data[10], data[12], data[14], data[16]]
    body_y = [data[11], data[13], data[15], data[17]]
    dist_border = [data[6], data[7], data[8], data[9]]
    tail_x = data[18]
    tail_y = data[19]
    hor_weight = data[20]
    ver_weight = data[21]

    # Calculate the blockings
    blocked = calculate_blocking(head_x, head_y, body_x, body_y, dist_border, tail_x, tail_y)
    print(blocked)
    print(f"H_w: {hor_weight}; V_w: {ver_weight}")

# TODO: IMPLEMENT HERE THE NEW INTELLIGENT METHOD
def print_line_data(game):
    '''
    This function returns a string containg the most relevant attributes
    '''
    direction = game.direction
    head_x = game.snake_pos[0]
    head_y = game.snake_pos[1]
    food_x = game.food_pos[0]
    food_y = game.food_pos[1]
    score = game.score

    # Tail position
    tail = game.snake_body[-1]
    tail_x = tail[0]
    tail_y = tail[1]

    dist_left_border = head_x
    dist_right_border = FRAME_SIZE_X - head_x
    dist_up_border = head_y
    dist_down_border = FRAME_SIZE_Y - head_y

    dist_body_x, dist_body_y = closest_body_points(head_x, head_y, game.snake_body)
    horizontal_weight, vertical_weight = calculate_weights(game)

    return (direction, head_x, head_y, food_x, food_y, score, 
            dist_left_border, dist_right_border, dist_up_border, dist_down_border,
            dist_body_x[0], dist_body_y[0], dist_body_x[1], dist_body_y[1], 
            dist_body_x[2], dist_body_y[2], dist_body_x[3], dist_body_y[3], 
            tail_x, tail_y, horizontal_weight, vertical_weight)

# For the tail add tail_x = game.snake_pos[-1] and ta

def closest_body_points(head_x, head_y, snake_body) -> tuple:
    """Takes the position of the head of the snake and its body and returns the 
    4 closest body points to the head"""
    # Initializing an empty list
    distances = []

    # Obtaining the distance between the body to each point
    for x,y in snake_body:
        dist = (x-head_x)**2 + (y-head_y)**2 # Calculating squared distance
        # Ensures the distance of the header is not saved as closest point
        if dist != 0:
            distances.append((dist,x,y))

    # Sorting the distances in ascending order
    distances.sort()

    # Obtaining the 4 smallest distances, if the list is smaller it will only return the existent values
    closest = distances[:4]

    # Returning the x and y coordinates
    closest_x = []
    closest_y = []

    for elem in closest:
        if elem: # Checks the element is not none
            dist, x, y = elem
            closest_x.append(int(x))
            closest_y.append(int(y))
        
    # Makes sure the list is of length of 4
    while len(closest_x) < 4:
       closest_x.append(None)
       closest_y.append(None)   

    return closest_x, closest_y

# Checks for errors encounteRED
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
        # CALLING MOVE METHOD
        game.direction = move_keyboard(game, event)

    # PUTTING IT ON TOP OF THE MOVEMENT TO USE REAL TIME DATA IN THE MOVE IMPLEMENTATION
    # Storing the information on the data csv, the a indicates append so data is not overwritten   
    with open('data.csv', 'a', newline= '') as csvfile:
        # Writing the corresponding information to each of the rows
        writer = csv.writer(csvfile)
        writer.writerow(list(print_line_data(game)))
        # Closing the file
        csvfile.close()

    # UNCOMMENT WHEN METHOD IS IMPLEMENTED
    game.direction = move_tutorial_1(game)


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