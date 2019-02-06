import PIL.Image
import PIL.ImageTk
from Tkinter import *
from scipy.spatial import distance

from imageutil import *
from line import Line
from neuralnetworkutil import *
from number import Number
from tracker import Tracker


class Workspace(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self["bg"] = "white"
        first_frame = frames[0]
        self.height, self.width, no_channels = first_frame.shape
        self.canvas = Canvas(self, width=self.width * 2, height=self.height * 2)
        self.canvas.grid(row=0, column=1, sticky=N + W + E + S)
        self.grid(row=0, column=1, sticky=N + W + E + S)

        # Lines
        self.addition_line = Line(first_frame, LineMask.blue)
        self.subtraction_line = Line(first_frame, LineMask.green)
        self.sum = 0
        self.tracker = Tracker()

        self.numbers = []
        self.photo = None
        # self.current_frame_index = 430
        self.current_frame_index = 0
        self.render()

    def render(self):
        if self.current_frame_index == len(frames):
            return

        if not ApplicationWindow.playing:
            self.after(ApplicationWindow.frames_per_second, self.render)
            return

        original_frame = frames[self.current_frame_index]
        previous_frame = None if self.current_frame_index - 1 < 0 else frames[self.current_frame_index - 1]
        frame = np.copy(original_frame)

        for num in self.numbers:
            if num.y2 > 477 or num.x2 >= 637:
                num.out_of_screen = True

        # Contours
        binary_frame = ImageUtil.to_binary(original_frame)
        contours, hierarchy = cv2.findContours(binary_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        numbers = []
        potential_overlap = []
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)

            if not (3 <= w <= 40 and h >= 10):
                # print 'NOT SUITABLE [%d %d]' % (w, h)
                n = Number(contour, binary_frame, self.current_frame_index)
                potential_overlap.append(n)
                continue

            n = Number(contour, binary_frame, self.current_frame_index)
            if n.image.shape != (28, 28):
                continue

            n.prediction = str(np.argmax(model.predict(n.prepare_for_neural_network(), verbose=0)))
            numbers.append(n)
        #
        # potential_overlap = self.tracker.update_potential_overlap(potential_overlap, self.current_frame_index,
        #                                                           self.addition_line,
        #                                                           self.subtraction_line)
        numbers = self.tracker.update(numbers, self.current_frame_index, self.addition_line, self.subtraction_line,
                                      frame)
        # print numbers

        for overlap in potential_overlap:
            self.render_number(frame, overlap, (0, 255, 0))

        for number in numbers:

            # print 'Predicted %s - %d' % (number.prediction, area)

            if self.addition_line.intersects(number) and number.addition is False:
                self.sum += int(number.prediction)
                print number.addition
                number.addition = True
                print 'addition with %s' % number.prediction
                print 'sum %d' % self.sum
            if self.subtraction_line.intersects(number) and number.subtraction is False:
                self.sum -= int(number.prediction)
                number.subtraction = True
                print 'subtraction with %s' % number.prediction
                print 'sum %d' % self.sum
            self.render_number(binary_frame, number)

        # for number in self.numbers:

        self.draw_frame_meta_data(binary_frame)
        self.draw_sum(binary_frame)

        self.render_frame(binary_frame)
        self.current_frame_index = self.current_frame_index + 1
        self.after(ApplicationWindow.frames_per_second, self.render)

    def render_number(self, frame, number, color=(255, 0, 0)):
        if number.out_of_screen:
            pass
        # cv2.circle(frame, (cX, cY), 14, (255, 0, 0), 1)
        cv2.putText(frame, number.prediction, (number.center_x - 25, number.center_y - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 255), 1)
        cv2.rectangle(frame, (number.x1, number.y1), (number.x2, number.y2), color, 1)

    def draw_frame_meta_data(self, frame):
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottom_left_corner_of_text = (20, 20)
        font_scale = 0.5
        font_color = (255, 255, 255)
        line_type = 1
        # fps = 40
        number_of_frames = len(frames)
        cv2.putText(frame, "{}/{} {}fps".format(self.current_frame_index + 1, number_of_frames,
                                                ApplicationWindow.frames_per_second),
                    bottom_left_corner_of_text,
                    font,
                    font_scale,
                    font_color,
                    line_type)

    def draw_sum(self, frame):
        font = cv2.FONT_HERSHEY_SIMPLEX
        right_top_corner = (600, 50)
        font_scale = 1
        font_color = (255, 50, 255)
        line_type = 2
        # fps = 40
        number_of_frames = len(frames)
        cv2.putText(frame, "%d" % self.sum,
                    right_top_corner,
                    font,
                    font_scale,
                    font_color,
                    line_type)

    def render_frame(self, frame):
        self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
        self.canvas.create_image(0, 0, image=self.photo, anchor=NW)

    def exists(self, number, previous_frame):
        if previous_frame is None:
            return False
        return True

    def find_closest(self, number, numbers):
        if len(numbers) == 0:
            return False

        numbers_with_distance = {}
        for n in numbers:
            numbers_with_distance[n] = distance.euclidean([number.center_x, number.center_y], [n.center_x, n.center_y])
        closest_number = min(numbers_with_distance.iterkeys(), key=(lambda key: numbers_with_distance[key]))
        if numbers_with_distance[closest_number] > 40:
            # if (closest_number.addition or closest_number.subtraction) and (
            #         numbers_with_distance[closest_number] > 5 or numbers_with_distance[closest_number] < 20):
            #     return closest_number
            return False
        return closest_number

    def first_time_shown(self, number, numbers):
        if len(numbers) == 0:
            return True

        numbers_with_distance = {}
        for n in numbers:
            numbers_with_distance[n] = distance.euclidean([number.center_x, number.center_y], [n.center_x, n.center_y])
        closest_number = min(numbers_with_distance.iterkeys(), key=(lambda key: numbers_with_distance[key]))
        if numbers_with_distance[closest_number] > 40:
            return False
        return closest_number


class Menu(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid_columnconfigure(0, weight=1)

        self.first = Button(self, text=">>", command=self.speed_up)
        self.first.grid(row=0, column=0, sticky=W + E, padx=20, pady=5)

        self.second = Button(self, text="<<", command=self.slow_down)
        self.second.grid(row=1, column=0, sticky=W + E, padx=20, pady=5)

        self.toggle_play_button = Button(self, text="toggle", command=self.toggle_play)
        self.toggle_play_button.grid(row=2, column=0, sticky=W + E, padx=20, pady=5)

        self.grid(row=0, column=0, rowspan=4, sticky=N + W + E + S)

    def slow_down(self):
        ApplicationWindow.frames_per_second = ApplicationWindow.frames_per_second + 50

    def toggle_play(self):
        ApplicationWindow.playing = not ApplicationWindow.playing

    def speed_up(self):
        ApplicationWindow.frames_per_second = ApplicationWindow.frames_per_second - 50


class ApplicationWindow(Frame):
    frames_per_second = 25
    playing = True

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self["bg"] = "yellow"
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.container = Frame(self, background="black")
        self.container.grid(columnspan=2, sticky=N + W + E + S)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=7)

        self.menu = Menu(self.container)
        self.workspace = Workspace(self.container)

        self.pack(fill=BOTH, expand=True)


train_and_persist()
# model = load('conv-60-e')
# frames = VideoUtil.load_frames('./resources/video-9.avi')
# #
# root = Tk()
# window = ApplicationWindow(master=root)
# window.mainloop()
# window.destroy()
# root.destroy()
