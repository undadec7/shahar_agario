import socket
import select
import pygame
import random
import time
import threading
from threading import Thread
import sys



# Variables
client_sockets = []
player_size = 20
y = 0
x = 0


# Constants
location_x = random.randint(0, 14000)
location_y = random.randint(0, 10000)
WINDOW_WIDTH = 1940
WINDOW_HEIGHT = 1020
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
clock = pygame.time.Clock()

# Init screen
pygame.init()
pygame.mixer.init()
size_screen = (WINDOW_WIDTH, WINDOW_HEIGHT)
screen = pygame.display.set_mode(size_screen)
pygame.display.set_caption("P1")
screen.fill(WHITE)
pygame.display.flip()
pygame.font.init()

# Make grid
grid_horizontal = []
grid_vertical = []
count1 = 0
count2 = 0
food_start = []
food = {}
countf = -1
for x in range(3000):
    xf = random.randint(0, 14000)
    yf = random.randint(0, 10000)
    xf = str(xf)
    yf = str(yf)
    xfyf = xf + "," + yf
    food["food" + str(countf)] = xfyf
    countf = countf - 1


def Restart(my_socket, names,timer):
    global y
    global x
    global player_size
    global name
    player_size = 20
    finish_r = False
    while finish_r != True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finish = True
                finish_r = True
                reply = 0
                timer.cancel()
                sys.exit()
                # User pressed a key
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    y = random.randint(0,10000)
                    x = random.randint(0,14000)
                    game()
                    finish_r = True


