#import the most important packages - pygame, math, random, and matplotlib
import pygame
import math
import random
import matplotlib.pyplot as plt

#starting coordinates - a is an 'x', and b is 'y'.
a=500
b=500

# game initiation
pygame.init()

# screen for the game
screen = pygame.display.set_mode((1300, 700))

# background image
background = pygame.image.load('map.jpg')

# name in the left top corner
pygame.display.set_caption("Flight Sim 1")

#clock in order to make the game in 60FPS, so the computer does not explode
clock = pygame.time.Clock()

# Player - Aeroplane icon
playerImg = pygame.image.load('plane.png')
player_position = pygame.Vector2(a, b) #starting position of the player
player_position_change = pygame.Vector2(0, 0) #change of the vector above
player_speed = 1  # initial speed of the player
player_speed_change = 0  # change of the speed
heading_degree = 0  # initial degree (go up)

#height controls
player_height = 0
player_vertical_speed = 0
height_autopilot1 = 0


flight_path = [] #flight path - it is a list of points that later will be placed on the map

#display HUD - creating font sizes to display in top right
pygame.font.init()
font = pygame.font.SysFont('None', 20)
font2 = pygame.font.SysFont('None', 80)

#Autopliot1
autopilot_mode1 = False
target_heading = 0

#autopilot2
autopilot_mode2 = False
target_heading2 = 0

#autopilot3
autopilot_mode3 = False
speed_min = 1.0
speed_max = 4.0

#autopilot4
autopilot_mode4 = False
score = 0.0
autopilot4_key_left = False
autopilot4_key_right = False
autopilot4_ctrl = False


#creation of points - all points are in the lists
points_number = 4
pointImg = []
pointX=[]
pointY=[]
pointZ=[]

#score - the number of collected points
score_value=0

#list in order to put it in the graph at the end
score_over_time = []

#for every point select its coordinates randomly and make it appear as an image
for i in range(points_number):
    pointImg.append(pygame.image.load('point.png'))
    pointX.append(random.randint(0, 1268))
    pointY.append(random.randint(0, 668))
    pointZ.append(random.randint(500,3000)) #make height in range between 500 and 3000

#time ticks - 1000 ticks is 1 second
start_ticks = pygame.time.get_ticks()

#autopilot1
def autopilot1_on(event1):
    # function to turn on the autopilot mode 1
    global autopilot_mode1, autopilot_mode2, autopilot_mode3, autopilot_mode4
    if event1.type == pygame.KEYDOWN:
        if event1.key == pygame.K_p:
            autopilot_mode1 = not autopilot_mode1
            autopilot_mode2 = False
            autopilot_mode3 = False
            autopilot_mode4 = False
    return autopilot_mode1

def autopilot1_heading(event1):
    global target_heading

    # player controls the heading in autopilot 1 by clicking J and L. It must be in range 0-360.

    if event1.type == pygame.KEYDOWN:
        if event1.key == pygame.K_j:
            target_heading -= 5
        elif event1.key == pygame.K_l:
            target_heading += 5

    target_heading %= 360

    return target_heading

def autopilot1_height(event1):

    #setting the autopilot1 height value by different keys
    global height_autopilot1
    if event1.type == pygame.KEYDOWN:
        if event1.key == pygame.K_k:
            height_autopilot1 += 50
        elif event1.key == pygame.K_m:
            height_autopilot1 -= 50
    if height_autopilot1 <= 0:
        height_autopilot1 = 0

    return height_autopilot1

def autopilot1_height_update():
    global player_height, player_vertical_speed, height_autopilot1

    # height control of autopilot
    if player_height != height_autopilot1:
        height_diff = height_autopilot1 - player_height
        if height_diff > 1000:
            player_vertical_speed = 5
        elif height_diff > 0:
            player_vertical_speed = height_diff*0.005
            if height_diff < 10:
                player_height = height_autopilot1

        elif height_diff > -1000:
            player_vertical_speed = height_diff*0.005
            if height_diff > -10:
                player_height = height_autopilot1
        elif height_diff <-1000:
            player_vertical_speed = -5

