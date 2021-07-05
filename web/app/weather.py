import requests

class RequestWeather():
    '''Class for requesting weather for Charleroi'''
    
    api_key = "bef98ba6ffb6125c9a08abec73fd18cc"
    def request(self):
        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q=Charleroi&units=metric&appid={self.api_key}")
        print(response.status_code)
        return response.json() if response.status_code == 200 else response.status_code