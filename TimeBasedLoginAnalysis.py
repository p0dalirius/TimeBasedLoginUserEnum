#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : TimeBasedLoginUserEnum.py
# Author             : Podalirius (@podalirius_)
# Date created       : 9 Mar 2022

import argparse
import re
import requests
import random
import string
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor


def trylogin(username, statistics):
    """Documentation for trylogin"""
    session = requests.Session()
    r = session.post(
        "http://127.0.0.1:5000/login",
        data={
            "username": username,
            "password": "DummyPassword"
        }
    )
    statistics[username].append(r.elapsed.total_seconds() * 1000)
    return r.elapsed.total_seconds() * 1000


def parseArgs():
    print("TimeBasedLoginAnalysis v1.1 - by @podalirius_\n")

    parser = argparse.ArgumentParser(description="Enumerate valid usernames based on the requests response times.")
    parser.add_argument("-u", "--username", default=None, required=True, help='Username')
    parser.add_argument("-t", "--threads", dest="threads", action="store", type=int, default=4, required=False, help="Number of threads (default: 4)")
    parser.add_argument("-s", "--samples", dest="samples", action="store", type=int, default=20, required=False, help="Number of login tries (default: 20)")
    parser.add_argument("-v", "--verbose", default=False, action="store_true", help='Verbose mode. (default: False)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-S", "--show", default=None, action="store_true", help='Show graph')
    group.add_argument("-f", "--file", default=None, help='Output image graph.')
    return parser.parse_args()


if __name__ == '__main__':
    options = parseArgs()

    random_username = ''.join([random.choice(string.ascii_letters) for k in range(len(options.username))])
    print("[>] Using random username '%s'" % random_username)

    statistics = {random_username: [], options.username: []}

    print("[>] Trying %d logins with '%s'" % (options.samples, random_username))
    # Waits for all the threads to be completed
    with ThreadPoolExecutor(max_workers=min(options.threads, options.samples)) as tp:
        for k in range(options.samples):
            tp.submit(trylogin, random_username, statistics)
    average_rand_user = sum(statistics[random_username]) / len(statistics[random_username])
    print("   [+] Average response time for random user = %f ms" % average_rand_user)

    print("[>] Trying %d logins with '%s'" % (options.samples, options.username))
    # Waits for all the threads to be completed
    with ThreadPoolExecutor(max_workers=min(options.threads, options.samples)) as tp:
        for k in range(options.samples):
            tp.submit(trylogin, options.username, statistics)
    average_real_user = sum(statistics[options.username]) / len(statistics[options.username])
    print("   [+] Average response time for real user = %f ms" % average_real_user)


    diff = (average_rand_user - average_real_user)
    if diff < 0:
        print("[+] A login with a real username was %f ms slower than a random username on an average of %d tries." % (abs(diff), options.samples))
    else:
        print("[+] A login with a random username was %f ms faster than a real username on an average of %d tries." % (abs(diff), options.samples))

    if options.show is not None or options.file is not None:
        plt.plot(
            [x for x in range(len(statistics[random_username]))],
            statistics[random_username],
            color='red'
        )
        plt.fill_between([x for x in range(len(statistics[random_username]))], [average_rand_user for x in range(len(statistics[random_username]))], step="pre", alpha=0.25, color='red')

        plt.plot(
            [x for x in range(len(statistics[options.username]))],
            statistics[options.username],
            color='blue'
        )
        plt.fill_between([x for x in range(len(statistics[options.username]))], [average_real_user for x in range(len(statistics[options.username]))], step="pre", alpha=0.25, color='blue')

        plt.legend([random_username, None, options.username, None])
        plt.grid()

        if options.file is not None:
            print("[>] Saving graph to %s" % options.file)
            plt.savefig(options.file, dpi=600)
        elif options.show is not None:
            print("[>] Showing graph")
            plt.show()
