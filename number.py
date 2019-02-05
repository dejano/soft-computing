import cv2


class Number:
    NUMBER_DIMENSIONS = 28

    def __init__(self, contour, frame):
        self.contour = contour
        self.used = False
        self.calculate(contour, frame)

    def calculate(self, contour, frame):
        self.moments = cv2.moments(contour)
        self.center_x = int(self.moments["m10"] / self.moments["m00"])
        self.center_y = int(self.moments["m01"] / self.moments["m00"])
        self.x1 = self.center_x - (self.NUMBER_DIMENSIONS / 2)
        self.y1 = self.center_y - (self.NUMBER_DIMENSIONS / 2)
        self.x2 = self.center_x + (self.NUMBER_DIMENSIONS / 2)
        self.y2 = self.center_y + (self.NUMBER_DIMENSIONS / 2)
        # TODO 1
        # Don't resize rectangle like this but instead expand with black pixels
        self.image = frame[self.y1: self.y2, self.x1: self.x2]

    def prepare_for_neural_network(self):
        return self.image.reshape(1, self.NUMBER_DIMENSIONS * self.NUMBER_DIMENSIONS)
