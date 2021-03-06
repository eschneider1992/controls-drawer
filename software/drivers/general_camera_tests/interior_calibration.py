# http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html

# Part 1
import cv2
import glob
import numpy as np
import pickle

from utils import lcm_msgs


# Checkerboard corner column and row values
CBROW = 9
CBCOL = 6


# termination criteria
# 30 = max number of iterations
# 0.001 = min accuracy
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0, 0, 0), (1, 0, 0), (2, 0, 0) ...., (6, 5, 0)
objPoint = np.zeros((CBCOL * CBROW, 3), np.float32)
objPoint[:, :2] = np.mgrid[0:CBROW, 0:CBCOL].T.reshape(-1, 2)

# Arrays to store object points and image points from all the images.
objPoints = [] # 3d point in real world space
imagePoints = [] # 2d points in image plane.

imageNames = glob.glob('../crenova_iscope_endoscope_2Mpix/square_images/*.png')
imageNames = [name for name in imageNames if "_calib" not in name]

import ipdb; ipdb.set_trace()
for imageName in imageNames:
    image = cv2.imread(imageName)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (CBROW, CBCOL), None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objPoints.append(objPoint)

        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imagePoints.append(corners2)

        # Draw and display the corners
        image = cv2.drawChessboardCorners(image, (CBROW, CBCOL), corners2, ret)
        cv2.imshow('{}'.format(imageName), image)
        cv2.waitKey(1200)
        cv2.destroyAllWindows()
    else:
        print("File {} pattern not found!".format(imageName))


# Part 2
import ipdb; ipdb.set_trace()
retval, matrix, distCoeffs, rvecs, tvecs = cv2.calibrateCamera(objPoints, imagePoints, gray.shape[::-1],None,None)

print "retval", retval

# Output 3x3 floating-point camera matrix  A = [[f_x, 0,   c_x],
#                                               [0,   f_y, c_y],
#                                               [0,   0,   1  ]]
# fx, fy are the focal lengths expressed in pixel units
# (cx, cy) is a principal point that is usually at the image center
print "matrix", matrix

# distCoeffs - Output vector of distortion coefficients
#   (k_1, k_2, p_1, p_2[, k_3[, k_4, k_5, k_6]]) of 4, 5, or 8 elements.
# k_1, k_2, k_3, k_4, k_5, and k_6 are radial distortion coefficients. p_1 and
#   p_2 are tangential distortion coefficients. if the vector contains four
#   elements, it means that k_3=0.
print "distCoeffs", distCoeffs

# rvecs - Output vector of rotation vectors (see Rodrigues()) estimated for
#   each pattern view (e.g. std::vector<cv::Mat>>). That is, each k-th rotation
#   vector together with the corresponding k-th translation vector (see the
#   next output parameter description) brings the calibration pattern from the
#   model coordinate space (in which object points are specified) to the world
#   coordinate space, that is, a real position of the calibration pattern in
#   the k-th pattern view (k=0.. M -1).
# tvecs - Output vector of translation vectors estimated for each pattern view.
print "rvecs", rvecs
print "tvecs", tvecs

# Write out results to pickle
calibrationResults = {
    "retval": retval,
    "matrix": matrix,
    "distCoeffs": distCoeffs,
    "rvecs": rvecs,
    "tvecs": tvecs,
}
pickle.dump(calibrationResults,
            open("intrinsic_calibration_results_{}.pickle".format(lcm_msgs.utime_now()), "wb"))


# Part 3
h = None
w = None
newCameraMatrix = None
roi = None
for imageName in imageNames:
    image = cv2.imread(imageName)
    if h is None:
        h, w = image.shape[:2]
        newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(matrix, distCoeffs, (w, h), 1, (w, h))
        print "newCameraMatrix", newCameraMatrix

    # Part 4
    # undistort
    dst = cv2.undistort(image, matrix, distCoeffs, None, newCameraMatrix)

    # crop the image
    x, y, w, h = roi
    dstCrop = dst[y:y + h, x:x + w]
    cv2.imwrite('{}_calib.png'.format(imageName.replace(".jpg", "")), dstCrop)
    cv2.imwrite('{}_calib_nocrop.png'.format(imageName.replace(".jpg", "")), dst)


# Part 5
import ipdb; ipdb.set_trace()
tot_error = 0
for i in xrange(len(objPoints)):
    imagePoints2, _ = cv2.projectPoints(objPoints[i], rvecs[i], tvecs[i], matrix, distCoeffs)
    error = cv2.norm(imagePoints[i], imagePoints2, cv2.NORM_L2) / len(imagePoints2)
    tot_error += error

print "mean error: ", tot_error / len(objPoints)
