import cv2
import numpy as np

from point import Point


class LineType:
    def __init__(self):
        pass

    green = {"operation": "+", "lower": np.array([55, 150, 100]), "upper": np.array([70, 255, 255])}
    blue = {"operation": "-", "lower": np.array([100, 150, 100]), "upper": np.array([140, 255, 255])}


class Line:

    def __init__(self, image, line_type):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, line_type.get('lower'), line_type.get('upper'))
        lines = cv2.HoughLinesP(mask, 1, np.pi / 180, 200, maxLineGap=20)
        if lines is None or len(lines) == 0:
            raise ValueError('Unable to locate lines')

        self.operation = line_type.get("operation")
        x1, y1, x2, y2 = np.min(lines, axis=0)[0]
        self.a = Point(x1, y1)
        self.b = Point(x2, y2)
