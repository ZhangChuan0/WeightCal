import cv2

def main(cam_index=0):
	"""打开摄像头并实时预览画面。按 'q' 键退出。"""
	cap = cv2.VideoCapture(cam_index)
	if not cap.isOpened():
		print(f"无法打开摄像头 {cam_index}")
		return

	cv2.namedWindow('Camera', cv2.WINDOW_NORMAL)
	while True:
		ret, frame = cap.read()
		if not ret:
			print('读取帧失败')
			break

		cv2.imshow('Camera', frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()
# 改进，增加一个关闭的方法，不要无限循环

if __name__ == '__main__':
	main()
