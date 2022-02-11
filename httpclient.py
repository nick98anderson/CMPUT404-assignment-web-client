#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
import urllib

DEFAULT_PORT = 80

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def connect(self, host, port):
        self.socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def get_headers(self,data):
        data = data.split("\r\n\r\n")
        header = data[0].split("\r\n",1)[1]
        return header

    def get_code(self, data):
        code = data.split()[1]
        return code

    def get_body(self, data):
        if data != None:
            return data.split('\r\n\r\n',2)[1]
        else:
            return None

    def sendall(self,data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')


    def parse_url(self,url):
        url = urllib.parse.urlparse(url)
        netloc = url.netloc
        path = url.path

        try: 
            host = netloc.split(':')[0]
            port = int(netloc.split(':')[1])
        except:
            host = netloc
            port = 80
        
        if path == "":
            path = "/"

        return host, path, port

    def GET(self, url, args=None):
        host,path,port = self.parse_url(url)

        request  = "GET "+ path + " HTTP/1.1\r\nHost:" + host + "\r\nConnection: close\r\n\r\n"
        self.connect(host, int(port))
        self.sendall(request)
        res = self.recvall(self.socket)
        print(res)
        self.close()

        header = self.get_headers(res)
        code = self.get_code(res)
        body = self.get_body(res)
        return HTTPResponse(int(code), body)



    def POST(self, url, args=None):
        host, path, port = self.parse_url(url) 
        content = ''

        if args == None:
            content_len = 0
        else:
            content = urllib.parse.urlencode(args)
            content_len = len(content)
        
        request = "POST "+ path + " HTTP/1.1\r\nHost:"+ host+ "\r\nConnection: close\r\nContent-Length:"+ str(content_len) + "\r\nContent-Type: application/x-www-form-urlencoded" + "\r\n\r\n" + content


        self.connect(host, int(port))
        self.sendall(request)
        res = self.recvall(self.socket)
        self.close()

        header = self.get_headers(res)
        code = self.get_code(res)
        body = self.get_body(res)

        print(res)
        return HTTPResponse(int(code), body)


    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
# Entry point supplied by Dr. Hindle
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))  