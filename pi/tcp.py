#!/usr/bin/env python3
# *_* coding: utf-8 *_*

"""TCP Server library"""

import socket
import select
import time
import getmac

class new_connection(Exception):
    """TCP: New connection detected"""
    pass

class address_does_not_exist(Exception):
    """TCP: Address does exist in dictionary"""
    def __init__(self, *args):
        super().__init__(*args)

def get_ip():
    """Find local IP of the current network interface, avoid 127.0.0.1"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def receive_message(client_socket):
    """Recive message from client_socket"""
    try:
        mess = client_socket.recv(1024)
        if (not len(mess)):
            return False
        elif (len(mess) <= 2) or (mess == '\r\n'):
            return
        return mess
    
    except:
        return False

class tcp_server:
    """Create a TCP/IP Server"""
    def __init__(self,IP,PORT):
        self.IP = IP
        self.PORT = PORT
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setblocking(0)
        self.server_socket.bind((self.IP, self.PORT))
        self.server_socket.listen(5)
        self.sockets_list = [self.server_socket]
        self.socket_list_by_mac = {}
        self.id_dict = {}
        self.msg = {}
        self.read_sockets = []
        self.write_sockets = []
        self.exception_sockets = []
        self.mac_list = []
        

    def update_sockets_list(self):
        """Update sockets list to read_sockets, write_sockets, exception_sockets"""
        self.read_sockets, self.write_sockets, self.exception_sockets = select.select(self.sockets_list, self.sockets_list, [], 0)

    def check_read_sockets(self):
        """Handle new connection after updating socket lists"""    
        for notified_socket in self.read_sockets:
            if notified_socket == self.server_socket:
                raise new_connection('New Connection')

    def new_socket_handler(self):
        """New socket handler"""
        client_socket, client_address = self.server_socket.accept()
        client_mac = getmac.get_mac_address(ip = client_address[0], network_request=True)
        client_socket.setblocking(0)
        self.sockets_list.append(client_socket)
        logic = True
        for mac in self.mac_list:
            if mac == client_mac:
                client_socket.send(b"Welcome back!")
                logic = False
                try:
                    self.sockets_list.remove(self.socket_list_by_mac[mac])
                except ValueError:
                    pass
                self.socket_list_by_mac[mac]=client_socket
                return

        if logic:
            raise address_does_not_exist(client_socket, client_address)

    def create_new_socket(self, client_socket, client_address, id):
        """Create new TCP socket"""
        client_mac = getmac.get_mac_address(ip = client_address[0], network_request=True)
        self.id_dict[client_mac] = id
        self.mac_list.append(client_mac)
        self.socket_list_by_mac[client_mac] = client_socket
    
    def send_all(self, mess):
        """THIS FUNCTION IS WRONG"""
        for key in self.id_dict:
            if  (self.id_dict[key] != 'UPS') and (self.id_dict[key] != 'AC') and (key != self.server_socket):
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
                client_mac = getmac.get_mac_address(ip = notified_socket.getpeername()[0])
                if self.id_dict[client_mac] != 'UPS':
                    mess_dict = {'ID':self.id_dict[client_mac]}
                    message = receive_message(notified_socket)
                    if message is False:
                        self.sockets_list.remove(notified_socket)
                        continue
                    elif message == None:
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