# This example script demonstrates how to use Python to fly Tello in a box mission
# This script is part of our course on Tello drone programming
# https://learn.droneblocks.io/p/tello-drone-programming-with-python/

# Import the necessary modules
import socket
import threading
import time
import math

# IP and port of Tello
#tello1_address = ('IP_address_of_drone', 8889)
tello1_address = ('10.0.0.162', 8889) # my addreses
tello2_address = ('10.0.0.154',8889) # ^^
tello3_address = ('10.0.0.202',8889) # <------ This is not found yet but will be when we test it.

# IP and port of local computer
local1_address = ('',9010)
local2_address = ('',9011)
local3_address = ('',9012)


# Create a UDP connection that we'll send the command to
sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to the local address and port
sock1.bind(local1_address)
sock2.bind(local2_address)
sock3.bind(local3_address)

def send(message,delay): #sends to all 3.
    try:
        sock1.sendto(message.encode(),tello1_address)
        sock2.sendto(message.encode(),tello2_address)
        sock3.sendto(message.encode(),tello3_address)
        print("Sending message to all three: "+message)
    except Exception as e:
        print("Error sending: "+str(e))
    time.sleep(delay)

def send2(message,delay): #only for sending to drones 1 and 2.
    try:
        sock1.sendto(message.encode(),tello1_address)
        sock2.sendto(message.encode(),tello2_address)
        print("Sending message to both: "+message)
    except Exception as e:
        print("Error sending: "+str(e))
    time.sleep(delay)

def Drone3_do(message, delay):
    # Try to send the message otherwise print the exception
    try:
        sock3.sendto(message.encode(), tello3_address)
        print("Sending message to Tello # 3: " + message)
    except Exception as e:
        print("Error sending: " + str(e))
    # Delay for a user-defined period of time
    time.sleep(delay)

def Drone2_do(message, delay):
    # Try to send the message otherwise print the exception
    try:
        sock2.sendto(message.encode(), tello2_address)
        print("Sending message to Tello # 2: " + message)
    except Exception as e:
        print("Error sending: " + str(e))
    # Delay for a user-defined period of time
    time.sleep(delay)
# Send the message to Tello and allow for a delay in seconds
def Drone1_do(message, delay):
    # Try to send the message otherwise print the exception
    try:
        sock1.sendto(message.encode(), tello1_address)
        print("Sending message to Tello # 1: " + message)
    except Exception as e:
        print("Error sending: " + str(e))
    # Delay for a user-defined period of time
    time.sleep(delay)

# Receive the message from Tello
def receive():
    # Continuously loop and listen for incoming messages
    while True:
        # Try to receive the message otherwise print the exception
        try:
            response1, ip_address = sock1.recvfrom(128)
            response2, ip_address = sock2.recvfrom(128)
            response3, ip_address = sock3.recvfrom(128)
            print("Received message: from Tello EDU #1: " + response1.decode(encoding='utf-8'))
            print("Received message: from Tello EDU #2: " + response2.decode(encoding='utf-8'))
            print("Received message: from Tello EDU #3: " + response3.decode(encoding='utf-8'))
        except Exception as e:
            # If there's an error close the socket and break out of the loop
            sock1.close()
            sock2.close()
            sock3.close()
            print("Error receiving: " + str(e))
            break

# Create and start a listening thread that runs in the background
# This utilizes our receive functions and will continuously monitor for incoming messages
receiveThread = threading.Thread(target=receive)
receiveThread.daemon = True
receiveThread.start()

send("command",4)
send("battery?",4)
#send("takeoff",7)
#send("go 0 0 0 0",4)
Drone2_do("go 0 -30 0 20",6) #goes to the right 30
Drone1_do("stop",5)
Drone3_do("go 0 30 0 20", 6) #goes to the left 30
Drone3_do("ccw 180",6) #rotates the 3rd drone 180 degrees to start moving to the left.
#Drone2_do("right 60",5)

z_point = 0
def Turn(last_theta,radius):
    theta = 0
    if last_theta <= 90:
        delta_angel = last_theta / 4
    elif last_theta <= 180 & last_theta >= 90:
        delta_angel = last_theta / 8
    elif last_theta <= 270 & last_theta >= 180:
        delta_angel = last_theta / 12
    elif last_theta <= 360 & last_theta >= 270:
        delta_angel = last_theta / 16
    else:
        print("Unknown")

    while theta < last_theta:
        theta = theta + delta_angel
        x = (math.cos(math.radians(theta))) * radius
        x_float = float(str(x))
        x_int = int(x_float)

        print("theta = "+str(theta))
        send("ccw "+str(delta_angel),4) #rotates all 3 drones.

        if theta != 90:
            Drone2_do("forward "+str(x_int),5)
            Drone3_do("forward "+str(x_int),5)
            Drone1_do("stop",5)
        else:
            print("90 degree rotate has finished")
            send("stop",4)

        time.sleep(2)

print("first call to turn")
Turn(90,60)
print("second call to turn")
Turn(90,60)
print("third call to turn")
Turn(90,60)
print("fourth call to turn")
Turn(90,60)
print("return to center")
Drone2_do("go 0 30 0 20",6) #go back to center
Drone3_do("go 0 -30 0 20",6) #go back to center
# Print message
print("Drones are landing now")
send("land", 4)
print("Mission completed successfully!")

# Close the socket
sock1.close()
sock2.close()
sock3.close()