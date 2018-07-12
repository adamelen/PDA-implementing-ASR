class VoiceCommand:
    ''' An <<Entity>> class that contains the initial text the user said, the intent and parameters extracted from TTIV and the final text that is returned to the user'''

    def __init__(self, text=None):
        self.text = text
        self.intent = None
        self.parameters = None
        self.textToTell = None
