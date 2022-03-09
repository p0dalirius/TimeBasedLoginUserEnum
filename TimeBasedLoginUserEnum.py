#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : TimeBasedLoginUserEnum.py
# Author             : Podalirius (@podalirius_)
# Date created       : 9 Mar 2022

import argparse
import requests
import random
import string
from concurrent.futures import ThreadPoolExecutor
from rich.progress import track


def trylogin(username, results):
    """Documentation for trylogin"""
    session = requests.Session()
    try:
        r = session.post(
            "http://127.0.0.1:5000/login",
            data={
                "username": username,
                "password": "DummyPassword"
            }
        )
        results[username].append(r.elapsed.total_seconds() * 1000)
        return r.elapsed.total_seconds() * 1000
    except Exception as e:
        print("   [error] %s" % e)
        return 0


def average_response_time(username, threads=4, samples=100):
    # Waits for all the threads to be completed
    results = {username: []}
    with ThreadPoolExecutor(max_workers=min(threads, samples)) as tp:
        for k in range(samples):
            tp.submit(trylogin, username, results)
    if len(results[username]) != 0:
        rtime = sum(results[username]) / len(results[username])
        return rtime
    else:
        return None


def parseArgs():
    print("TimeBasedLoginUserEnum v1.1 - by @podalirius_\n")

    parser = argparse.ArgumentParser(description="Enumerate valid usernames based on the requests response times.")
    parser.add_argument("-u", "--username", default=None, required=True, help='Username')
    parser.add_argument("-f", "--usernames-file", default=None, required=True, help='File containing list of usernames to test.')
    parser.add_argument("-t", "--threads", dest="threads", action="store", type=int, default=4, required=False, help="Number of threads (default: 4)")
    parser.add_argument("-s", "--samples", dest="samples", action="store", type=int, default=20, required=False, help="Number of login tries (default: 20)")
    parser.add_argument("-o", "--outfile", default=None, required=False, help='Output file for valid usernames.')
    parser.add_argument("-v", "--verbose", default=False, action="store_true", help='Verbose mode. (default: False)')
    parser.add_argument("--no-colors", default=False, action="store_true", help='Disables colored output mode.')
    return parser.parse_args()


if __name__ == '__main__':
    options = parseArgs()

    print("[>] Autodetecting time difference between valid and random usernames ...")

    random_username = ''.join([random.choice(string.ascii_letters) for k in range(len(options.username))])

    statistics = {random_username: [], options.username: []}

    print("   [>] Trying %d logins with random user '%s'" % (options.samples, random_username))
    average_rand_user = average_response_time(random_username, threads=options.threads, samples=options.samples)
    if average_rand_user is None:
        exit()
    print("      [+] Average response time for random user = %f ms" % average_rand_user)

    print("   [>] Trying %d logins with '%s'" % (options.samples, options.username))
    average_real_user = average_response_time(options.username, threads=options.threads, samples=options.samples)
    if average_real_user is None:
        exit()
    print("      [+] Average response time for real user = %f ms" % average_real_user)

    diff = (average_rand_user - average_real_user)
    if diff < 0:
        print("[+] A login with a real username was %f ms slower than a random username on an average of %d tries." % (abs(diff), options.samples))
    else:
        print("[+] A login with a random username was %f ms faster than a real username on an average of %d tries." % (abs(diff), options.samples))

    # Preparing margins

    # Now, bruteforce with time based output
    f = open(options.usernames_file, "r")
    usernames_list = [l.strip() for l in f.readlines()]
    f.close()

    if options.outfile is not None:
        f = open(options.outfile, "w")

    print("[>] Loaded %d usernames to test." % len(usernames_list))

    for test_username in track(usernames_list, description="Testing usernames"):
        # Waits for all the threads to be completed
        avg_resp = average_response_time(test_username, threads=options.threads, samples=options.samples)

        distance_to_real, distance_to_random = abs(average_real_user - avg_resp), abs(average_rand_user - avg_resp)
        if distance_to_real < distance_to_random:
            if options.outfile is not None:
                f.write(test_username+"\n")
            if options.no_colors:
                print("   [+] Valid user found: '%s'" % test_username)
            else:
                print("   \x1b[92m[+] Valid user found: '%s'\x1b[0m" % test_username)
            if options.verbose:
                print("      [>] Average response time for user '%s' is %f ms" % (test_username, avg_resp))
        else:
            if options.verbose:
                if options.no_colors:
                    print("   [+] User '%s' is invalid." % test_username)
                else:
                    print("   \x1b[91m[+] User '%s' is invalid.\x1b[0m" % test_username)
                print("      [>] Average response time for user '%s' is %f ms" % (test_username, avg_resp))

    if options.outfile is not None:
        f.close()
