class Information:
    ''' A class that acts as a bridge between AppControl and Service classes '''

    def __init__(self, s):
        self.service = s

    def useService(self, vc, trl, lang):
        return self.service.getInfo(vc, trl, lang)
