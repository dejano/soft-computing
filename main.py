import cv2
import numpy as np

from imageutil import LineMask, ImageUtil
from line import Line
from neuralnetworkutil import *
from number import Number
from tracker import Tracker
from videoutil import VideoUtil


def process_video(name):
    frames = VideoUtil.load_frames('./resources/%s' % name)
    first_frame = frames[0]
    addition_line = Line(first_frame, LineMask.blue)
    subtraction_line = Line(first_frame, LineMask.green)
    total = 0
    tracker = Tracker()
    for current_frame_index, frame in enumerate(frames):
        binary_frame = ImageUtil.to_binary(frame)
        contours, hierarchy = cv2.findContours(binary_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        numbers = []
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)

            if not (3 <= w <= 40 and h >= 10):
                continue

            number = Number(contour, binary_frame, current_frame_index)
            if number.image.shape != (28, 28):
                continue

            numbers.append(number)
        numbers = tracker.update(numbers, current_frame_index, addition_line, subtraction_line,
                                 frame)
        for number in numbers:

            if addition_line.intersects(number) and number.addition is False:
                number.prediction = str(np.argmax(model.predict(number.prepare_for_neural_network(), verbose=0)))
                total += int(number.prediction)
                number.addition = True
            if subtraction_line.intersects(number) and number.subtraction is False:
                number.prediction = str(np.argmax(model.predict(number.prepare_for_neural_network(), verbose=0)))
                total -= int(number.prediction)
                number.subtraction = True

    return total


model = load('conv-60-e')
# Output file
outputFile = 'out.txt'
out = open(outputFile, 'w')
out.write('RA 142/2011 Dejan Osmanovic\n')
out.write('file\tsum\n')

for video_file_index in range(0, 10):
    video_file_name = 'video-%d.avi' % video_file_index
    sum = process_video(video_file_name)
    print '%s: %d' % (video_file_name, sum)
    out.write('%s\t%d\n' % (video_file_name, sum))

out.close()
