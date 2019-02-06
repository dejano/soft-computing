import cv2


class Number:
    NUMBER_DIMENSIONS = 28

    def __init__(self, contour, frame, frame_index):
        self.contour = contour
        self.frame_index = frame_index
        self.overlap = False
        self.overlap_number = None
        self.prediction = None
        self.subtraction = False
        self.addition = False
        self.out_of_screen = False
        self.history = []
        self.moments = cv2.moments(contour)
        self.center_x = int(self.moments["m10"] / self.moments["m00"])
        self.center_y = int(self.moments["m01"] / self.moments["m00"])
        self.x1 = self.center_x - (self.NUMBER_DIMENSIONS / 2)
        self.y1 = self.center_y - (self.NUMBER_DIMENSIONS / 2)
        self.x2 = self.center_x + (self.NUMBER_DIMENSIONS / 2)
        self.y2 = self.center_y + (self.NUMBER_DIMENSIONS / 2)
        # TODO 1
        # Don't resize rectangle like this but instead expand with black pixels
        # self.image = cv2.resize(frame[self.y1: self.y2, self.x1: self.x2], (28, 28), interpolation=cv2.INTER_NEAREST)
        self.image = frame[self.y1: self.y2, self.x1: self.x2]

    def prepare_for_neural_network(self):
        region = cv2.resize(self.image, (28, 28))
        region = region.astype('float32')
        region /= 255
        region = region.reshape(1, 28, 28, 1)
        return region
        # return self.image.reshape(1, self.NUMBER_DIMENSIONS * self.NUMBER_DIMENSIONS)

    def update(self, number):
        self.contour = number.contour
        self.out_of_screen = number.out_of_screen
        self.frame_index = number.frame_index
        self.moments = number.moments
        self.center_x = number.center_x
        self.center_y = number.center_y
        self.x1 = number.x1
        self.y1 = number.y1
        self.x2 = number.x2
        self.y2 = number.y2
        self.image = number.image

    def __str__(self):
        return str(self.prediction)

    def __repr__(self):
        return self.__str__()
