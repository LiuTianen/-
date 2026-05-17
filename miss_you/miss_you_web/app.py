'''
Date: 2026-05-17 23:49:11
LastEditors: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
LastEditTime: 2026-05-17 23:49:56
FilePath: \-\miss_you\miss_you_web\app.py
Description: 

Copyright (c) 2026 by ${git_name_email}, All Rights Reserved. 
'''
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)