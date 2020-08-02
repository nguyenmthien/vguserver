#!/usr/bin/env python3
# *_* coding: utf-8 *_*

"""TCP Server library"""

import multiprocessing
import queue
import socket
import select
import time
import getmac

class LocalServer(object):
    """This class is created for usage in multiprocessing of the main program"""
    def __init__(self, tcp_queue: multiprocessing.Queue, port: int):
        self.queue = tcp_queue
        self.server = tcp_server(get_ip(), port)
        self.thermal_update_interval = 300
        self.allow_new_client_flag = False
        self.new_client_name = ""

    def server_loop(self):
        """TCP server main loop, similiar with the code in if name == main"""
        self.server.update_sockets_list()
        try:
            self.server.check_read_sockets()
        except new_connection as msg:
            print(msg, end="")
            try:
                self.server.new_socket_handler(self.thermal_update_interval)
            except address_does_not_exist as arg:
                if allow_new_client_flag:
                    self.server.create_new_socket(arg.args[0], arg.args[1], self.new_client_name)
                    print(f"[TCP] Created new socket")
                    print(f"ID: {self.new_client_name}, address {arg.args[1][0]}")
                    allow_new_client_flag = False
                return
            return

        message_list = self.server.recv_all()

        if message_list != []:
            print(message_list)
            for dictionary in message_list:
                print(dictionary['ID'], dictionary['Temp'], dictionary['Humid'])

    def consumer(self):
        """multiprocessing queue consumer"""
        try:
            msg = self.queue.get_nowait()
            self.allow_new_client_flag = True
            if msg[0] == "sleep_interval":
                self.thermal_update_interval = msg[1]
            if msg[0] == "change":
                self.server.change_client_name(msg[1], msg[2])
            if msg[0] == "remove":
                self.server.remove_client(msg[1])
            if msg[0] == "add":
                self.allow_new_client_flag = True
                self.new_client_name = msg[1]
        except queue.Empty:
            pass

    def program(self):
        """Complete program"""
        while True:
            self.consumer()
            self.server_loop()

class new_connection(Exception):
    """TCP: New connection detected"""

class address_does_not_exist(Exception):
    """TCP: Address does exist in dictionary"""
    def __init__(self, *args):
        super().__init__(*args)

