#!/usr/bin/env python

import argparse
import numpy as np
import time

import lcm

from geometry import planar
from utils import cv_tools
from utils.grbl_tools import mToMM
from utils import lcm_msgs


# Default travel speed in m/s, roughly 600 mm/min
TRAVEL_SPEED = 0.01
# Number of Polygon sides
POLYGON_DEGREE = 5
# Polygon side length in meters
SIDE_LENGTH = 0.015
# Point at which to take a picture from (TODO: jitter this and take more pics)
PICTURE_POSITION = [-0.01, 0.015]


class ExteriorCameraCalibration():
    def __init__(self, args):
        # Set up the LCM publishers and subscribers
        self.lcmobj = lcm.LCM()
        self.toolStateChannel = "TOOL_STATE"
        self.posCmdChannel = "POSITION_COMMAND"
        self.imageReqChannel = "REQUEST_IMAGE"
        self.imageChannel = "IMAGE_CALIB"
        self.toolSub = self.lcmobj.subscribe(self.toolStateChannel, self.onToolState)
        self.imageSub = self.lcmobj.subscribe(self.imageChannel, self.onImage)

        # Ask and make sure the system is set up
        raw_input("Is system in place and pen down? [enter]")

        # Draw a pentagon
        vectors = planar.polygonVectors(POLYGON_DEGREE)
        msg = lcm_msgs.auto_instantiate(self.posCmdChannel)
        msg.velocity = TRAVEL_SPEED
        for i in xrange(POLYGON_DEGREE):
            msg.position = vectors[i][0:2] * SIDE_LENGTH
            msg.utime = lcm_msgs.utime_now()
            self.lcmobj.publish(self.posCmdChannel, msg.encode())

        # Lift the pen
        raw_input("Lift pen (don't joggle tool) hit enter when done [enter]")

        # Do the hatching by hand for now (make a tool that lifts the pen up!)
        raw_input("Do hatching by hand for now, hit enter when done [enter]")

        # Travel out of the way and take a picture
        msg = lcm_msgs.auto_instantiate(self.posCmdChannel)
        msg.velocity = TRAVEL_SPEED
        msg.position = PICTURE_POSITION
        self.lcmobj.publish(self.posCmdChannel, msg.encode())

        # Wait until the system is stopped - the loop sleep is long enough to
        #   capture tool head movement
        self.systemStopped = False
        self.lastMsg = None
        while not self.systemStopped:
            # Waits to handle message until timeout, then loops
            lcm_msgs.lcmobj_handle_msg(self.lcmobj, timeout=0.05)
            # Sleep for 0.1 seconds to make sure TOOL_STATE changes if the head
            #   is actually moving
            time.sleep(0.1)

        # Wait for camera to focus, then take a picture
        print("Waiting for camera to focus (hopefully)")
        time.sleep(10.0)
        imReqMsg = lcm_msgs.auto_instantiate(self.imageReqChannel)
        imReqMsg.format = imReqMsg.FORMAT_GRAY
        imReqMsg.name = self.__class__.__name__
        imReqMsg.dest_channel = self.imageChannel
        print("Sent image request!")
        self.lcmobj.publish(self.imageReqChannel, imReqMsg.encode())

        # Wait for a second to see if the picture came in
        self.frame = None
        startTime = time.time()
        while time.time() < (startTime + 4.0) and self.frame is None:
            lcm_msgs.lcmobj_handle_msg(self.lcmobj, timeout=0.05)
            time.sleep(0.01)
        if self.frame is None:
            print("Never ended up getting an image!")
        else:
            import cv2
            # Display the frame for funsies
            cv2.imshow("frame", self.frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def onToolState(self, channel, data):
        msg = lcm_msgs.auto_decode(channel, data)
        if self.lastMsg is not None:
            # If the position is unchanging, the tool has stopped
            if np.allclose(msg.position, self.lastMsg.position):
                self.systemStopped = True
        self.lastMsg = msg

    def onImage(self, channel, data):
        print("Received an image!")
        # Decode/parse out the image
        image = lcm_msgs.auto_decode(channel, data)
        frame = lcm_msgs.image_t_to_nparray(image)
        # Save the image for safekeeping
        imageName = "frame_SL{}_X{}_Y{}_{}.png".format(
            mToMM(SIDE_LENGTH), mToMM(PICTURE_POSITION[0]),
            mToMM(PICTURE_POSITION[1]), image.utime
        )
        cv_tools.writeImage(imageName, frame)
        print("Image saved to {}".format(imageName))
        self.frame = frame


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runs exterior (hand<>eye) camera calibration",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--num-pictures",
                        help="Number of pictures to take of the polygon",
                        type=int,
                        default=2)
    args = parser.parse_args()

    ECC = ExteriorCameraCalibration(args)