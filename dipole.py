import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection

from .misc import rotation_matrix_3D

# ****************************************************************************************************
class MagneticDipole(object):
    # TODO bounding box
    # TODO multicolor shells?
    # TODO plot2D
    # TODO tilted dipole!

    def __init__(self, center, inclination):
        self.center = center
        self.phi = np.radians(inclination)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def fieldlines(self, nshells=3, naz=5, res=100, scale=1., bounding_box=3, rmin=1.):
        '''Compute the field lines for a dipole magnetic field'''

        Re = 1
        L = np.r_['-1,3,0', range(1, nshells + 1)]  # as 3D array

        theta = np.linspace(0, np.pi, res)
        sin_theta = np.sin(theta)
        r = Re * sin_theta ** 2  # radial profile of B-field lines
        r_sin_theta = r * sin_theta

        phi = np.c_[np.linspace(0, 2 * np.pi, naz+1)[:-1]] # wraps at 2pi

        # convert to Cartesian coordinates
        v = np.r_['-1,3,0',
                  r_sin_theta * np.cos(phi),
                  r_sin_theta * np.sin(phi),
                  r * np.cos(theta) * np.ones_like(phi)]
        v = v.reshape(-1, 3)
        fieldlines = L * v

        if scale:
            fieldlines *= scale

        # tilt
        if self.phi != 0:
            # 3D rotation!
            R = rotation_matrix_3D((0, 1, 0), np.radians(20))
            fieldlines = np.tensordot(R, fieldlines, [0, -1]).transpose(1, 2, 0)

        # mask fieldlines inside WD
        if rmin:
            l = np.linalg.norm(fieldlines.T, axis=0) <= rmin
            L = np.tile(l, (3, 1, 1)).T
            fieldlines = np.ma.masked_array(fieldlines, mask=L)

        bbox = bounding_box
        if bbox:
            if np.size(bbox) <= 1:
                bbox = np.tile([-1, 1], (3, 1)) * bbox
            xyz = (fieldlines - self.center.T) - bbox.mean(1)
            fieldlines[(xyz < bbox[:, 0]) | (bbox[:, 1] < xyz)] = np.ma.masked

        return fieldlines

    def boxed(self, fieldlines, box):
        box = 3

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def plot3d(self, ax, nshells=3, naz=5, **kw):
        #
        # ax = kw.get('ax', None):
        # if ax
        segments = self.fieldlines(nshells, naz)
        ax.add_collection3d(Line3DCollection(segments, **kw))
        ax.auto_scale_xyz(*segments.T)


        # dipole = MagneticDipole()
