#!/usr/bin/env python3
import socket
import time
from multiprocessing import Process

from client import get_remote_ip

#define address & buffer size
HOST = ""
PORT = 8001
BUFFER_SIZE = 1024

def main():
    host = 'www.google.com'
    port = 80

    # acting as a server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_s:
        print("Starting proxy server")
        proxy_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy_s.bind((HOST, PORT))
        proxy_s.listen(1)

        # acting as a client so that we can forward the request
        # from our client to the main server
        while True:
            conn, addr = proxy_s.accept()
            print("Connected by", addr)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_e:
                print("Connecting to Google")
                remote_ip = get_remote_ip(host)

                proxy_e.connect((remote_ip, port))
                p = Process(target=handle_proxy, args=(conn, proxy_e))
                p.daemon = True
                p.start()
                print("Started process", p)

def handle_proxy(conn, proxy_e):
        # receive data from client
        send_full_data = conn.recv(BUFFER_SIZE)

        # send to main server
        print(f"Sending recieved data {send_full_data} to Google")
        proxy_e.sendall(send_full_data)

        proxy_e.shutdown(socket.SHUT_WR)

        # recieve data from main server
        data = proxy_e.recv(BUFFER_SIZE)

        # send to client
        print(f"Sending recieved data {data} to client")
        conn.send(data)
        conn.close()


if __name__ == "__main__":
    main()
