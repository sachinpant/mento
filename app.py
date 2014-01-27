#! engine/bin/python2.7

from flask import Flask
app = Flask(__name__)

@app.route('/')
def invalid_call():
    return 'Mento has to be accessed using REST API calls.'

@app.route('/manage/refresh')
def refresh_library():
    print 'Refreshing music library...'

@app.errorhandler(404)
def page_not_found(error):
    return 'Invalid call.'

@app.errorhandler(500)
def internal_server_error(error):
    return 'Invalid call.'

if __name__ == '__main__':
    app.run(port=1337, host='0.0.0.0')
