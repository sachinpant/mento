#! engine/bin/python2.7

from flask import Flask
app = Flask(__name__)

@app.route('/')
def invalid_call():
    return 'Mento has to be accessed using REST API calls.'

if __name__ == '__main__':
    app.run(port=1337, host='0.0.0.0')
