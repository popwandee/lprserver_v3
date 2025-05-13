import cv2
import time

cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(f'video_{time.time()}.avi', fourcc, 20.0, (640, 480))

while True:
	ret, frame = cap.read()
	if ret:
		out.write(frame)
		cv2.imshow('Recording...', frame)
		
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

cap.release()
out.release()
cv2.destroyAllWindows()
