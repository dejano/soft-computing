import cv2
import numpy as np


class LineMask(object):
    green = {"lower": np.array([55, 150, 100]), "upper": np.array([70, 255, 255])}
    blue = {"lower": np.array([100, 150, 100]), "upper": np.array([140, 255, 255])}


class ImageUtil:

    def __init__(self):
        pass

    @staticmethod
    def gray_scale(img_rgb):
        return cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

    @staticmethod
    def find_lines(frame_bgr, line_type):
        # type: ([], {}) -> []
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, line_type.get('lower'), line_type.get('upper'))
        lines = cv2.HoughLinesP(mask, 1, np.pi / 180, 200, maxLineGap=20)
        if lines is None or len(lines) == 0:
            raise ValueError('Unable to locate lines using Hough')

        return np.min(lines, axis=0)[0]

    @staticmethod
    def to_binary(frame):
        return ImageUtil.try_hard_1(frame)

    @staticmethod
    def try_hard_1(frame):
        lower = np.array([200, 200, 200])
        upper = np.array([255, 255, 255])
        binary = cv2.inRange(frame, lower, upper)
        binary = cv2.blur(binary, ksize=(2, 2))
        binary = cv2.dilate(binary, (3, 3))
        return cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel=np.ones((2, 2), dtype=np.uint8), iterations=1)

    @staticmethod
    def try_hard_2(frame):
        frame_gs = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        tr, frame_bin = cv2.threshold(frame_gs, 160, 255,
                                      cv2.THRESH_BINARY)  # ret je izracunata vrednost praga, image_bin je binarna slika
        frame_bin = cv2.blur(frame_bin, ksize=(2, 2))
        return cv2.morphologyEx(frame_bin, cv2.MORPH_CLOSE, kernel=np.ones((2, 2), dtype=np.uint8), iterations=1)

    @staticmethod
    def try_hard_3(frame):
        lower = np.array([140, 140, 140])
        upper = np.array([255, 255, 255])
        shapeMask = cv2.inRange(frame, lower, upper)

        # shapeMask = cv2.blur(shapeMask, ksize=(2, 2))
        # shapeMask = cv2.dilate(shapeMask, (3, 3))
        # shapeMask = cv2.erode(shapeMask, (3, 3))
        # shapeMask = cv2.dilate(shapeMask, (3, 3))
        shapeMask = cv2.blur(shapeMask, ksize=(2, 2))
        return cv2.morphologyEx(shapeMask, cv2.MORPH_CLOSE, kernel=np.ones((2, 2), dtype=np.uint8), iterations=1)
