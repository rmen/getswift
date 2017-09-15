#!/usr/bin/env python
# coding: utf-8
# getswift/dronedelivery/dispath.py

"""
GetSwift Code Test
See: https://github.com/GetSwift/codetest

Author: Rajesh Menon <menon.rajesh@gmail.com>
"""
import time
from collections import namedtuple
from math import (radians, sin, cos, sqrt, asin)
from operator import attrgetter

import requests


class Global(object):
    # depo = '303 Collins Street, Melbourne, VIC 3000'
    depo = (-37.81652845, 144.963816478363)
    drone_speed = 50  # in km/h


def haversine(lat1, lon1, lat2, lon2):
    """
    The haversine formula determines the great-circle distance between
    two points on a sphere given their longitudes and latitudes.

    From: https://rosettacode.org/wiki/Haversine_formula
    """

    R = 6372.8  # Earth radius in kilometers

    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
    c = 2*asin(sqrt(a))

    return R * c


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Assign packages to drones.')
    parser.add_argument('-d', '--drones', required=True,
                        help='URL containing a JSON listing of drones.')
    parser.add_argument('-p', '--packages', required=True,
                        help='URL containing a JSON listing of packages.')
    return parser.parse_args()


def enque_drones(json_drones, now):
    """
    Returns a list of tuples of drones sorted by their ETA at the depo.
    """
    drones = []
    Drone = namedtuple('Drone', ['droneId', 'ETA'])
    for drone in json_drones:
        lat = drone['location']['latitude']
        lon = drone['location']['longitude']
        try:
            package = drone['packages'][0]
            # drone is en route to package destination.
            destlat = package['destination']['latitude']
            destlon = package['destination']['longitude']
            dist_to_dest = haversine(lat, lon, destlat, destlon)
            dist_to_depo = haversine(destlat, destlon, *Global.depo)
            distance = dist_to_dest + dist_to_depo
        except IndexError:  # no packages; en route to depo after delivery.
            distance = haversine(lat, lon, *Global.depo)

        # get the flight time, in seconds, to the depo and then the ETA.
        flight_time_to_depo = int((distance / Global.drone_speed) * 3600)
        eta = now + flight_time_to_depo
        drones.append(Drone(drone['droneId'], eta))

    drones.sort(key=attrgetter('ETA'))  # sorted by the ETA at the depo.
    return drones


def enque_packages(json_packages, now):
    """
    Returns a list of tuples of packages, sorted by delivery deadlines.
    """
    Package = namedtuple('Package', ['ETD', 'deadline', 'packageId'])
    packages = []
    for pkg in json_packages:
        lat = pkg['destination']['latitude']
        lon = pkg['destination']['longitude']
        dist_to_dest = haversine(lat, lon, *Global.depo)
        flight_time_to_dest = int((dist_to_dest / Global.drone_speed) * 3600)
        packages.append(
            Package(flight_time_to_dest, pkg['deadline'], pkg['packageId']))

    packages.sort(key=attrgetter('deadline'))  # sorted by deadline.
    return packages


def assign_packages(drones, packages):
    """
    Assigns packages to drones by ability to deliver by the deadline.
    Returns a mapping of successful assignments and unassigned packages.
    """
    assignments = []
    unassignedPackageIds = []

    len_p = len(packages)
    len_d = len(drones)
    i = 0
    j = 0
    while i < len_p and j < len_d:
        package = packages[i]
        drone = drones[j]
        if drone.ETA + package.ETD <= package.deadline:
            assignments.append(
                {'droneId': drone.droneId, 'packageId': package.packageId})
            j += 1
        else:
            unassignedPackageIds.append(package.packageId)
        i += 1
    while i < len_p:  # we have more packages than drones.
        unassignedPackageIds.append(package.packageId)
        i += 1

    return {
        'assignments': assignments,
        'unassignedPackageIds': unassignedPackageIds,
        }


def main():
    args = parse_args()
    json_drones = []
    json_packages = []

    now = int(time.time())  # used as reference time for the dispatch plan.

    # return if either listings are unavailable.
    rd = requests.get(args.drones)
    if rd.status_code != 200:
        return
    print('Got listing: drones.')
    rp = requests.get(args.packages)
    if rp.status_code != 200:
        return
    print('Got listing: packages.')

    tbegin = time.process_time()
    json_drones = rd.json()
    json_packages = rp.json()

    drones = enque_drones(json_drones, now)
    packages = enque_packages(json_packages, now)
    dispatch_plan = assign_packages(drones, packages)
    tend = time.process_time()

    import pprint
    pprint.pprint(dispatch_plan, compact=True)
    print('process time = {0:.5} s.'.format(tend - tbegin))


if __name__ == '__main__':
    import sys
    sys.exit(main())