def autopilot1_update():
    global heading_degree
    # this function calculates the error that is between -180 and 180 degrees abd then decides where to turn.
    error = (target_heading - heading_degree + 540) % 360 - 180

    if abs(error) > 0.5:
        heading_degree += error / 30 #it changes the heading by the error / 30, which gives an impression that it turns sharply first, and then smoother and smoother.

    else:
        heading_degree = target_heading

    return heading_degree

#autopilot2
def autopilot2_on(event2):
    global autopilot_mode2, autopilot_mode1, autopilot_mode3, autopilot_mode4
    # function to turn on the autopilot mode 2
    if event2.type == pygame.KEYDOWN:
        if event2.key == pygame.K_o:
            autopilot_mode2 = not autopilot_mode2
            autopilot_mode1 = False
            autopilot_mode3 = False
            autopilot_mode4 = False
    return autopilot_mode2

def autopilot2_update():
    closest_index = None
    min_distance = 10000
    global target_heading2
    global player_speed_change, player_position, heading_degree, player_position_change, player_height, player_vertical_speed

    # the function updates where to fly. For every number it checks the distance. If it is the shortest distance now, it chooses this point. At the end it just gives the index of the best point found.

    for j in range(points_number):
        point_position_vec = pygame.Vector2(pointX[j], pointY[j])
        distance_to = player_position.distance_to(point_position_vec)
        if distance_to < min_distance:
            min_distance = distance_to
            closest_index = j
    if closest_index is not None:

        # it takes this index and calculate the target heading that the plane should take.

        target_vector = pygame.Vector2(pointX[closest_index]-player_position.x+12, 12+pointY[closest_index]-player_position.y)
        height_difference = pointZ[closest_index] - player_height

        # height control of autopilot
        if height_difference > 200:
            player_vertical_speed = 10
        elif height_difference <-200:
            player_vertical_speed = -10
        elif height_difference > 5:
            player_vertical_speed -= 0.1
        elif height_difference < 5:
            player_vertical_speed += 0.1
        else:
            player_vertical_speed = 0

        if target_vector.length() != 0:
            target_vector_unit = target_vector.normalize()

            target_heading2 = math.degrees(math.atan2(target_vector_unit.x, -target_vector_unit.y)) % 360

def autopilot2_turn_update():
    global heading_degree, target_heading2
    error1 = (target_heading2 - heading_degree + 540) % 360 - 180  # this function calculates the error that is between -180 and 180 degrees abd then decides where to turn.

    if abs(error1) > 0.25:
        heading_degree += error1 / 30 #it changes the heading by the error / 30, which gives an impression that it turns sharply first, and then smoother and smoother.

    else:
        heading_degree = target_heading2

    return heading_degree

#autopilot3
def autopilot3_on(event3):
    global autopilot_mode2, autopilot_mode1, autopilot_mode3, autopilot_mode4
    # function to turn on the autopilot mode 3
    if event3.type == pygame.KEYDOWN:
        if event3.key == pygame.K_i:
            autopilot_mode3 = not autopilot_mode3
            autopilot_mode1 = False
            autopilot_mode2 = False
            autopilot_mode4 = False
    return autopilot_mode3

def autopilot3_speed_control(distance_to):
    global target_heading2, heading_degree, player_speed, speed_max, speed_min

    # the function controls the speed in autopilot 3
    # calculate the error in angles and give me the speed factor - an easy way to control the speed.

    error = abs((target_heading2 - heading_degree + 540) % 360 - 180)
    speed_factor = max(0.3, 1 - error/180)
    player_speed = speed_factor * speed_max
    # if you are close to one of the make your speed lower. speed_min is set to such a point that it will catch the point while turning around it.

    if distance_to < 80:
        desired_speed = max(speed_min, player_speed - 0.05)
    else:
        desired_speed = min(player_speed + 0.02, speed_max)

    player_speed += (desired_speed - player_speed) * 0.1

