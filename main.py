print("Welcome to CO3038, Lab 1.")
# Lecturer's code-------------------------------------------------------------------------------------------------------
import paho.mqtt.client as mqttclient
import time
import json
# ----------------------------------------------------------------------------------------------------------------------
import requests
import winrt.windows.devices.geolocation as wdg     # For dynamic location.
import asyncio                                      # wdg requires asynchronous input/output.
from geopy.geocoders import Nominatim               # To get city name from coordinates.
# Lecturer's code-------------------------------------------------------------------------------------------------------
BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "FGdNTjaigRJBidqrJZ60"

def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")

def recv_message(client, userdate, message):...

def connected(client, userdate, flags, rc):...
#-----------------------------------------------------------------------------------------------------------------------
async def get_geoposition():
    # Geolocator class provided by WinRT
    geolocator = wdg.Geolocator()
    # Asynchronous operation to retrieve geoposition
    geoposition = await geolocator.get_geoposition_async()
    return [geoposition.coordinate.latitude, geoposition.coordinate.longitude]

def get_location():
    return asyncio.run(get_geoposition())
# Lecturer's code-------------------------------------------------------------------------------------------------------
client = mqttclient.Client("Gateway_Thingsboard")

client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message
# ----------------------------------------------------------------------------------------------------------------------
# Inititializing variables.
temp = 99
humi = 99
light_intensity = 100
longitude = 139.839478
latitude = 35.652832
city = "Tokyo"

# API key for OpenWeather API.
api_key = "7b58f1ac37aa6eed43c8083af305e913"
# Provided by GeoPy.
geolocator = Nominatim(user_agent="geoapiExercises")

counter = 0
#-----------------------------------------------------------------------------------------------------------------------
while True:
    # Get coordinates using WinRT-based functions.
    latitude = get_location()[0]
    longitude = get_location()[1]

    # Get city name from coordinates using GeoPy.
    where = geolocator.reverse(str(latitude)+","+str(longitude))
    address = where.raw['address']
    city = address.get('city', '')
    state = address.get('state', '')
    country = address.get('country', '')

    # Using OpenWeather API to get dynamic temperature and humidity.
    complete_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"
    response = requests.get(complete_url)
    response_json = response.json()

    if response_json["cod"] != "404":
        response_json_main = response_json["main"]
        # Convert from Kelvin to Celsius.
        temp = response_json_main["temp"]-273.15

        humi = response_json_main["humidity"]

    # Convert data to JSON.
    collect_data = {'temperature': temp, 'humidity': humi, 'light': light_intensity, 'longitude': longitude,
                    'latitude': latitude, 'city': city, 'state': state, 'country': country}

    # Changes light intensity and loops back if overflow.
    light_intensity += 1
    if (light_intensity > 100):
        light_intensity = 0

    # Send data to server.
    client.publish('v1/devices/me/telemetry', json.dumps(collect_data),1)
    # Print to console to check.
    print("Current location: ", city, ", ", state, ", ", country, "; temperature: ", temp, "; humidity: ", humi)
    time.sleep(10)
