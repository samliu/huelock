# @name               huelock.py
# @desc               Finds the center of colored masses (default
#                     calibrated to red) and returns it
# @initial_authors    Alexey Komissarouk <alexey86@gmail.com>
# @contributors       Sam Liu <sam@ambushnetworks.com>
# @copyright          MIT License / WTFPL License

# Notes
# -----
# Quadrants are as follows:
# Quad0 Quad1
# Quad2 Quad3
#
# Requires opencv 2.2+
# If you're unable to import cv (but rather, opencv),
# you have an old version of opencv.

import cv
import os
import sys


class ObjectDetector():

    def __init__(self, color_min=[100, 200, 95], color_max=[150, 255, 255]):
        # Default colors work to detect red-cup red!
        self.color_min = cv.Scalar(color_min[0], color_min[1], color_min[2])
        self.color_max = cv.Scalar(color_max[0], color_max[1], color_max[2])

    # Returns x, y of object
    def detect_object(self, image_filename):
        # Get the image from disk (TODO: get a stream instead)
        frame = cv.LoadImage(image_filename)
        frameHSV = cv.CreateImage(cv.GetSize(frame), 8, 3)
        cv.CvtColor(frame, frameHSV, cv.CV_RGB2HSV)

        # Generate new image object with only the detected color in white
        frame_threshed = cv.CreateImage(cv.GetSize(frameHSV), 8, 1)
        cv.InRangeS(frameHSV, self.color_min, self.color_max, frame_threshed)

        # Get and return coordinates of the center of the color mass
        center = self.find_center(frame_threshed, 0, 0, frame_threshed.width, frame_threshed.height)

        return center

    # Finds center of mass having defined color recursively
    def find_center(self, matrix, left, top, right, bot):
        # Separate thresholded matrix into four quadrants and find the darkest
        mid_x, mid_y = (int((left + right) / 2), int((top + bot) / 2))

        # Base case
        if (right - left < 3) or (bot - top < 3):
            #return (mid_x, mid_y)
            return str(mid_x) + "," + str(mid_y)

        # Otherwise, initialize scores and recursively score quadrants
        quadrant_scores = [0, 0, 0, 0]

        for x in xrange(left, right):
            for y in xrange(top, bot):
                if matrix[y, x] > 0:  # yeah I know, right? Y, X. WTF
                    quadrant_scores[self.quadrant(x, y, mid_x, mid_y)] += 1

        # Functional magic to tally up scores to find the best next quad
        winning_quad = max(enumerate(quadrant_scores), key=lambda kvp: kvp[1])[0]

        # Calculate bounds of next region to search
        new_left = left if winning_quad in [0, 2] else mid_x
        new_right = mid_x if winning_quad in [0, 2] else right
        new_top = top if winning_quad in [0, 1] else mid_y
        new_bot = mid_y if winning_quad in [0, 1] else bot

        return self.find_center(matrix, new_left, new_top, new_right, new_bot)

    def quadrant(self, x, y, mid_x, mid_y):
      #Utility function to find quadrants in a x by y rectangle
        return 2 * (y > mid_y) + 1 * (x > mid_x)


def cli():
    # Regardless, instantiate an object detector
    detector = ObjectDetector()

    if len(sys.argv) == 1:
        print "Usage: ./" + str(sys.argv[0]) + " [filename]"

    elif len(sys.argv) == 2:
        # Detect object, print result
        print detector.detect_object(str(sys.argv[1]))

    else:
        # For testing (HACK) -- uses OSX's builtin imagesnap util
        while True:
            image_filename = 'temp.png'
            os.system("imagesnap %s " % image_filename)

            # Detect center
            center = detector.detect_object(image_filename)
            frame = cv.LoadImage(image_filename)

            # Draw a circle to indicate where the center was found
            cv.Circle(frame, center, 10, cv.Scalar(0, 255, 255))
            cv.NamedWindow('a_window', cv.CV_WINDOW_AUTOSIZE)
            cv.ShowImage('a_window', frame)
            cv.WaitKey(400)

if __name__ == '__main__':
    # Call command line interface
    cli()
