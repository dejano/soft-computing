from scipy.spatial import distance


# https://www.pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/
# So called "centroid tracker"
class Tracker:
    tracked = []
    potential_overlap = []

    def __init__(self):
        pass

    def update(self, numbers, frame_index, line, line1, frame=None):
        if len(self.tracked) == 0:
            self.register(numbers)
            return self.tracked

        for number in numbers:
            ok, closest = self.find_closest(number, self.tracked, 15)
            if ok:
                closest.update(number)
                continue

            if self.is_intersecting(number, line, line1):
                # print 'number %s intersecting' % number
                continue

            # Maybe overlap number revealed
            ok, closest = self.find_closest(number, self.potential_overlap)
            if ok:
                self.deregister_potential(closest)
                number.overlap = True
                number.overlap_number = closest

                print 'REMOVE OVERLAPING AND REPLACE WITH NUMBER %s' % number

            self.register([number])

        # for number in self.tracked:
        #     if number.overlap:
        #         cv2.rectangle(frame, (number.x1, number.y1), (number.x2, number.y2), (255, 0, 0), 2)
        # remove tracked objects if they didn't move in past N frames (N could be ~5?)
        for num in self.tracked:
            if abs(frame_index - num.frame_index) > 50:
                self.deregister(num)

        return self.tracked

    def register(self, number):
        self.tracked.extend(number)
        pass

    def deregister_potential(self, number):
        self.potential_overlap.remove(number)

    def deregister(self, number):
        self.tracked.remove(number)

    def update_potential_overlap(self, numbers, frame_index, line, line1):
        # if len(self.potential_overlap) == 0:
        #     self.potential_overlap.extend(numbers)

        for number in numbers:
            if line.intersects(number) or line1.intersects(number):
                continue

            ok, closest = self.find_closest(number, self.potential_overlap, 50)
            if ok:
                closest.update(number)
                continue

            self.potential_overlap.append(number)

        # remove tracked objects if they didn't move in past N frames (N could be ~5?)
        for overlap in self.potential_overlap:
            print '%d, %d' % (overlap.frame_index, frame_index)
            if frame_index - overlap.frame_index > 100:
                print 'deregister'
                self.deregister_potential(overlap)

        print 'potential overlap parts (%d)' % (len(self.potential_overlap))
        return self.potential_overlap

    def find_closest(self, number, tracked, max_distance=15):
        numbers_with_distance = {}
        for tracked_number in tracked:
            numbers_with_distance[tracked_number] = distance.euclidean([number.center_x, number.center_y],
                                                                       [tracked_number.center_x,
                                                                        tracked_number.center_y])

        if len(numbers_with_distance) == 0:
            return False, None

        closest_number = min(numbers_with_distance.iterkeys(), key=(lambda key: numbers_with_distance[key]))
        if numbers_with_distance[closest_number] > max_distance:
            return False, None
        return True, closest_number

    def is_intersecting(self, number, line, line1):
        return line.intersects(number) or line1.intersects(number)
