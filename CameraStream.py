import cv2 #opencv stand for open source computer vision
import numpy as np
import socket
from struct import unpack ,pack
from math import ceil


class CameraStream():
    """
    object which used to stream video camera
    default port = 5000
    Cam num = 0 as its the default of any pc webcam
    """
    def __init__(self,issender = False,port=5000,ipaddress = "", camNum = 0):
        self.MAX_DGRAM = 65472
        #capture webcam stream if you are the send
        if issender:
            self.cam = cv2.VideoCapture(camNum)
            self.face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml") # load facial detection model if you are the sender
        #create UDP socket with selected ip and port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #listen on the selected port if you are the receiver
        if not issender:
            self.s.bind((ipaddress, port))
        self.address = ipaddress
        self.issender = issender
        self.PORT = port
        self.dat = b''
        #clean old data from buffer when starting a new stream
        if not issender:
            self.dump_buffer()
            print("Security camera : connected succefully")

    def dump_buffer(self):
        """
        Function that dumps old data from buffer once new connection is established
        """
        while True:
            seg, addr = self.s.recvfrom(self.MAX_DGRAM)
            if unpack("B", seg[0:1])[0] == 1:
                break

    def read(self):
        """
        Function that receives data from the stream if you are the receiver, decompress it, decode it and return the frames
        """
        if self.issender:
            return
        seg, addr = self.s.recvfrom(self.MAX_DGRAM)
        while unpack("B", seg[0:1])[0] > 1:
            self.dat += seg[1:]
            seg, addr = self.s.recvfrom(self.MAX_DGRAM)
            
        self.dat += seg[1:]
        #decode the data to get the frame
        img = cv2.imdecode(np.fromstring(self.dat, dtype=np.uint8), 1)
        img = cv2.resize(img, (1480, 820))
        self.dat = b''
        return img

    def __del__(self):
        if self.issender:
	        self.cam.release()
        self.s.close()
	
    def send_Frame(self):
        """
        Function that applies facial detection to the frame, encode it and compress it then send it over udp session
        """
        #check if you are the sender
        if not self.issender:
            return
        #check if the webcam stream captured is working
        if not self.cam.isOpened():
            return
        #read image
        _, img = self.cam.read()
		#apply facial detection using haars facial detection cascade classifier
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        #draw detected faces on the frame
        for (x , y, w, h) in faces:
        	cv2.rectangle(img, (x ,y), (x + w , y + h), (0,0,0), 3)
        #compress the frame
        compress_img = cv2.imencode(".jpg", img=img)[1]
        dat = compress_img.tostring()
        size = len(dat)
        num_of_datagrams = ceil(size/(self.MAX_DGRAM))
        array_pos_start = 0
        #send data as a stream of data grams
        while num_of_datagrams:
            array_pos_end = min(size, array_pos_start + self.MAX_DGRAM)
            self.s.sendto(
                        pack("B", num_of_datagrams) +
                        dat[array_pos_start:array_pos_end], 
                        (self.address, self.PORT))
            array_pos_start = array_pos_end
            num_of_datagrams -= 1