def autopilot3_update():
    closest_index = None
    min_distance = 10000
    distance_to = None
    global target_heading2
    global player_speed_change, player_position, heading_degree, player_position_change, player_height, player_vertical_speed

    # the function updates where to fly. For every number it checks the distance. If it is the shortest distance now, it chooses this point. At the end it just gives the index of the best point found.

    for j in range(points_number):
        point_position_vec = pygame.Vector2(pointX[j], pointY[j])
        distance_to = player_position.distance_to(point_position_vec)
        if distance_to < min_distance:
            min_distance = distance_to
            closest_index = j
    if closest_index is not None:

        # it takes this index and calculate the target heading that the plane should take.

        target_vector = pygame.Vector2(pointX[closest_index] - player_position.x + 12,
                                           12 + pointY[closest_index] - player_position.y)
        height_difference = pointZ[closest_index] - player_height

        # height control of autopilot
        if height_difference > 200:
            player_vertical_speed = 10
        elif height_difference < -200:
            player_vertical_speed = -10
        elif height_difference > 5:
            player_vertical_speed -= 0.1
        elif height_difference < 5:
            player_vertical_speed += 0.1
        else:
            player_vertical_speed = 0
        if target_vector.length() != 0:
            target_vector_unit = target_vector.normalize()
            target_heading2 = math.degrees(math.atan2(target_vector_unit.x, -target_vector_unit.y)) % 360
    return distance_to

def autopilot3_turn_update():
    global heading_degree, target_heading2
    error1 = (target_heading2 - heading_degree + 540) % 360 - 180  # this function calculates the error that is between -180 and 180 degrees abd then decides where to turn.
    if abs(error1) > 0.25:
        heading_degree += error1 / 30 #it changes the heading by the error / 30, which gives an impression that it turns sharply first, and then smoother and smoother.
    else:
        heading_degree = target_heading2

    return heading_degree

#autopilot 4
def autopilot4_on(event4):
    global autopilot_mode2, autopilot_mode1, autopilot_mode3, autopilot_mode4
    # function to turn on the autopilot mode 4
    if event4.type == pygame.KEYDOWN:
        if event4.key == pygame.K_u:
            autopilot_mode4 = not autopilot_mode4
            autopilot_mode1 = False
            autopilot_mode2 = False
            autopilot_mode3 = False

    return autopilot_mode4

def autopilot4_speed_control(distance_to):
    #the function controls the speed in autopilot 4
    global target_heading2, heading_degree, player_speed, speed_max, speed_min

    #calculate the error in angles and give me the speed factor - an easy way to control the speed.

    error = abs((target_heading2 - heading_degree + 540) % 360 - 180)
    speed_factor = max(0.3, 1 - error / 180)
    player_speed = speed_factor * speed_max

    #if you are close to one of the make your speed lower. speed_min is set to such a point that it will catch the point while turning around it.
    if distance_to < 120:
        desired_speed = max(speed_min, player_speed - 0.01)
    else:
        desired_speed = min(player_speed + 0.05, speed_max)

    player_speed += (desired_speed - player_speed) * 0.1

def score1(distance, angle, height_diff):
    # the function is a way to find the best point to fly to (because not always the nearest point is the best)
    angle_penalty = abs(angle) / 90
    height_penalty = height_diff / 300
    total_penalty = 1 + angle_penalty + height_penalty
    return 1 / (distance * total_penalty)

def autopilot4_update():
    closest_index = None
    best_score = -10000.0
    distance_to = None
    global target_heading2
    global player_speed_change, player_position, heading_degree, player_position_change, player_height, player_vertical_speed

    # the function updates where to fly. For every number it checks the score from the score1() function. If it is better than best score for now, it chooses this point. At the end it just gives the index of the best point found.

    for j in range(points_number):
        point_position_vec = pygame.Vector2(pointX[j], pointY[j])
        distance_to = player_position.distance_to(point_position_vec)
        error_angle = (target_heading2 - heading_degree + 540) % 360 - 180
        altitude_difference = abs(player_height - pointZ[j])
        current_score = score1(distance_to, error_angle, altitude_difference)
        if current_score > best_score:
            best_score = current_score
            closest_index = j
    if closest_index is not None:
        # it takes this index and calculate the target heading that the plane should take.

        target_vector = pygame.Vector2(pointX[closest_index] - player_position.x + 12,

                                           12 + pointY[closest_index] - player_position.y)

        #height control of autopilot
        height_difference = pointZ[closest_index] - player_height
        if height_difference > 200:
            player_vertical_speed = 10
        elif height_difference < -200:
            player_vertical_speed = -10
        elif height_difference > 5:
            player_vertical_speed -= 0.1
        elif height_difference < 5:
            player_vertical_speed += 0.1
        else:
            player_vertical_speed = 0

        if target_vector.length() != 0:
            target_vector_unit = target_vector.normalize()

            target_heading2 = math.degrees(math.atan2(target_vector_unit.x, -target_vector_unit.y)) % 360
    return distance_to

