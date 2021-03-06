import argparse
import cv2
import lcm
import numpy as np
import time

from geometry.cameras import Camera
from geometry.cameras import cropImage
from geometry.cameras import globalToPixels
from perception.line_following import findPointInFrame
from perception.line_following import getCircularMask
from perception.line_following import getMaskBounds
from utils import lcm_msgs


TRAVEL_SPEED = 0.01


class LineFollower():
    def __init__(self, args):
        self.setupMasks()
        self.setupLCM(args.image_channel, args.table_channel, args.command_rate)

        # Set an initial starting point for the tracking
        self.targetPoint = np.array([0, 0.01, 0])
        # Whether to re-publish the image with the IDed point
        self.publishLabeledImage = args.publish_labeled_image
        # Whether to print live commands
        self.printCommands = args.print_commands
        # Whether to publish points of interest
        self.publishPOI = args.publish_poi

        # The width of the followed line
        self.lineWidth = args.line_width

    def setupMasks(self):
        self.camera = Camera()
        frameShape = (460, 621)
        mask9mm = getCircularMask(frameShape, self.camera.HT, self.camera.invCalibMatrix, 0.009)
        self.maskBounds = getMaskBounds(mask9mm, pixBuffer=10)
        self.kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
        circleEdges9 = cv2.Canny(mask9mm.astype(np.uint8) * 255, 50, 200)
        self.ring = cv2.dilate(circleEdges9, self.kernel, iterations=1)
        self.croppedRing, croppedCalibMatrix = \
            cropImage(self.ring, self.maskBounds, self.camera.calibMatrix)
        self.invCroppedCalib = np.linalg.inv(croppedCalibMatrix)

    def setupLCM(self, imageChannel, tableChannel, commandRate):
        self.lcmobj = lcm.LCM()
        self.lcmobj.subscribe(imageChannel, self.onImage)
        self.tableChannel = tableChannel
        self.commandPeriod = 1.0 / commandRate
        self.lastCommandTime = time.time()

    def run(self):
        while(True):
            lcm_msgs.lcmobj_handle_msg(self.lcmobj, timeout=0.01)
            now = time.time()
            if now >= self.lastCommandTime + self.commandPeriod:
                self.commandTable()
                self.lastCommandTime = now

    def onImage(self, channel, data):
        # Decode/parse out the image
        image = lcm_msgs.auto_decode(channel, data)
        # Get actual image data
        frame = lcm_msgs.image_t_to_nparray(image)
        # Find the point that we want to track
        foundPoint = findPointInFrame(frame=frame,
                                      bounds=self.maskBounds,
                                      kernel=self.kernel,
                                      ringOfInterest=self.croppedRing,
                                      HT=self.camera.HT,
                                      invCroppedCalibMatrix=self.invCroppedCalib,
                                      pastGlobalPoint=self.targetPoint,
                                      width=self.lineWidth)
        # If we found a viable point, save it as the current tracked point
        if foundPoint is not None:
            self.targetPoint = foundPoint
            if self.publishPOI:
                self.publishFoundPoint()
        else:
            print "None!"

        # Publish marked up image if desired
        if self.publishLabeledImage:
            self.publishFoundPointImage(image, frame)

    def publishFoundPoint(self):
        # Set up message
        channel = 'IMAGE_POINTS_OF_INTEREST'
        outMsg = lcm_msgs.auto_instantiate(channel)
        outMsg.utime = lcm_msgs.utime_now()
        outMsg.num_points = 1
        # Pack point data
        pixel = self.targetPixel
        outMsg.axis_1 = [int(pixel[0])]
        outMsg.axis_2 = [int(pixel[1])]
        # Publish
        self.lcmobj.publish(channel, outMsg.encode())

    def publishFoundPointImage(self, inMsg, frame):
        # Set up the image
        channel = "IMAGE_TRACKING"
        outMsg = lcm_msgs.auto_instantiate(channel)
        # Copy message except for the image data
        for slot in outMsg.__slots__:
            if slot in ['data', 'num_data']:
                continue
            setattr(outMsg, slot, getattr(inMsg, slot))
        # Plot the point
        frame *= np.logical_not(self.ring.astype('bool'))
        colorFrame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        cv2.circle(colorFrame, self.targetPixel, radius=15, thickness=2,
                   color=(0, 0, 255))
        # Write the image data
        outMsg.request.format = outMsg.request.FORMAT_BGR
        outMsg.data = lcm_msgs.nparray_to_image_t_data(colorFrame)
        outMsg.num_data = len(outMsg.data)
        # Publish
        self.lcmobj.publish(channel, outMsg.encode())

    def commandTable(self):
        # For now, just drive in that direction
        direction = self.targetPoint / np.linalg.norm(self.targetPoint)
        stepSize = TRAVEL_SPEED * self.commandPeriod
        # Build and publish
        msg = lcm_msgs.auto_instantiate(self.tableChannel)
        msg.position = direction * stepSize
        msg.velocity = TRAVEL_SPEED
        if self.printCommands
            print("Publishing relative command {} with velocity {}".format(msg.position, msg.velocity))
        self.lcmobj.publish(self.tableChannel, msg.encode())

    @property
    def targetPixel(self):
        return tuple([int(x)
                      for x in np.round(globalToPixels(self.targetPoint,
                                                       self.camera.calibMatrix,
                                                       HT=self.camera.HT))])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Starts a line follower",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--controller-function",
                        help="Choose which function to use as a controller",
                        default="proportional")
    parser.add_argument("-i", "--image-channel",
                        help="Channel on which to track line position",
                        default="IMAGE_RAW")
    parser.add_argument("-o", "--publish-poi",
                        help="Whether to publish points of interest",
                        action="store_false")
    parser.add_argument("-p", "--publish-labeled-image",
                        help="Publishes on the IMAGE_TRACKING channel",
                        action="store_true")
    parser.add_argument("-P", "--print-commands",
                        help="Prints the table commands that are occurring",
                        action="store_false")
    parser.add_argument("-r", "--command-rate",
                        help="Rate at which to send out position commands",
                        type=float,
                        default=10.0)
    parser.add_argument("-t", "--table-channel",
                        help="Channel on which to send table commands",
                        default="POSITION_COMMAND")
    parser.add_argument("line_width",
                        help="Width of the line in meters (usually 0.003, but"
                             "actually choose each time)",
                        type=float)
    args = parser.parse_args()

    LF = LineFollower(args)
    LF.run()
