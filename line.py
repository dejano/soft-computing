import cv2
import numpy as np
from shapely.geometry import LineString

from intersectionutil import pnt2line


class LineType:
    def __init__(self):
        pass

    green = {"operation": "-", "lower": np.array([55, 150, 100]), "upper": np.array([70, 255, 255])}
    blue = {"operation": "+", "lower": np.array([100, 150, 100]), "upper": np.array([140, 255, 255])}


class Line:

    def __init__(self, image, line_type):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, line_type.get('lower'), line_type.get('upper'))
        lines = cv2.HoughLinesP(mask, 1, np.pi / 180, 200, maxLineGap=20)
        if lines is None or len(lines) == 0:
            raise ValueError('Unable to locate lines')

        self.x1, self.y1, self.x2, self.y2 = np.min(lines, axis=0)[0]
        self.line_string = LineString([(self.x1, self.y1), (self.x2, self.y2)])
        self.operation = line_type.get("operation")

    def intersects(self, number):
        dist, r = pnt2line([number.center_x, number.center_y], [self.x1, self.y1], [self.x2, self.y2])
        return r > 0 and dist < 9
