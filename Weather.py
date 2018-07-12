import abc

class Weather:
    ''' An abstract class for the possible weather APIs. It contains the getWeather method which is implemented by the children subclasses and returns the weather forecast '''
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def getWeather(self, city_name, lat, lon, dt):
        pass