def get_ip():
    """Find local IP of the current network interface, avoid 127.0.0.1"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        sock.connect(('10.255.255.255', 1))
        ip_addr = sock.getsockname()[0]
    except:
        ip_addr = '127.0.0.1'
    finally:
        sock.close()
    return ip_addr


def receive_message(client_socket):
    """Recive message from client_socket"""
    try:
        mess = client_socket.recv(1024)
        if not len(mess):
            return False
        elif (len(mess) <= 2) or (mess == '\r\n'):
            return
        return mess

    except:
        return False

class tcp_server:
    """Create a TCP/IP Server"""
    def __init__(self, IP, PORT):
        self.ip_addr = IP
        self.port = PORT
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setblocking(0)
        self.server_socket.bind((self.ip_addr, self.port))
        self.server_socket.listen(5)
        self.sockets_list = [self.server_socket]
        self.socket_list_by_mac = {}
        self.name_dict = {}
        self.msg = {}
        self.read_sockets = []
        self.write_sockets = []
        self.exception_sockets = []
        self.mac_list = []


    def update_sockets_list(self):
        """Update sockets list to read_sockets, write_sockets, exception_sockets"""
        self.read_sockets, self.write_sockets, self.exception_sockets = select.select(
            self.sockets_list, self.sockets_list, [], 0)

    def check_read_sockets(self):
        """Handle new connection after updating socket lists"""
        for notified_socket in self.read_sockets:
            if notified_socket == self.server_socket:
                raise new_connection('New Connection')

    def new_socket_handler(self, sleeptime):
        """New socket handler"""
        client_socket, client_address = self.server_socket.accept()
        client_mac = getmac.get_mac_address(ip=client_address[0], network_request=True)
        client_socket.setblocking(0)
        self.sockets_list.append(client_socket)
        client_socket.send(bytes([sleeptime]))
        logic = True
        for mac in self.mac_list:
            if mac == client_mac:
                logic = False
                try:
                    self.sockets_list.remove(self.socket_list_by_mac[mac])
                except ValueError:
                    pass
                self.socket_list_by_mac[mac] = client_socket
                return

        if logic:
            raise address_does_not_exist(client_socket, client_address)

    def create_new_socket(self, client_socket, client_address, name):
        """Create new TCP socket"""
        client_mac = getmac.get_mac_address(ip=client_address[0], network_request=True)
        self.name_dict[client_mac] = name
        self.mac_list.append(client_mac)
        self.socket_list_by_mac[client_mac] = client_socket

    def send_all(self, mess):
        """THIS FUNCTION IS WRONG"""
        for key in self.name_dict:
            if  (self.name_dict[key] != 'UPS') and (self.name_dict[key] != 'AC') and (key != self.server_socket):
                key.send(mess.encode('utf-8'))

    def therm_parsing(self, mess):
        """Split a message from a client into 2 variables by spaces"""
        mess_list = mess.split()
        if len(mess_list) == 2:
            return mess_list[0], mess_list[1]

    def recv_all(self):
        """Receive all messages from clients and parse as therm"""
        self.update_sockets_list()
        return_list = []
        for notified_socket in self.read_sockets:
            if notified_socket != self.server_socket:
                client_mac = getmac.get_mac_address(ip=notified_socket.getpeername()[0])
                if self.name_dict[client_mac] != 'UPS':
                    mess_dict = {'ID':self.name_dict[client_mac]}
                    message = receive_message(notified_socket)
                    if message is False:
                        self.sockets_list.remove(notified_socket)
                        continue
                    elif message is None:
                        continue
                    message = message.strip()
                    try:
                        temp, humid = self.therm_parsing(message)
                        mess_dict['Temp'] = temp.decode('utf-8')
                        mess_dict['Humid'] = humid.decode('utf-8')
                        return_list.append(mess_dict)
                    except TypeError:
                        return_list = []

        return return_list

    def remove_client(self, name):
        """Remove client form lists by name"""
        client_mac = self.mac_list[0]
        for key, value in self.name_dict.items():
            if name == value:
                client_mac = key
                break
        self.name_dict.pop(client_mac, None)
        self.mac_list.remove(client_mac)
        self.socket_list_by_mac.pop(client_mac, None)

    def change_client_name(self, name_old, name_new):
        """Rename a client from name_old to name_new"""
        client_mac = self.mac_list[0]
        for key, value in self.name_dict.items():
            if name_old == value:
                client_mac = key
                break
        self.name_dict[client_mac] = name_new

    def send_ac_control(self, message):
        """Send message to the air conditioner controlling client"""
        client_mac = self.mac_list[0]
        for key, value in self.name_dict.items():
            if "AC" == value:
                client_mac = key
                break
        client_socket = self.socket_list_by_mac[client_mac]
        client_socket.send(message.encode(ascii))

if __name__ == "__main__":
    def main():
        vguserver.update_sockets_list()
        try:
            vguserver.check_read_sockets()
        except new_connection as msg:
            print(msg, end='')
            try:
                vguserver.new_socket_handler(100)
            except address_does_not_exist as arg:
                name = input("Enter name: ")
                vguserver.create_new_socket(arg.args[0], arg.args[1], name)
                print(f"Created socket with name {name}, address {arg.args[1][0]}")
                return
            return

        message_list = vguserver.recv_all()

        if message_list != []:
            print(message_list)
            for dictionary in message_list:
                print(dictionary['ID'], dictionary['Temp'], dictionary['Humid'])

    vguserver = tcp_server(get_ip(), 2033)
    print(f"Started TCP server at {get_ip()}:2033")
    last_t = time.time()


    while True:
        main()
