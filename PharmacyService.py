from GooglePlaceService import GooglePlaceService

class PharmacyService(GooglePlaceService):
    ''' A child class to GooglePlaceService that implements PharmacyService'''

    def __init__(self):
        super(PharmacyService, self).__init__()
        self.place_type = 'pharmacy'
