from Weather import Weather

class Xweather(Weather):
    ''' A sample interface for a weather API '''
    def getWeather(self, city_name, lat, lon, dt):
        print("Not available")