def autopilot4_turn_update():
    global heading_degree, target_heading2
    global autopilot4_key_left, autopilot4_key_right, autopilot4_ctrl
    #this function calculates the error that is between -180 and 180 degrees abd then decides where to turn. It is using different way for turning as it is more efficient in comparision to the previous ones.
    error = (target_heading2 - heading_degree + 540) % 360 - 180

    autopilot4_ctrl = False
    autopilot4_key_left = False
    autopilot4_key_right = False

    if error != 0:  # when error is not 0

        autopilot4_ctrl = True  # sharp turns only
        if error < 0:
            autopilot4_key_left = True
            autopilot4_key_right = False
        else:
            autopilot4_key_right = True
            autopilot4_key_left = False

#Hand Mode of flying
def heading_vector(heading_degree1):
    heading_angle_radians = math.radians(heading_degree1)
    y = -math.cos(heading_angle_radians)
    x = math.sin(heading_angle_radians)
    return pygame.Vector2(x, y)  # it is a function that changes heading in degrees into a unit vector. It is important for game to be able to that.

#handle input - when something is clicked, something is happening
def handle_input():
    global heading_degree, player_speed, player_vertical_speed
    keys = pygame.key.get_pressed()
    # there are two types of clicking - keys[] and pygame.KEYDOWN or KEYUP. The first one works like that:
    # If there are two keys clicked at the same time, it finds both of them clicked
    # And the second one: only one (the first one) key is considered as clicked - it is used for autopilots

    turn_left = keys[pygame.K_a]
    turn_right = keys[pygame.K_d]
    sharp_turn = keys[pygame.K_LCTRL]

    # It can be done as with speed, however, for the autopilot mode 4, I tried something new: it makes the new variable that can be used for turning in autopilot 4
    # it says that if you are using autopilot 4, then 'click' these and these keys, so that it can be controlled similarly to the hand-mode version (it makes it more controllable)

    if autopilot_mode4:
        turn_left = autopilot4_key_left
        turn_right = autopilot4_key_right
        sharp_turn = autopilot4_ctrl

    # it is hand and autopilot 4 way of turning
    if not autopilot_mode1 and not autopilot_mode2 and not autopilot_mode3:
        if turn_right:
            heading_degree += 3 if sharp_turn else 1
        if turn_left:
            heading_degree -= 3 if sharp_turn else 1

    #keys for altitude change - arrow up for increasing and arrown down for decreasing the altitude. If nothing is clicked, then make it 0
    if not autopilot_mode1:
        if keys[pygame.K_UP]:
            player_vertical_speed += 0.05
        elif keys[pygame.K_DOWN]:
            player_vertical_speed -= 0.05

    #limitation for vertical speed
    if player_vertical_speed>10:
        player_vertical_speed=10
    elif player_vertical_speed<-10:
        player_vertical_speed=-10

    # hand acceleration abd speed control. Not used while autopilot 3 and 4 used.
    if not autopilot_mode3 and not autopilot_mode4:
        if keys[pygame.K_w]:
            if keys[pygame.K_LSHIFT]:
                player_speed += 0.03
            else:
                player_speed += 0.01
        elif keys[pygame.K_s]:
            if keys[pygame.K_LSHIFT]:
                player_speed -= 0.03
            else:
                player_speed -= 0.01


    # speed limit, so that you cannot fly in negative speed directions and above the max speed.
    if player_speed <= 0:
        player_speed = 0

    if player_speed >= speed_max:
        player_speed = speed_max

