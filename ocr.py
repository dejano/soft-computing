import cv2


class Ocr:
    def __init__(self):
        pass

    def recognize(self, contour):
        x, y, w, h = cv2.boundingRect(contour)
        if not self.looks_like_number(h, w):
            pass
        number = Number(contour, binary_frame)
        number = self.tracker.update(number,, self.addition_line, self.subtraction_line
        number.prediction = str(np.argmax(model.predict(number.prepare_for_neural_network(), verbose=0)))
        # print 'Predicted %s - %d' % (number.prediction, area)

        if self.addition_line.intersects(number) and number.addition is False:
            self.sum += int(number.prediction)
        print number.addition
        number.addition = True
        print 'addition with %s' % number.prediction

        if self.subtraction_line.intersects(number) and number.subtraction is False:
            self.sum -= int(number.prediction)
        number.subtraction = True
        print 'subtraction with %s' % number.prediction
        self.render_number(frame, number)

    def looks_like_number(self, h, w):
        return 3 <= w <= 40 and h >= 10
