from CameraStream import CameraStream
from keyboard import is_pressed

Camera = CameraStream(ipaddress="192.168.1.255",issender= True) #send camera stream over the broad cast ip of home internal network

while True:
	Camera.send_Frame()
	if is_pressed('q'):
		break
	