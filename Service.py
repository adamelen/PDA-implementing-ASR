import abc

class Service:
    ''' An abstract class for the possible services. It contains the getInfo method with which the user gets the information he's looking for '''
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def getInfo(self, vc, trl, lang):
        pass
