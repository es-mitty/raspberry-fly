import pyautogui as auto
import socketio
import time

# Globals for flight simulator keys
THROTTLE_UP = 'q'
THROTTLE_DOWN = 'a'
THROTTLE_INCREMENT = 20

# Create socketIO client for receiving data
io = socketio.Client()

# Initialize mouse controller
width, height = auto.size()
print('Dimensions:', width, height)

# Initialize variables
#Track how many times we've throttled up or down
throttle_position = 0
#Used to terminate loop upon certain exceptions
run = True

#Continuously request position data from the pi
def eventloop():
    while run:
        io.emit('collect_data')
        time.sleep(0.1)

    io.disconnect()


# Socket events

@io.event
def connect():
    print('connection established')
    eventloop()


@io.event
def disconnect():
    print('disconnected')


# Get Data
@io.event
def flight_data(data):
    #Reference globals
    global throttle_position
    global run

    # Testing data in console
    print(data)
    print('Throttle Value:', round(data['throttle_val'] * THROTTLE_INCREMENT))
    print('Throttle Position:', throttle_position)

    # Mouse position determined using potentiometer data
    x_width = round(data['x'] * width)
    y_height = round(data['y'] * height)
    try:
        auto.moveTo(x_width, y_height, duration=0.1)

        # Throttle up or down based on potentionmeter data
        throttle = (round(data['throttle_val'] * THROTTLE_INCREMENT))
        if throttle > throttle_position and throttle > 2:
            auto.press(THROTTLE_UP)
            throttle_position += 1
        elif throttle < throttle_position:
            auto.press(THROTTLE_DOWN)
            throttle_position -= 1
    except auto.FailSafeException:
        run = False


# Main method
if __name__ == '__main__':
    ip = input("Enter an IP Address:")
    print('http://' + ip + ':5000')
    time.sleep(6)
    io.connect('http://' + ip + ':5000')
