import socket
import serial
from threading import Thread
from time import sleep

thWorkingFlag = False

def com2tcpThread(conn, port):
    try:
        while thWorkingFlag:
            data = port.read()
            if data:
                #print("COM>TCP: ", data)
                conn.send(data)
    except Exception as e:
        print('com2tcp: ', e)

sock = socket.socket()
sock.bind(('', 9090))

while True:
    thread = None
    conn = None
    port = None

    try:
        sock.listen(1)
        conn, addr = sock.accept()
        print('Got connection from ', addr)

        port = serial.Serial()
        port.port = '/dev/ttyUSB0'
        port.baudrate = 115200
        port.timeout = 0.1
        port.setDTR(True)
        port.open()

        # reset arduino
        port.setDTR(False)
        sleep(.1)
        port.flushInput()
        port.setDTR(True)
        sleep(.1)

        thWorkingFlag = True
        thread = Thread(target=com2tcpThread, args=(conn,port))
        thread.start()

        # tcp to com data transfer loop
        while True:
            data = conn.recv(1024)
            #print("TCP>COM: ", data)
            if not data:
                break
            port.write(data)

    except Exception as e:
        print('tcp2com: ', e)

    finally:
        print('Disconnected')
        thWorkingFlag = False
        if thread:
            thread.join()
        if port:
            port.close()
        if conn:
            conn.close()

