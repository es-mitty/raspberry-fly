import socketio
import time
import eventlet
import board
import busio
import adafruit_ads1x15.ads1115 as ads
from adafruit_ads1x15.analog_in import AnalogIn
import threading

# Create socketIO Server
io = socketio.Server()

# Setup of ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
yoke = ads.ADS1115(i2c)

a0 = AnalogIn(yoke, ads.P0)
a1 = AnalogIn(yoke, ads.P1)
a2 = AnalogIn(yoke, ads.P2)


# Runs the WSGI server
def run_server():
    app = socketio.WSGIApp(io)
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
    print("Server closed.")

# Collect x and y data from analog to digital converter, then emit it

@io.event
def collect_data(sid):
    voltage_max = 3.3
    voltage_min = 0
    whole_val = voltage_max - voltage_min

    x_volt = a0.voltage
    y_volt = a1.voltage
    throttle_volt = a2.voltage

    x_val = x_volt / whole_val
    y_val = (y_volt - 1.1)/1

    throttle_val = throttle_volt / whole_val

    print(x_volt, y_volt, throttle_volt)
    emit_data(x_val, y_val, throttle_val, sid)


# Emits x and y decimals to all socket connections
def emit_data(x, y, throt, sid):
    io.emit('flight_data', {'x': x, 'y': y, 'throttle_val': throt}, room=sid)
    print('emitting:', x, y)


# Socket event to detect a connection
@io.event
def connect(sid, environ, auth):
    print('connect ', sid)
    #collect_data(sid)

@io.event
def disconnect(sid):
    print('User', sid, 'disconnected.')

# Define main
def main():
    run_server()


# Run main method
if __name__ == '__main__':
    main()
