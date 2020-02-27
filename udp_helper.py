'''
Based on https://github.com/ricardodeazambuja/BrianConnectUDP/blob/master/brian_multiprocess_udp.py
'''
import socket
import struct


class UDPHelper(object):
    def __init__(self):
        self._sockO = None
        self._sockI = None

    def __del__(self):
        if self._sockI:
            self._sockI.close()

    def init_sender(self, ip, port):
        self._sockO = socket.socket(socket.AF_INET,     # IP
                                    socket.SOCK_DGRAM)  # UDP
        self._IPO = ip
        self._PORTO = port

    def init_receiver(self, ip, port, clean=True):
        self._sockI = socket.socket(socket.AF_INET,     # IP
                                    socket.SOCK_DGRAM)  # UDP

        self._sockI.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Tells the OS that if someone else is using the PORT, it
        # can use the same PORT without any error/warning msg.
        # Actually this is useful because if you restart the simulation
        # the OS is not going to release the socket so fast and an error
        # could occur.

        self._sockI.bind((ip, port))  # Bind the socket to the ip/port

        self._buffersize = self._sockI.getsockopt(socket.SOL_SOCKET,
                                                  socket.SO_RCVBUF)

        while clean:
            print("Cleaning receiving buffer...")
            try:
                # buffer size is 1 byte, NON blocking.
                data = self._sockI.recv(1, socket.MSG_DONTWAIT)
            except IOError:  # The try and except are necessary because the recv raises a error when no data is received
                clean = False
        print("Cleaning receiving buffer...Done!")

        # Tells the system that the socket recv() method will DO block until a packet is received
        # self._sockI.setblocking(1)

    def send_msg(self, data):
        '''
        data: list/tuple of floats

        It will break the system if you try to send something too big...
        '''
        assert self._sockO, 'init_sender was not initialized!'

        data_header = struct.pack('>I', len(data))  # d=>8bytes
        data = data_header + \
            b''.join([struct.pack(">d", float(ji)) for ji in data])

        self._sockO.sendto(data, (self._IPO, self._PORTO))

    def recv_msg(self, timeout=None):
        '''Read the first received message and block if 
        nothing is available.
        '''
        assert self._sockI, 'init_receiver was not initialized!'

        if timeout:
            self._sockI.settimeout(timeout)

        try:
            msg = self._sockI.recv(self._buffersize)

        except socket.timeout:
            return None

        msglen = struct.unpack('>I', msg[:4])[0]

        return struct.unpack('>'+''.join(['d']*msglen), msg[4:])

    def recv_msg_nonblocking(self):
        '''Read the last received message, non-blocking.
        '''
        data = b''
        while True:
            try:
                packet = self._sockI.recv(self._buffersize,
                                          socket.MSG_DONTWAIT)
            except IOError:
                received_data = None
                while data:
                    msglen = struct.unpack('>I', data[:4])[0]
                    received_data = struct.unpack('>'+''.join(['d']*msglen), data[4:4+msglen*8])
                    data = data[4+msglen*8:]
                return received_data
            data += packet


if __name__ == '__main__':
    from udp_helper import *
    import time
    conn = UDPHelper()

    conn.init_sender('127.0.0.1', 8989)
    conn.init_receiver('127.0.0.1', 8989)

    msg1 = [1, 2, 3]
    msg2 = [4, 5, 6]
    print("First msg: {}".format(msg1))
    conn.send_msg(msg1)
    print("Second msg: {}".format(msg2))
    conn.send_msg(msg2)
    time.sleep(0.1)
    print("recv_msg: ", conn.recv_msg())

    print("First msg: {}".format(msg1))
    conn.send_msg(msg1)
    print("Second msg: {}".format(msg2))
    conn.send_msg(msg2)
    time.sleep(0.1)
    print("recv_msg_nonblocking: ", conn.recv_msg_nonblocking())
