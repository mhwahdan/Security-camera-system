import cv2
from CameraStream import CameraStream

feedSize = (1480, 820)
cam = CameraStream(port=5000)
while 1:
	try:
		img = cam.read()
		fullSizeFeed = cv2.resize(img, feedSize)

		cv2.imshow("Camera feed", fullSizeFeed)
	except:
		continue
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
cv2.destroyAllWindows()

