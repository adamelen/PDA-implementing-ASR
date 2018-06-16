from places import places

def hospital(parameters):
    ''' Sends a request to google API "Places" to find hospitals in a certain region and returns a text that contains names and addresses of these hospitals'''

    textToTell = places(parameters, 'hospital', 'hospitals')
    return textToTell
