import abc

class PlaceService:
    ''' An abstract class for the possible place service APIs. It contains the getPlaceInfo method which is implemented by the children subclasses and returns information about a place type. '''
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def getPlaceInfo(self, loc, dist, city_name, lang):
        pass