def update_player():

    global player_speed_change, player_position, heading_degree, player_position_change, player_height, player_vertical_speed

    # player position change is a unit vector coming from the function heading_vector
    player_position_change = heading_vector(heading_degree)

    # player position changes by the multiplication of the unit vector and its speed - it creates the effect that if the player speed is larger, the player position changes more rapidly
    player_position += player_speed * player_position_change

    #change player's height accordingly to the vertical speed
    player_height += player_vertical_speed

    # heading degree must be between 0 and 360, sometimes it crashed because of that so I put it here to prevent.
    heading_degree %= 360

    #prevent making height below 0
    if player_height < 0:
        player_height = 0
        player_vertical_speed = 0


    # after uncommenting the following, if the plane leaves the screen on the left, it should appear on the right, however, the drawn line is not working correctly then and after some time I prefer to have a game like it is now instead of such mode. But I left it, so it is possible.
    #if player_position.x < 0:
     #   player_position.x = 1300
    #elif player_position.x > 1300:
    #    player_position.x = 0

     # if speed is not 0, then there is an addition to the list for the flight path of the player position, which will be drawn later
    if player_speed != 0 :
        flight_path.append(player_position.xy)

#creation of the points on the screen
def points_creation():
    # just show on the screen all of the points
    for j in range(points_number):
        screen.blit(pointImg[j],(pointX[j], pointY[j]))
        altitude_text = font.render(f"{pointZ[j]} m", 1, (0, 0, 0))
        screen.blit(altitude_text, (pointX[j], pointY[j] - 20))
#function that checks whether there was a collisionm or not
def is_collection():
    # for every point calculate the distance between point and the player
    for j in range(points_number):
        point_position = pygame.Vector2(pointX[j], pointY[j])
        distance_2d = player_position.distance_to(point_position)
        altitude_difference = abs(player_height - pointZ[j])

        # if the distance is small enough it looks it is hit and the height difference is not big, give us the index (j) of the point, which is going to be used in the collision_happened() function

        if distance_2d <= 24 and altitude_difference <= 100:
            return j
    return None
#recreation of the point after it got hit and add 1 point to the score
def collision_happened():
    global score_value
    index = is_collection()
    # is_collection() functions returns the index of the point that was hit
    if index is not None:
        # if it is anything different than none, add one point to the score and create new point randomly
        score_value += 1
        pointX[index] = random.randint(0, 1268)
        pointY[index] = random.randint(0, 668)
        pointZ[index] = random.randint(500,3000)

        # add it to the lists for the graph later
        time_now = (pygame.time.get_ticks() - start_ticks) / 1000
        score_over_time.append((time_now, score_value))

#HUD drawing in the left top corner
def draw_hud():
    # variables for the text it self in good fonts
    speed_text = font.render(f"Speed: {player_speed:.2f}", 1, (0,0,0))
    heading_text = font.render(f"Heading: {heading_degree:.1f}°", 1, (0,0,0))
    position_text = font.render(f"Position: ({int(player_position.x)}, {int(player_position.y)})", 1, (0,0,0))
    autopilot1_heading_text = font.render(f"Autopilot 1 heading: {target_heading:.1f}°", 1, (0, 0, 0))
    ap_text = font.render(f"Autopilot 1: {'ON' if autopilot_mode1 else 'OFF'}", 1, (0, 0, 0) if autopilot_mode1 else (255, 0, 0))
    scorevaluetext = font.render(f"Your score is {score_value}", 1,(0,0,0))
    time_left = 60 - ((pygame.time.get_ticks() - start_ticks) / 1000)
    time_left_text = font.render(f"Time left: {time_left:.2f}", 1, (0,0,0))
    autopilot2_text = font.render(f"Autopilot 2: {'ON' if autopilot_mode2 else 'OFF'}", 1, (0, 0, 0) if autopilot_mode2 else (255, 0, 0))
    autopilot3_text = font.render(f"Autopilot 3: {'ON' if autopilot_mode3 else 'OFF'}", 1,
                                  (0, 0, 0) if autopilot_mode3 else (255, 0, 0))
    autopilot4_text = font.render(f"Autopilot 4: {'ON' if autopilot_mode4 else 'OFF'}", 1, (0, 0, 0) if autopilot_mode4 else (255, 0, 0))
    altitude_text = font.render(f"Altitude: {player_height:.1f} m", 1, (0, 0, 0))
    vertical_speed_text = font.render(f"Vertical speed: {player_vertical_speed:.2f} m/s", 1, (0, 0, 0))
    altitude_autopilot1_text = font.render(f'Goal altitude: {height_autopilot1:.2f} m', 1, (0,0,0))

    # showing all the texts on the screen on the right positions
    screen.blit(speed_text, (10,10))
    screen.blit(heading_text, (10, 25))
    screen.blit(position_text, (10, 40))
    screen.blit(autopilot1_heading_text, (10, 55))
    screen.blit(ap_text, (10, 70))
    screen.blit(autopilot2_text, (10, 85))
    screen.blit(autopilot3_text, (10, 100))
    screen.blit(autopilot4_text, (10, 115))
    screen.blit(scorevaluetext, (10, 130))
    screen.blit(time_left_text, (10, 145))
    screen.blit(altitude_text, (10, 160))
    screen.blit(vertical_speed_text, (10, 175))
    screen.blit(altitude_autopilot1_text, (10,190))

