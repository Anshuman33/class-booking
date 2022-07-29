from flask import Flask, request, jsonify
from json import load


app = Flask(__name__)


if __name__ == '__main__':
    app.run()