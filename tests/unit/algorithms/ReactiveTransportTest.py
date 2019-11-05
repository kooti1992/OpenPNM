import pytest
import openpnm as op
from numpy.testing import assert_allclose


class ReactiveTransportTest:

    def setup_class(self):
        self.net = op.network.Cubic(shape=[9, 9, 9])
        self.geo = op.geometry.GenericGeometry(network=self.net,
                                               pores=self.net.Ps,
                                               throats=self.net.Ts)
        self.phase = op.phases.GenericPhase(network=self.net)
        self.phys = op.physics.GenericPhysics(network=self.net,
                                              phase=self.phase,
                                              geometry=self.geo)
        self.phys['throat.diffusive_conductance'] = 1e-15
        self.phys['pore.A'] = -1e-15
        self.phys['pore.k'] = 2
        std_kinetics = op.models.physics.generic_source_term.standard_kinetics
        self.phys.add_model(propname='pore.reaction', model=std_kinetics,
                            prefactor='pore.A', exponent='pore.k',
                            quantity='pore.concentration',
                            regen_mode='deferred')

    def test_one_value_one_source(self):
        rt = op.algorithms.ReactiveTransport(network=self.net,
                                             phase=self.phase)
        rt.setup(rxn_tolerance=1e-10, max_iter=5000,
                 relaxation_source=1.0, relaxation_quantity=1.0)
        rt.settings.update({'conductance': 'throat.diffusive_conductance',
                            'quantity': 'pore.concentration'})
        rt.set_source(pores=self.net.pores('bottom'), propname='pore.reaction')
        rt.set_value_BC(pores=self.net.pores('top'), values=1.0)
        rt.run()
        c_mean_desired = 0.648268
        c_mean = rt['pore.concentration'].mean()
        assert_allclose(c_mean, c_mean_desired, rtol=1e-6)

    def test_source_over_BCs(self):
        rt = op.algorithms.ReactiveTransport(network=self.net,
                                             phase=self.phase)
        rt.settings.update({'conductance': 'throat.diffusive_conductance',
                            'quantity': 'pore.concentration'})
        rt.set_value_BC(pores=self.net.pores('left'), values=1.0)
        rt.set_value_BC(pores=self.net.pores('right'), values=0.5)
        with pytest.raises(Exception):
            rt.set_source(pores=self.net.pores(["left", "right"]),
                          propname='pore.reaction')

    def test_BCs_over_source(self):
        rt = op.algorithms.ReactiveTransport(network=self.net,
                                             phase=self.phase)
        rt.settings.update({'conductance': 'throat.diffusive_conductance',
                            'quantity': 'pore.concentration'})
        rt.set_source(pores=self.net.pores('left'), propname='pore.reaction')
        with pytest.raises(Exception):
            rt.set_value_BC(pores=self.net.pores('left'), values=1.0)

    def test_source_over_source(self):
        rt = op.algorithms.ReactiveTransport(network=self.net,
                                             phase=self.phase)
        rt.settings.update({'conductance': 'throat.diffusive_conductance',
                            'quantity': 'pore.concentration'})
        rt.set_source(pores=self.net.pores('left'), propname='pore.reaction')
        with pytest.raises(Exception):
            rt.set_source(pores=self.net.pores("left"),
                          propname='pore.another_reaction')

    def teardown_class(self):
        ws = op.Workspace()
        ws.clear()


if __name__ == '__main__':

    t = ReactiveTransportTest()
    t.setup_class()
    for item in t.__dir__():
        if item.startswith('test'):
            print('running test: '+item)
            t.__getattribute__(item)()
    self = t
