import os
from flask import Flask

random_string = os.urandom(24)

app = Flask(__name__)
app.secret_key = random_string
