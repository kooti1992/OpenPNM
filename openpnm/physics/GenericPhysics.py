from openpnm.core import Base, Workspace, ModelsMixin, logging
from numpy import ones
logger = logging.getLogger(__name__)
ws = Workspace()


class GenericPhysics(Base, ModelsMixin):
    r"""
    Generic class to generate Physics objects

    Parameters
    ----------
    network : OpenPNM Network object
        The network to which this Physics should be attached

    phase : OpenPNM Phase object
        The Phase object to which this Physics applies

    geometry : OpenPNM Geometry object
        The Geometry object that defines the pores/throats where this Physics
        should be applied.

    name : str, optional
        A unique string name to identify the Physics object, typically same as
        instance name but can be anything.  If left blank, and name will be
        generated that include the class name and a random string.

    """

    def __init__(self, project=None, network=None, phase=None,
                 geometry=None, settings={}, **kwargs):

        # Define some default settings
        self.settings.update({'prefix': 'phys'})
        # Overwrite with user supplied settings, if any
        self.settings.update(settings)

        # Deal with network or project arguments
        if network is not None:
            project = network.project

        super().__init__(project=project, **kwargs)

        if phase is not None:
            self.settings['phase'] = phase.name
        if geometry is not None:
            self.settings['geometry'] = geometry.name
            self.set_locations(geometry)

    def set_locations(self, geometry):
        phase = self.project.phases()[self.settings['phase']]
        network = self.project.network

        # Adjust array sizes
        self['pore.all'] = ones((geometry.Np, ), dtype=bool)
        self['throat.all'] = ones((geometry.Nt, ), dtype=bool)

        # Initialize a label array in the associated phase
        phase['pore.'+self.name] = False
        phase['pore.'+self.name][network.pores(geometry.name)] = True
        phase['throat.'+self.name] = False
        phase['throat.'+self.name][network.throats(geometry.name)] = True

    def __getitem__(self, key):
        element = key.split('.')[0]
        boss = self.project.find_phase(self)
        if key.split('.')[-1] == '_id':
            inds = boss._get_indices(element=element, labels=self.name)
            vals = boss[element+'._id'][inds]
        # Convert self.name into 'all'
        elif key.split('.')[-1] in [self.name]:
            vals = self[element+'.all']
        # Apply logic in the __missing__ method
        elif key not in self.keys():
            vals = self.__missing__(key)
        else:
            vals = super(Base, self).__getitem__(key)
        return vals

    def __missing__(self, key):
        element = key.split('.')[0]
        phase = self.project.find_phase(self)
        # If key not available try running model
        if key in self.models.keys():
            print('GenericPhysics: ' + key + ' missing, running model')
            self.regenerate_models(propnames=[key])
            vals = self.__getitem__(key)
        # If not found on network a key error will be raised
        else:
            inds = phase._get_indices(element=element, labels=self.name)
            vals = super(Base, phase).__getitem__(key)[inds]
        return vals
