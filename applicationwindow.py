import PIL.Image
import PIL.ImageTk
from Tkinter import *
from scipy.spatial import distance
from shapely.geometry import LineString
from shapely.geometry import box

from imageutil import *
from line import Line
from neuralnetworkutil import *
from number import Number
from videoutil import VideoUtil


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
        self.lines = []
        self.lines.append(self.addition_line)
        self.lines.append(self.subtraction_line)
        self.sum = 0

        self.numbers = []
        self.photo = None
        self.current_frame_index = 0
        self.render()

    def render(self):
        if self.current_frame_index == len(frames):
            return

        original_frame = frames[self.current_frame_index]
        previous_frame = None if self.current_frame_index - 1 < 0 else frames[self.current_frame_index - 1]
        frame = np.copy(original_frame)

        to_delete = []
        for num in self.numbers:
            if num.y2 > 477 or num.x2 >= 637:
                to_delete.append(num)

        for delete in to_delete:
            self.numbers.remove(delete)

        # Contours
        binary_frame = ImageUtil.to_binary(original_frame)
        contours, hierarchy = cv2.findContours(binary_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            # todo add area as well
            if 3 <= w <= 40 and h >= 10:
                number = Number(contour, binary_frame)
                # TODO 2
                # Handle when intersection happens with line
                # Something is wrong here, sometimes shape is (28, 27). Prolly related to todo 1
                if number.image.shape != (28, 28):
                    continue

                closest = self.find_closest(number, self.numbers)
                if closest is False:
                    closest = number
                    self.numbers.append(closest)

                closest.calculate(contour, binary_frame)

                # Intersection
                rectangle = box(number.x1, number.y1, number.x2, number.y2)
                subtraction = LineString([(self.subtraction_line.a.x, self.subtraction_line.a.y),
                                          (self.subtraction_line.b.x, self.subtraction_line.b.y)])
                addition = LineString([(self.addition_line.a.x, self.addition_line.a.y),
                                       (self.addition_line.b.x, self.addition_line.b.y)])

                # # Prediction
                # prediction = model.predict(number.prepare_for_neural_network(), verbose=0)
                # predicted_number = str(np.argmax(prediction))
                # # cv2.putText(frame, predicted_number, (cX - 25, cY - 15), cv2.FONT_HERSHEY_SIMPLEX, 1,
                # #             (0, 255, 255), 1)

                prediction = model.predict(closest.prepare_for_neural_network(), verbose=0)
                predicted_number = str(np.argmax(prediction))
                cv2.putText(frame, predicted_number, (closest.center_x - 25, closest.center_y - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 255), 1)
                if rectangle.intersects(subtraction) and closest.used is False:
                    self.sum = self.sum - int(predicted_number)
                    closest.used = True
                    print 'subtraction with %s' % predicted_number

                if rectangle.intersects(addition) and closest.used is False:
                    self.sum = self.sum + int(predicted_number)
                    closest.used = True
                    print 'addition with %s' % predicted_number

        for number in self.numbers:
            self.render_number(frame, number)

        self.draw_frame_meta_data(frame)

        self.draw_lines(frame)

        self.draw_sum(frame)

        self.render_frame(frame)
        self.current_frame_index = self.current_frame_index + 1
        self.after(25, self.render)

    def render_number(self, frame, number):
        # cv2.circle(frame, (cX, cY), 14, (255, 0, 0), 1)
        cv2.rectangle(frame, (number.x1, number.y1), (number.x2, number.y2), (0, 255, 0), 1)

    def draw_frame_meta_data(self, frame):
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottom_left_corner_of_text = (20, 20)
        font_scale = 0.5
        font_color = (255, 255, 255)
        line_type = 1
        # fps = 40
        number_of_frames = len(frames)
        cv2.putText(frame, "{}/{}".format(self.current_frame_index + 1, number_of_frames),
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
        line_type = 1
        # fps = 40
        number_of_frames = len(frames)
        cv2.putText(frame, "%d" % self.sum,
                    right_top_corner,
                    font,
                    font_scale,
                    font_color,
                    line_type)

    def draw_lines(self, frame):
        pass
        # draw lines
        # for line in self.lines:
        #     x1, y1, x2, y2 = line
        #     cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)

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
            return False
        return closest_number


class Menu(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid_columnconfigure(0, weight=1)

        self.first = Button(self, text="Grayscale", command=self.gray_scale)
        self.first.grid(row=0, column=0, sticky=W + E, padx=20, pady=5)

        self.second = Button(self, text="second", command=self.command)
        self.second.grid(row=1, column=0, sticky=W + E, padx=20, pady=5)

        self.grid(row=0, column=0, rowspan=4, sticky=N + W + E + S)

    def command(self):
        print "do command"

    def gray_scale(self):
        print "asd"


class ApplicationWindow(Frame):
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


# train_and_persist()
model = load()
frames = VideoUtil.load_frames('./resources/video-0.avi')
#
root = Tk()
window = ApplicationWindow(master=root)
window.mainloop()
# window.destroy()
# root.destroy()
