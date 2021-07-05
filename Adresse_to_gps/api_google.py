#!/usr/bin/env python
# coding: utf-8

import googlemaps


def google_api(ville, rue, numero):
    gmaps = googlemaps.Client(key='AIzaSyCZtvRS9zekqjZM5NzFwf-J9sJPZZLsq5s')

    # Geocoding an address
    geocode_result = gmaps.geocode(rue + " " + numero + " " + ville)
    print(type(geocode_result[0]))

    gps = geocode_result[0]["geometry"]["location"]

    return gps


if __name__ == '__main__':
    ville = 'Leuven'
    rue = 'Henri Regastraat'
    numero = '43'

    print(google_api(ville, rue, numero))

