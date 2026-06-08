import cv2
import time
import threading


class CameraPreview:
    """
    带性能检测的摄像头预览类：
    - 实时显示 FPS
    - 可选显示 Canny 边缘检测画面（按 'm' 键切换模式）
    - 按 'q' 或调用 stop() 退出
    """

    def __init__(self, cam_index=0, width=640, height=480, api_preference=None):
        self.cam_index = cam_index
        self.width = width
        self.height = height
        # 自动选择后端加速打开
        if api_preference is None:
            import platform
            api_preference = cv2.CAP_DSHOW if platform.system() == 'Windows' else cv2.CAP_ANY
        self.api_preference = api_preference

        self.cap = None
        self._running = False
        self._stop_event = threading.Event()
        self._mode = 0  # 0: 原始画面, 1: Canny 边缘检测

    def start(self):
        if self._running:
            print("已经在运行中")
            return

        self.cap = cv2.VideoCapture(self.cam_index, self.api_preference)
        if not self.cap.isOpened():
            print(f"无法打开摄像头 {self.cam_index}")
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 减小缓冲

        self._running = True
        self._stop_event.clear()
        cv2.namedWindow('Camera Performance Test', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Camera Performance Test', self.width, self.height)

        # FPS 计算变量（修复版）
        fps = 0.0
        fps_start_time = time.time()
        fps_frame_count = 0

        print("性能测试开始。按 'm' 切换模式，按 'q' 退出。")
        try:
            while self._running and not self._stop_event.is_set():
                ret, frame = self.cap.read()
                if not ret:
                    print("读取帧失败")
                    break

                # ---- 简单检测算法 ----
                if self._mode == 1:
                    # 灰度 + 高斯模糊 + Canny 边缘检测
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                    edges = cv2.Canny(blurred, 50, 150)
                    # 转为三通道以便显示
                    display_frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                else:
                    display_frame = frame.copy()
                # ---- 检测算法结束 ----

                # 计算 FPS（每秒更新一次）
                fps_frame_count += 1
                elapsed_time = time.time() - fps_start_time
                if elapsed_time >= 1.0:
                    fps = fps_frame_count / elapsed_time
                    fps_frame_count = 0
                    fps_start_time = time.time()

                # 将 FPS 和模式信息叠加到画面上
                mode_text = "Original" if self._mode == 0 else "Canny Edges"
                cv2.putText(display_frame, f"Mode: {mode_text} | FPS: {fps:.1f}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                cv2.imshow('Camera Performance Test', display_frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.stop()
                    break
                elif key == ord('m'):
                    self._mode = 1 - self._mode
                    print(f"切换到: {'Canny 边缘检测' if self._mode == 1 else '原始画面'}")
        finally:
            self._cleanup()

    def stop(self):
        if not self._running:
            return
        self._running = False
        self._stop_event.set()
        cv2.destroyAllWindows()

    def _cleanup(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        self._running = False
        print("测试结束，摄像头已关闭")


def main():
    """测试不同分辨率的摄像头性能"""
    # 可以尝试不同分辨率测试性能
    resolutions = [
        (640, 480),  # 标准 VGA
        (1920, 1080), # Full HqD (如果摄像头支持)
        (2560,1440)

    ]

    for width, height in resolutions:
        print(f"\n--- 测试分辨率: {width}x{height} ---")
        preview = CameraPreview(cam_index=0, width=width, height=height)
        try:
            preview.start()
            # 按 'q' 键退出当前分辨率测试
        except KeyboardInterrupt:
            preview.stop()
            break

        # 简单延时，让用户看到 FPS 数据
        time.sleep(1)

    print("\n所有测试完成")


if __name__ == '__main__':
    main()