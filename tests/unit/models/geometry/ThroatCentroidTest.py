import openpnm as op
import openpnm.models.geometry as gm
import numpy as np


class ThroatCentroidTest:

    def setup_class(self):
        self.net = op.network.Cubic(shape=[5, 1, 1], spacing=1)
        self.geo = op.geometry.GenericGeometry(network=self.net,
                                               pores=self.net.pores(),
                                               throats=self.net.throats())

    def test_voronoi(self):
        pass

    def test_pore_coords(self):
        self.geo.add_model(propname='throat.centroid',
                           model=gm.throat_centroid.pore_coords)
        assert np.all(self.geo['throat.centroid'][:, 0]
                      - np.arange(1, 5, 1) == 0)
        assert np.all(self.geo['throat.centroid'][:, 1] == 0.5)
        assert np.all(self.geo['throat.centroid'][:, 2] == 0.5)


if __name__ == '__main__':

    t = ThroatCentroidTest()
    self = t
    t.setup_class()
    for item in t.__dir__():
        if item.startswith('test'):
            print('running test: '+item)
            t.__getattribute__(item)()
