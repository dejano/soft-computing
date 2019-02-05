import cv2


class VideoUtil:

    def __init__(self):
        pass

    @staticmethod
    def load_frames(video_path, color=None):
        cap = cv2.VideoCapture(video_path)
        frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if color is not None:
                frame = cv2.cvtColor(frame, color)

            frames.append(frame)
        cap.release()
        return frames
