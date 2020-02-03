from flask import Flask, request, session, redirect, url_for
from datetime import datetime
from cas import CASClient

app = Flask(__name__)

app.secret_key = 'V7nlCN90LPHOTA9PGGyf'

cas_client = CASClient(
    version=3,
    service_url='http://localhost:5000/profile',
    server_url='https://django-cas-ng-demo-server.herokuapp.com/cas/'
    )

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/profile')
def profile(method=['GET']):
    if 'username' in session:
        return 'Already logged as %s. <a href="/logout">Logout</a>' % session['username']

    ticket = request.args.get('ticket')
    if not ticket:
        return 'User is not logged in. <a href="/login">Login</a>'

    app.logger.debug('ticket: %s', ticket)

    user, attributes, pgtiou = cas_client.verify_ticket(ticket)

    app.logger.debug('user: %s, attributes: %s, pgtiou: %s', user, attributes, pgtiou)

    if not user:
        return 'Failed to verify ticket. <a href="/login">Login</a>'
    else:
        session['username'] = user
        return 'Logged in user: %s. <a href="/logout">Logout</a>' % user

@app.route('/login')
def login():
    cas_login_url = cas_client.get_login_url()
    app.logger.debug('cas_login_url: %s', cas_login_url)
    return redirect(cas_login_url)

@app.route('/logout')
def logout():
    cas_logout_url = cas_client.get_logout_url(url_for('logout_callback', _external=True))
    app.logger.debug('cas_logout_url: %s', cas_logout_url)

    return redirect(cas_logout_url)

@app.route('/logout_callback')
def logout_callback():
    session.pop('username', None)
    return 'Logged out from CAS. <a href="/login">Login</a>'