#drawing after plane
def drawing():
    global rotated_player, rotated_rect, heading_degree

    #background
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    #point creation
    points_creation()

    # turning of the icon of the aeroplane, so when we turn it looks like we are turning
    rotated_player = pygame.transform.rotate(playerImg, -heading_degree)
    rotated_rect = rotated_player.get_rect(center=player_position)
    screen.blit(rotated_player, rotated_rect)

     # drawing of the line behind the plane
    if len(flight_path) > 1:
        pygame.draw.lines(screen, (0, 0, 0), False, flight_path, 2)

    #draw left top HUD
    draw_hud()

    # refresh the screen, so we can see it
    pygame.display.update()

#end of the game - what happens then
def endgame():
    global player_speed

    time_left = 60 - ((pygame.time.get_ticks() - start_ticks) / 1000) # counts time to 60 seconds (when it is 60 seconds, the time_left is 0)
    if time_left <= 0: #if time left is 0 or smaller
        player_speed = 0 #speed is 0
        end_game_text = font2.render(f"Time's up! Your score: {score_value}", True, (0, 0, 0)) #text on the screen
        text_rect = end_game_text.get_rect(center=(650, 350))  #coordinates of the text
        screen.blit(end_game_text, text_rect) #write the text
        pygame.display.update() #update the screen, so the text is visible
        pygame.time.delay(5000)  # show the message for 5 seconds

        #creating of the graph of points in time
        times = [x[0] for x in score_over_time]
        scores = [x[1] for x in score_over_time]
        plt.figure(figsize=(8, 4))
        plt.plot(times, scores, marker='o')
        plt.title("Points in time")
        plt.xlabel("Time (s)")
        plt.ylabel("Points number")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        pygame.quit()
        exit()

# Game Loop
running = True
while running:
    # max FPS is 60
    clock.tick(60)

    # functions that are happening
    # if none of the autopilot is on, then there is a hand mode, so we use only handle input function
    handle_input()

    # simple if loop: if autopilot mode 1 is on, then update it accordingly to the autopilot mode 1 and so on for the others
    if autopilot_mode1:
        autopilot1_update()
        autopilot1_height_update()
    if autopilot_mode2:
        autopilot2_update()
        autopilot2_turn_update()
    if autopilot_mode3:
        distance_to = autopilot3_update()
        # because this type of autopilot changes both heading and speed, it requires two update functions - one for each parameter
        autopilot3_turn_update()
        autopilot3_speed_control(distance_to)
    if autopilot_mode4:
        distance_to = autopilot4_update()
        autopilot4_turn_update()
        autopilot4_speed_control(distance_to)

    #update player position on the screen
    update_player()

    #check whether collision has happened?
    collision_happened()

    #drawing of everything on the screen
    drawing()

    #endgame - happens after 60 seconds
    endgame()


    # checking whether any key was clicked so the autopilot works
    for event in pygame.event.get():
        autopilot1_on(event)
        autopilot1_heading(event)
        autopilot1_height(event)
        autopilot2_on(event)
        autopilot3_on(event)
        autopilot4_on(event)

        # turning off the screen - red cross in top right or by clicking ESCAPE button
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

#leave pygame
pygame.quit()
