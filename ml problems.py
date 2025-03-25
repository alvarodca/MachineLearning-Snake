"""
Snake Eater Game with Machine Learning Integration

Arguments:
    --keyboard: Enable keyboard control for the snake.
    --ml: Enable machine learning control for the snake(also allows keyboard control).
    --auto: Enable automatic movement control for the snake.
    --save: Enable saving game state data to CSV and ARFF files.
    --difficulty: Set game difficulty from 1 (Easy) to 5 (Impossible).
Snake Eater
Made with PyGame
Machine Learning Classes - University Carlos III of Madrid
"""
import pygame, sys, time, random, csv, os
from datetime import datetime
from math import sqrt
from wekaI import Weka
import argparse
import pandas as pd
from scipy.io import arff


# DIFFICULTY settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
DIFFICULTY = 20
# Set difficulty based on argument
# Default difficulty is 10 (Easy)
DIFFICULTY_MAP = {1: 10, 2: 15, 3: 40, 4: 100, 5: 10000}

# Window size
FRAME_SIZE_X = 480
FRAME_SIZE_Y = 480

weka = Weka()
weka.start_jvm()
# Checks for errors encountered
check_errors = pygame.init()
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
        self.snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]] # After eating the length increases by 1
        self.food_pos = [random.randrange(1, (FRAME_SIZE[0]//10)) * 10, random.randrange(1, (FRAME_SIZE[1]//10)) * 10]
        self.food_spawn = True
        self.direction = 'RIGHT'
        self.change_to = self.direction
        self.score = 0
        self.previous_direction = self.direction
        self.next_score = 0
        self.previous_arff_data = None

        self.min_vals, self.max_vals = load_min_max("training_fixed.arff")

        # CSV initialization
        self.csv_filename = 'snake_game_data.csv'
        self.tick_count = 0
        
        # Initialize CSV with headers if file doesn't exist
        if not os.path.exists(self.csv_filename):
            with open(self.csv_filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'game_id', 'tick', 
                    'snake_x', 'snake_y', 
                    'food_x', 'food_y',
                    'direction', 
                    'distance_x', 'distance_y', 'euclidean_distance',
                    'wall_distance_up', 'wall_distance_down', 
                    'wall_distance_left', 'wall_distance_right',
                    'body_distance_up', 'body_distance_down',
                    'body_distance_left', 'body_distance_right',
                    'score', 'length'
                ])
        
        
        # ARFF initialization
        # ARFF initialization
        self.arff_filename = 'snake_game_data.arff'

        # Initialize ARFF with headers if file doesn't exist
        if not os.path.exists(self.arff_filename):
            with open(self.arff_filename, 'w') as file:
                file.write('@RELATION snake_game\n\n')
                file.write('@ATTRIBUTE Head_x NUMERIC\n')
                file.write('@ATTRIBUTE Head_y NUMERIC\n')
                file.write('@ATTRIBUTE Food_x NUMERIC\n')
                file.write('@ATTRIBUTE Food_y NUMERIC\n')
                file.write('@ATTRIBUTE Score NUMERIC\n')
                file.write('@ATTRIBUTE Dist_right_border NUMERIC\n')
                file.write('@ATTRIBUTE Dist_bottom_border NUMERIC\n')
                file.write('@ATTRIBUTE Dist_body_x1 NUMERIC\n')
                file.write('@ATTRIBUTE Dist_body_y1 NUMERIC\n')
                file.write('@ATTRIBUTE Dist_body_x2 NUMERIC\n')
                file.write('@ATTRIBUTE Dist_body_y2 NUMERIC\n')
                file.write('@ATTRIBUTE Dist_body_x3 NUMERIC\n')
                file.write('@ATTRIBUTE Dist_body_y3 NUMERIC\n')
                file.write('@ATTRIBUTE Dist_body_x4 NUMERIC\n')
                file.write('@ATTRIBUTE Dist_body_y4 NUMERIC\n')
                file.write('@ATTRIBUTE Tail_x NUMERIC\n')
                file.write('@ATTRIBUTE Tail_y NUMERIC\n')
                file.write('@ATTRIBUTE Horizontal_weight NUMERIC\n')
                file.write('@ATTRIBUTE Vertical_weight NUMERIC\n')
                file.write('@ATTRIBUTE Length NUMERIC\n')
                file.write('@ATTRIBUTE Dist_tail_x NUMERIC\n')
                file.write('@ATTRIBUTE Dist_tail_y NUMERIC\n')
                file.write('@ATTRIBUTE direction {UP,DOWN,LEFT,RIGHT}\n')
                file.write('@DATA\n')
            
        # Generate unique game ID for this session
        self.game_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Open the CSV file
        self.csv_file = open(self.csv_filename, 'a', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        
        # Open the ARFF file
        self.arff_file = open(self.arff_filename, 'a')
        
        def __del__(self):
            # Ensure the CSV file is closed when the game state is destroyed
            if hasattr(self, 'csv_file'):
                self.csv_file.close()
            # Ensure the ARFF file is closed when the game state is destroyed
            if hasattr(self, 'arff_file'):
                self.arff_file.close()

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

def game_over(game):
    """
    Ensures the last stored tick is written with a placeholder future score (-1).
    """
    if game.previous_arff_data:
        game.previous_arff_data.append(-1)  # No future tick, assign -1
        game.arff_file.write(','.join(map(str, game.previous_arff_data)) + '\n')

    game.csv_file.close()
    game.arff_file.close()
    
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

def move_tutorial_1(game):
    """
    Simple movement algorithm that:
    1. Uses snake body as snake_body_past based on current length
    2. Moves toward food while avoiding these positions
    """
    # From the snake body list in the init
    snake_body_past = game.snake_body[1:]  # All positions except head
    
    # Calculate possible next positions and store in a dictionary
    next_frame_positions = {
        'UP': [game.snake_pos[0], game.snake_pos[1] - 10],
        'DOWN': [game.snake_pos[0], game.snake_pos[1] + 10],
        'LEFT': [game.snake_pos[0] - 10, game.snake_pos[1]],
        'RIGHT': [game.snake_pos[0] + 10, game.snake_pos[1]]
    }
    
    # Remove directions that would make the snake run into itself
    safe_directions = []
    for direction, next_pos in next_frame_positions.items():
        # Check if next position is in snake_body_past
        if next_pos not in snake_body_past:
            # Also check frame boundaries
            if (0 <= next_pos[0] < FRAME_SIZE_X and 
                0 <= next_pos[1] < FRAME_SIZE_Y):
                safe_directions.append(direction)
    
    if not safe_directions:
        return game.direction  # No safe moves, continue current direction
        
    # Among safe directions, choose the one closest to food
    best_direction = game.direction
    min_distance = float('inf')
    
    for direction in safe_directions:
        next_pos = next_frame_positions[direction]
        distance = abs(next_pos[0] - game.food_pos[0]) + abs(next_pos[1] - game.food_pos[1])
        
        if distance < min_distance:
            min_distance = distance
            best_direction = direction
            
    return best_direction

def move_with_ml(game):
    # Gather relevant game state data
    head_x, head_y = game.snake_body[0]
    food_x, food_y = game.food_pos
    tail_x, tail_y = game.snake_body[-1]
    
    # Distance to borders
    dist_right_border = FRAME_SIZE_X - head_x
    dist_bottom_border = FRAME_SIZE_Y - head_y

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

    # Prepare game data for model prediction
    game_data = [
        head_x, head_y, food_x, food_y,
        dist_right_border, dist_bottom_border,
        dist_body_x1, dist_body_y1, dist_body_x2, dist_body_y2,
        dist_body_x3, dist_body_y3, dist_body_x4, dist_body_y4,
        tail_x, tail_y, horizontal_weight, vertical_weight,
        len(game.snake_body),  # Length of the snake
        head_x - tail_x,  # Dist_tail_x
        head_y - tail_y # Direction
    ]

    # Normalize data (if applicable)
    #game_data = normalize_data(game_data, game.min_vals, game.max_vals)

    # Predict using the trained model
    prediction = weka.predict("./svm_iter2.model", game_data, "./training_second_iter_processed.arff")

    return prediction

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



def distances_to_head(head_x: int, head_y: int, snake_body: list[int]) -> tuple:
    """
    Computes the distance of each of the body parts of the snake to the head
    """
    # Initializing an empty list
    distances = []

    # Obtaining the distance between the body to each point
    for x,y in snake_body[:4]: # Computes it for the first 4 points
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
    #closest = distances[:4]

    # Returning the x and y coordinates
    closest_x = []
    closest_y = []

    for elem in distances:
        if elem: # Checks the element is not none
            dist, x, y = elem
            closest_x.append(x)
            closest_y.append(y)
        
    # Makes sure the list is of length of 4
    while len(closest_x) < 4:
       closest_x.append(100_000)
       closest_y.append(100_000)   

    return closest_x, closest_y

def handle_keyboard_events(game):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # Esc -> Create event to quit the game
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            # R -> Restart the game
            if event.key == pygame.K_r:
                restart_game()
            game.previous_direction = game.direction
            # W -> Up; S -> Down; A -> Left; D -> Right
            if (event.key == pygame.K_UP or event.key == ord('w')) and game.direction != 'DOWN':
                game.direction = 'UP'
            if (event.key == pygame.K_DOWN or event.key == ord('s')) and game.direction != 'UP':
                game.direction = 'DOWN'
            if (event.key == pygame.K_LEFT or event.key == ord('a')) and game.direction != 'RIGHT':
                game.direction = 'LEFT'
            if (event.key == pygame.K_RIGHT or event.key == ord('d')) and game.direction != 'LEFT':
                game.direction = 'RIGHT'
    return game.direction

def restart_game():
    global game
    game = GameState((FRAME_SIZE_X, FRAME_SIZE_Y))
    print(f'[+] Data will be appended to: {game.csv_filename} with game ID: {game.game_id}')

def get_distances_to_body(game):
    """Calculate distances from head to nearest body part in each direction"""
    head_x, head_y = game.snake_pos
    distances = {
        'up': float('inf'),
        'down': float('inf'),
        'left': float('inf'),
        'right': float('inf')
    }
    
    # Check each body segment (excluding head)
    # Each segment is going to be a point in the list of snake_body
    for segment in game.snake_body[1:]:
        seg_x, seg_y = segment
        
        # Same column (vertical alignment)
        if seg_x == head_x:
            if seg_y < head_y:  # Segment is above
                distances['up'] = min(distances['up'], head_y - seg_y - 10) # - 10 for better understanding of when the snake is right next to it's body
            else:  # Segment is below
                distances['down'] = min(distances['down'], seg_y - head_y - 10)
        
        # Same row (horizontal alignment)
        if seg_y == head_y:
            if seg_x < head_x:  # Segment is to the left
                distances['left'] = min(distances['left'], head_x - seg_x)
            else:  # Segment is to the right
                distances['right'] = min(distances['right'], seg_x - head_x)
    
    # Convert inf to -1 for inf
    return {k: v if v != float('inf') else -1 for k, v in distances.items()}

def get_distances_to_walls(game):
    """Calculate distances from head to walls"""
    head_x, head_y = game.snake_pos
    return {
        'up': head_y,
        'down': FRAME_SIZE_Y - head_y,
        'left': head_x,
        'right': FRAME_SIZE_X - head_x
    }


def save_line_data(game):
    """
    Returns a single line of game state data and appends to CSV and ARFF
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
    dist_top_border = head_y
    dist_bottom_border = FRAME_SIZE_Y - head_y

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
    direction = game.direction1
      
    # Prepare ARFF data row
    # Removed up y left border, length y future score
    arff_data = [
        head_x, head_y, food_x, food_y, score,
        dist_right_border, dist_bottom_border,
        dist_body_x1, dist_body_y1,dist_body_x2, dist_body_y2,
        tail_x, tail_y, horizontal_weight, vertical_weight,game.direction]
    
    # If we have a previous tick, finalize its data with this tick's score as future_score
    #if game.previous_arff_data:
    #    game.previous_arff_data.append(game.score)  # Assign the future score
    #    game.arff_file.write(','.join(map(str, game.previous_arff_data)) + '\n')

    # Store current data for the next tick
    game.previous_arff_data = arff_data

def show_fps(clock, game_window):
    fps = str(int(clock.get_fps()))
    fps_string = f'FPS: {fps}'
    fps_font = pygame.font.SysFont('consolas', 20)
    fps_surface = fps_font.render(fps_string, True, WHITE)
    fps_rect = fps_surface.get_rect()
    fps_rect.topright = (FRAME_SIZE_X - 10, 10)
    game_window.blit(fps_surface, fps_rect)

def main():
    # Argument parser for enabling different movement methods
    parser = argparse.ArgumentParser(description='Snake Game with different movement methods.')
    parser.add_argument('--keyboard', action='store_true', help='Enable keyboard control')
    parser.add_argument('--ml', action='store_true', help='Enable machine learning control')
    parser.add_argument('--auto', action='store_true', help='Enable automatic movement control(hardcoded rules)')
    parser.add_argument('--save', action='store_true', help='Enable saving game state data to CSV and ARFF files.')
    parser.add_argument('--difficulty', type=int, choices=[1, 2, 3, 4, 5], default=1, help='Set game difficulty from 1 (Easy) to 5 (Impossible)')
    args = parser.parse_args()

    global DIFFICULTY
    global DIFFICULTY_MAP
    DIFFICULTY = 15

    while True:
        game.previous_direction = game.direction
                
        game.direction = move_with_ml(game)

        
        #save_line_data(game)
        
        #if args.ml:
        #    game.direction = move_with_ml(game)
        #    game.direction = handle_keyboard_events(game)
        #elif args.auto:
        #    game.direction = move_tutorial_1(game)
        #    game.direction = handle_keyboard_events(game)
        #elif args.keyboard:
        #    game.direction = handle_keyboard_events(game)
        #else:
        #    print("No movement method specified. Use --keyboard, --ml, or --auto.")
        #    pygame.quit()
        #    sys.exit()
        #if args.save:
        #    save_line_data(game)


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
            game.food_pos = [random.randrange(1, (FRAME_SIZE_X//10)) * 10, random.randrange(1, (FRAME_SIZE_Y//10)) * 10]
        game.food_spawn = True

        # GFX
        game_window.fill(BLUE)
        for pos in game.snake_body:
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
        show_fps(fps_controller, game_window)
        pygame.display.update()
        fps_controller.tick(DIFFICULTY)

# Checks for errors encountered
check_errors = pygame.init()
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


if __name__ == "__main__":
    main()
    weka.stop_jvm()