def song():
    # play song
    pygame.mixer.music.load("song.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play()





def connect_to_server():
    # connecting to server:
    my_socket = socket.socket()
    my_socket.connect(("127.0.0.1", 8822))
    return my_socket

def send_size_and_message(my_socket, reply, name):
    global player_size
    if reply == 0:
        reply = "die"
        size_message = len(reply).to_bytes(4, byteorder='big')
        my_socket.send(size_message)
        my_socket.send(reply.encode())
        size_message = len(name).to_bytes(4, byteorder='big')
        my_socket.send(size_message)
        my_socket.send(name.encode())
    else:
        name_size = len(name).to_bytes(4, byteorder='big')
        my_socket.send(name_size)
        my_socket.send(name.encode())
        size_message = len(reply).to_bytes(4, byteorder='big')
        my_socket.send(size_message)
        my_socket.send(reply.encode())
        size_message = len(str(player_size)).to_bytes(4, byteorder='big')
        my_socket.send(size_message)
        my_socket.send(str(player_size).encode())






def receive_message(current_socket):
    received_bytes = current_socket.recv(4)
    size = int.from_bytes(received_bytes, byteorder='big')
    name = current_socket.recv(size).decode()
    received_bytes = current_socket.recv(4)
    size = int.from_bytes(received_bytes, byteorder='big')
    message = current_socket.recv(size).decode()
    if "food" in name:
        data = [name,message]
    else:
        received_bytes = current_socket.recv(4)
        size = int.from_bytes(received_bytes, byteorder='big')
        player_size = current_socket.recv(size).decode()
        data = [name, [message, player_size]]
    return data




def game():
    global y
    global x
    global player_size
    global grid_vertical
    global grid_horizontal
    name = input("Enter name: ")
    my_socket = connect_to_server()
    data = None
    x = random.randint(0, 14000)
    y = random.randint(0, 10000)
    y_b = 0
    x_b = 0
    yk = 0
    xk = 0
    xy_before = [0,0]
    players_to_print = []
    food_list = []
    players = {}
    global food
    finish = False
    player_size = 50
    eat_food = None
    my_location = [location_x, location_y]
    speed = 100
    myfont = pygame.font.SysFont('Comic Sans MS', 10)
    myfont_score = pygame.font.SysFont('Comic Sans MS', 30)
    speed_count = 0
    size_count = 0
    size_devider = 0

    timer = threading.Timer(80.0, song)
    timer.start()

    pygame.mixer.music.load("song.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play()

    while finish != True:
        if size_count >= 20:
            if size_devider < 13:
                size_count = 0
                size_devider = size_devider + 1







        rlist, wlist, xlist = select.select([my_socket], [], [],0.01)
        data = None
        for s in rlist:
            data = receive_message(s)
            if "food" in data[0]:
                food[data[0]] = data[1]
            else:
                if data[0] == name:
                    my_location = data[1]
                    my_location = my_location[0].split(",")
                players[data[0]] = data[1]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finish = True
                finish_r = True
                reply = 0
                timer.cancel()
                sys.exit()
                send_size_and_message(my_socket, reply, name)

            # User pressed a key
            elif event.type == pygame.KEYDOWN:

                if y >= 0:

                    if event.key == pygame.K_w:  # Up
                        yk = -5
                        if y <= 0:
                            yk = 0
                if y <= 10000:
                    if event.key == pygame.K_s:  # Down
                        yk = 5
                        if y >= 10000:
                            yk = 0
                if x <= 14000:

                    if event.key == pygame.K_d:  # Right
                        xk = 5
                        if x >= 14000:
                            xk = 0
                if x >= 0:
                    if event.key == pygame.K_a:  # Left
                        xk = -5
                        if x <= 0:
                            xk = 0
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:  # Up
                    yk = 0
                if event.key == pygame.K_s:  # Down
                    yk = 0
                if event.key == pygame.K_d:  # Right
                    xk = 0
                if event.key == pygame.K_a:  # Left
                    xk = 0





        y += yk
        x += xk

        xy = [x, y]


        xySend = str(x) + "," + str(y)
        if xy != xy_before:
            send_size_and_message(my_socket, xySend, name)

        xy_before = [x, y]


        key_counter = 0

        for i in players:

            data_split = players.get(i)
            data_split = data_split[0].split(",")
            data_split[0] = int(data_split[0])
            data_split[1] = int(data_split[1])
            keys_list = list(players)
            key = keys_list[key_counter]
            key_counter += 1
            if key == name:
                for foods in food:
                    food_split = food[foods]
                    food_split = food_split.split(",")
                    foodx = int(food_split[0])
                    foody = int(food_split[1])
                    if (data_split[0] < (foodx + (player_size))) and (data_split[0] > (foodx - (player_size))) and (data_split[1] < (foody + (player_size))) and (data_split[1] > (foody - (player_size))):
                        eat_food = foods
                        player_size = player_size + 1
                        size_count = size_count + 1
                        speed_count = speed_count + 1
            else:
                for foods in food:
                    food_split = food[foods]
                    food_split = food_split.split(",")
                    foodx = int(food_split[0])
                    foody = int(food_split[1])
                    if (data_split[0] < (foodx + (player_size))) and (data_split[0] > (foodx - (player_size))) and (data_split[1] < (foody + (player_size))) and (data_split[1] > (foody - (player_size))):
                        eat_food = foods


        if eat_food != None:

            food.pop(eat_food)
            eat_food = None


        screen.fill(WHITE)







        key_counter = 0
        for foods in food:

            food_split = food[foods].split(",")
            foodx = int(food_split[0])
            foody = int(food_split[1])
            if foodx > (int(my_location[0]) - 970) and foodx < (int(my_location[0]) + 970) and foody > (int(my_location[1]) - 510) and foody < (int(my_location[1]) + 510):



                foodx = foodx - int(my_location[0])
                foodx = foodx + 970

                foody = foody - int(my_location[1])
                foody = foody + 510
                pygame.draw.circle(screen, [random.randint(0,255),random.randint(0,255),random.randint(0,255)], [foodx, foody], 15 - size_devider)

        players_to_kill = []

        for i in players:

            data_split = players[i][0].split(",")
            data_split[0] = int(data_split[0])
            data_split[1] = int(data_split[1])
            keys_list = list(players).copy()
            key = keys_list[key_counter]
            key_counter += 1
            if key == name:
                my_location = data_split
                pygame.draw.circle(screen, BLUE, [970, 510], player_size - size_devider - size_devider)
            else:
                if data_split[0] > (int(my_location[0]) - 970) and data_split[0] < (int(my_location[0]) + 970) and data_split[1] > (int(my_location[1]) - 510) and data_split[1] < (int(my_location[1]) + 510):

                    data_split_p = [(data_split[0] - my_location[0]) + 970, (data_split[1] - my_location[1]) + 510]
                    pygame.draw.circle(screen, RED, data_split_p, int(players[key][1]) - size_devider)



                if int(players[key][1]) < (player_size):
                    if data_split[0] > (int(my_location[0]) - (player_size - int(players[key][1]))) and data_split[0] < (int(my_location[0]) + (player_size - int(players[key][1]))) and data_split[1] > (int(my_location[1]) - (player_size - int(players[key][1]))) and data_split[1] < (int(my_location[1]) + (player_size - int(players[key][1]))):
                        if int(players[key][1]) < (player_size + 5):
                            print("you eat")
                            player_size = player_size + int(players[key][1])
                            players_to_kill.append(key)
                else:
                    if int(my_location[0]) > (data_split[0] - (int(players[key][1]) - player_size)) and int(my_location[0]) < (data_split[0] + (int(players[key][1]) - player_size)) and int(my_location[1]) > (data_split[1] - (int(players[key][1]) - player_size)) and int(my_location[1]) < (data_split[1] + (int(players[key][1]) - player_size)):
                        if int(players[key][1]) > (player_size + 5):
                            screen.fill(RED)
                            pygame.display.flip()
                            Restart(my_socket, name, timer)


        for p in players_to_kill:
            players.pop(p)

        pygame.draw.line(screen, BLACK, [970, 10], [1010, 10], 1)
        pygame.draw.line(screen, BLACK, [970, 30], [1010, 30], 1)
        pygame.draw.line(screen, BLACK, [970, 50], [1010, 50], 1)
        pygame.draw.line(screen, BLACK, [970, 70], [1010, 70], 1)
        pygame.draw.line(screen, BLACK, [970, 10], [970, 70], 1)
        pygame.draw.line(screen, BLACK, [1010, 10], [1010, 70], 1)

        first = ""
        second = ""
        third = ""
        max1 = 0
        max2 = 0
        max3 = 0

        key_counter = 0
        for i in players:
            keys_list = list(players).copy()
            key = keys_list[key_counter]

            if int(players[key][1]) > max1:
                third = second
                second = first
                first = key + " " + str(int(players[key][1]) - 50)
                max3 = max2
                max2 = max1
                max1 = int(players[key][1])
            elif int(players[key][1]) > max2:
                third = second
                second = key + " " + str(int(players[key][1]) - 50)
                max3 = max2
                max2 = int(players[key][1])
            elif int(players[key][1]) > max3:
                third = key + " " + str(int(players[key][1]) - 50)
                max3 = int(players[key][1])
            key_counter += 1


        textsurface = myfont.render(first, False, (0, 0, 0))

        screen.blit(textsurface, (975, 12))

        textsurface = myfont.render(second, False, (0, 0, 0))

        screen.blit(textsurface, (975, 32))

        textsurface = myfont.render(third, False, (0, 0, 0))

        screen.blit(textsurface, (975, 52))

        textsurface = myfont_score.render(("score: " + str(player_size - 50)), False, (0, 0, 0))

        screen.blit(textsurface, (100, 950))



        pygame.display.update()

    # closing:
    my_socket.close()


def main():



    game()



if __name__ == "__main__":
    main()
