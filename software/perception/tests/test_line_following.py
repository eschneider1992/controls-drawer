import numpy as np
import pytest

from geometry.planar import Rx, Ry, Rz
from perception.line_following import getCircularMask, getRingMask


@pytest.fixture
def shape():
    return (480, 640)


@pytest.fixture
def centeredHT():
    matrix = np.eye(4)
    matrix[0:3, 0:3] = Rx(np.pi).dot(Rz(np.pi))
    matrix[0:3, 3] = np.array([0.0, 0.0, 1.0])
    return matrix


@pytest.fixture
def offcenterHT():
    matrix = np.eye(4)
    matrix[0:3, 0:3] = Rx(np.pi).dot(Rz(np.pi))
    matrix[0:3, 3] = np.array([0.1, -0.1, 1.0])
    return matrix


@pytest.fixture
def calibMatrix():
    matrix = np.eye(3)
    # Set the c_x and c_y values for the center of the frame, for a fake
    # (640, 480) camera with added jitter
    matrix[0, 2] = 320
    matrix[1, 2] = 240
    # Set the focal length (I have no idea what a reasonable focal length is)
    matrix[0, 0] = 1000
    matrix[1, 1] = 1000
    return matrix


class TestGetCircularMask():
    def testCallable(self, shape, centeredHT, calibMatrix):
        mask = getCircularMask(shape, centeredHT, calibMatrix, radius=0.15)

    def testCentered(self, shape, centeredHT, calibMatrix):
        mask = getCircularMask(shape, centeredHT, calibMatrix, radius=0.002)
        assert mask.sum() > 1
        assert mask[mask.shape[0] / 2, mask.shape[1] / 2] == True

    def testSize(self, shape, centeredHT, calibMatrix):
        smallMask = getCircularMask(shape, centeredHT, calibMatrix, radius=0.002)
        largeMask = getCircularMask(shape, centeredHT, calibMatrix, radius=0.02)
        assert smallMask.sum() < largeMask.sum()

    def testComparision(self, shape, centeredHT, offcenterHT, calibMatrix):
        center = getCircularMask(shape, centeredHT, calibMatrix, radius=0.08)
        offcenter = getCircularMask(shape, offcenterHT, calibMatrix, radius=0.08)

        whereCenter = np.argwhere(center)
        whereOffcenter = np.argwhere(offcenter)

        centeredNorm = np.linalg.norm(whereCenter, axis=1)
        offcenterNorm = np.linalg.norm(whereOffcenter, axis=1)
        assert np.average(centeredNorm) < np.average(offcenterNorm)


class TestGetRingMask():
    def testOverlap(self, shape, centeredHT, calibMatrix):
        mask1 = getCircularMask(shape, centeredHT, calibMatrix, radius=0.05)
        mask2 = getCircularMask(shape, centeredHT, calibMatrix, radius=0.1)
        ringMask = getRingMask(shape, centeredHT, calibMatrix, 0.1, 0.05)
        assert np.all(ringMask == np.logical_xor(mask1, mask2))
