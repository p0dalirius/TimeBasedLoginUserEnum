#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : app.py
# Author             : Podalirius (@podalirius_)
# Date created       : 9 Mar 2022

import time
import random
from flask import Flask, request

app = Flask(__name__)


@app.route("/login", methods=["GET", "POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    if username in ["admin", "podalirius"]:
        time.sleep(random.randint(190, 200) / 1000)  # Simulate response time of heavy app
        if password == "V3ryS3cur3":
            return {
                "success": True,
                "message": "Redirecting to /home/ ..."
            }
        else:
            return {
                "success": False,
                "message": "Invalid username or password."
            }
    else:
        return {
            "success": False,
            "message": "Invalid username or password."
        }


if __name__ == '__main__':
    app.run(host="0.0.0.0")
