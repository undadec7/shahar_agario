import socket
import pyautogui
import time, threading
from threading import Lock
import select
import pygame
import random
from threading import Thread
import _thread

#Constants
WHITE = (255,255,255)
RED = (255,0,0)
BLACK = (0,0,0)


#variables
Food_dict_thread = {}
Food_dict = {}
Food_List = []
Food_List_Send = []
old_foood_list_sent = []
players = {}
messages_to_send = []

mylock = Lock()

def food(delay):
    global Food_List
    global mylock
    count = 0
    while True:
        time.sleep(delay)
        x = random.randint(0, 14000)
        y = random.randint(0, 10000)
        food_list = str(x) + "," + str(y)
        Food_dict_thread["food" + str(count)] = food_list
        count = count + 1
        # append a list of ["food<num>", "<x>,<y>"] to the big list

        mylock.acquire()
        Food_List.append([("food" + str(count)), food_list])
        mylock.release()






def initialize_server_settings():
    # initialize server settings:
    import socket
    import select
    MAX_MSG_LENGTH = 1024
    SERVER_PORT = 8822
    SERVER_IP = "0.0.0.0"
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print("Listening for clients...")
    global client_sockets
    client_sockets = []
    global messages_to_send
    messages_to_send = []
    return server_socket

def send_size_and_message_food(client_socket, reply, food_num):

    size = len(food_num.encode()).to_bytes(4, byteorder='big')
    client_socket.send(size)
    client_socket.send(food_num.encode())
    size = len(reply.encode()).to_bytes(4, byteorder='big')
    client_socket.send(size)
    client_socket.send(reply.encode())



def send_size_and_message(client_socket, reply):
    size = len(reply[0]).to_bytes(4, byteorder='big')
    client_socket.send(size)
    client_socket.send(reply[0].encode())
    size = len(reply[1][0]).to_bytes(4, byteorder='big')
    client_socket.send(size)
    client_socket.send(reply[1][0].encode())
    size = len(reply[1][1]).to_bytes(4, byteorder='big')
    client_socket.send(size)
    client_socket.send(reply[1][1].encode())

def receive_message(current_socket):
    global players
    global messages_to_send
    received_bytes = current_socket.recv(4)
    size = int.from_bytes(received_bytes, byteorder='big')
    name = current_socket.recv(size).decode()
    if name == "die":
        received_bytes = current_socket.recv(4)
        size = int.from_bytes(received_bytes, byteorder='big')
        message = current_socket.recv(size).decode()

        return 0

    received_bytes = current_socket.recv(4)
    size = int.from_bytes(received_bytes, byteorder='big')
    message = current_socket.recv(size).decode()
    if "food" in name:

        data = [name, message]
    else:
        received_bytes = current_socket.recv(4)
        size = int.from_bytes(received_bytes, byteorder='big')
        player_size = current_socket.recv(size).decode()
        data = [name, [message, player_size]]
    return data


def main():
    global Food_List
    global Food_List_Send
    Food_List_Short = []
    i = 5
    server_socket = initialize_server_settings()

    pygame.init()

    global messages_to_send
    global players
    t1 = threading.Thread(target=food, args=[4])
    t1.start()


    finish = False
    while not finish:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finish = True





        rlist, wlist, xlist = select.select([server_socket] + client_sockets, [], [],0.01)
        for current_socket in rlist:
            if current_socket is server_socket:
                connection, client_address = current_socket.accept()
                print("New Client joined!", client_address)
                client_sockets.append(connection)

                #Food_List_Send = Food_List.copy()
                for foods in Food_List_Send:

                    print("food send first")
                    send_size_and_message_food(connection, foods[1], foods[0])



            else:
                try:

                    data = receive_message(current_socket)
                except:
                    count = 0
                    for s in rlist:

                        if s == current_socket:
                            current_socket.close()
                            del client_sockets[count]
                        count = count + 1

                if data == '' or data == 0 or data[0] == '':
                    None
                else:
                    messages_to_send.append(data)

        Food_dict = dict(Food_dict_thread)
        old_foood_list_sent = Food_List_Send
        mylock.acquire()
        Food_List_Send = Food_List.copy()
        mylock.release()


        key_counter = 0
        if len(messages_to_send) != 0:
            for message in messages_to_send:


                p_place = message[1]
                p_size = int(p_place[1])
                p_place = p_place[0].split(",")
                p_placex = p_place[0]
                p_placey = p_place[1]
                p_placex = int(p_placex)
                p_placey = int(p_placey)

                for foods in Food_List_Send:
                    food_place = foods[1].split(",")
                    food_placex = int(food_place[0])
                    food_placey = int(food_place[1])

                    if food_placex > (p_placex - p_size) and food_placex < (p_placex + p_size) and food_placey > (p_placey - p_size) and food_placey < (p_placey + p_size):
                        mylock.acquire()
                        Food_List_Send.remove(foods)
                        mylock.release()

        mylock.acquire()
        Food_List = Food_List_Send.copy()
        mylock.release()

        for current_socket_write in client_sockets:
            if len(messages_to_send) != 0:
                for message in messages_to_send:

                    try:

                        send_size_and_message(current_socket_write, message)
                    except:
                        removing_list = False
                        for s in client_sockets:
                            if s == current_socket_write:
                                current_socket_write.close()
                                removing_list = True

                        client_sockets.remove(current_socket_write)

            if Food_List_Send != old_foood_list_sent:
                Food_List_Short = Food_List_Send.copy()
                countf1 = 0
                countf2 = 0
                for f in Food_List_Short:

                    for fo in old_foood_list_sent:
                        if fo == f:
                            Food_List_Short.pop(countf1)
                            print(Food_List_Short)
                        countf2 = countf2 + 1
                    countf1 = countf1 + 1

                for foods in Food_List_Short:
                    try:

                        send_size_and_message_food(current_socket_write, foods[1], foods[0])
                    except:
                        for s in client_address:
                            if s == current_socket_write:
                                current_socket_write.close()
                                client_address.pop(current_socket_write)
        if Food_List_Send != old_foood_list_sent:
            old_foood_list_sent = Food_List_Send.copy()
        messages_to_send = []






if __name__ == "__main__":
    main()
