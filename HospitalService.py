from GooglePlaceService import GooglePlaceService

class HospitalService(GooglePlaceService):
    ''' A child class to GooglePlaceService that implements HospitalService'''

    def __init__(self):
        super(HospitalService, self).__init__()
        self.place_type = 'hospital'
        
