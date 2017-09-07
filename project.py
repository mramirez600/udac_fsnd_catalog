from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Artist, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

engine = create_engine('sqlite:///musicartistsv2.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None



@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


#API
@app.route('/genre/<int:genre_id>/artists/JSON')
def genreArtistJSON(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    items = session.query(Artist).filter_by(
        genre_id = genre.id).all()
    return jsonify(Artist=[i.serialize for i in items])

# ADD JSON ENDPOINT HERE
@app.route('/genre/<int:genre_id>/artists/<int:artist_id>/JSON')
def artistJSON(genre_id, artist_id):
    artistListed = session.query(Artist).filter_by(id=artist_id).one()
    return jsonify(Artist=artistListed.serialize)

@app.route('/genre/JSON')
def genreJSON():
    genre = session.query(Genre).all()
    return jsonify(genre=[r.serialize for r in genre])


# Show all genres
@app.route('/')
@app.route('/genre/')
def showGenres():
    genre = session.query(Genre).all()
    if 'username' not in login_session:
        return render_template('publicgenre.html', genre=genre)
    else:
        return render_template('genres.html', genre=genre)
    


# Create a new genre
@app.route('/genre/new/', methods=['GET', 'POST'])
def newGenre():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newGenres = Genre(name=request.form['name'], user_id=login_session['user_id'])
        session.add(newGenres)
        session.commit()
        return redirect(url_for('showGenres'))
    else:
        return render_template('new_genre.html')
    # return "This page will be for making a new restaurant"

# Edit a genre


@app.route('/genre/<int:genre_id>/edit/', methods=['GET', 'POST'])
def editGenre(genre_id):
    editedGenre = session.query(
        Genre).filter_by(id=genre_id).one()
    if 'username' not in login_session:
        return redirect('/login')  
    if editedGenre.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this restaurant. Please create your own restaurant in order to edit.');}</script><body onload='myFunction()''>"      
    if request.method == 'POST':
        if request.form['name']:
            editedGenre.name = request.form['name']
            session.add(editedGenre)
            session.commit()
            return redirect(url_for('showGenres'))
    else:
        return render_template(
            'edit_genre.html', genre=editedGenre)

    # return 'This page will be for editing restaurant %s' % restaurant_id

# Delete a genre


@app.route('/genre/<int:genre_id>/delete/', methods=['GET', 'POST'])
def deleteGenre(genre_id):
    delGenre = session.query(
        Genre).filter_by(id=genre_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if delGenre.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this restaurant. Please create your own restaurant in order to edit.');}</script><body onload='myFunction()''>"      
    if request.method == 'POST':
        session.delete(delGenre)
        session.commit()
        return redirect(
            url_for('showGenres', genre_id=genre_id))
    else:
        return render_template(
            'delete_genre.html', genre=delGenre)
    # return 'This page will be for deleting restaurant %s' % restaurant_id



#@app.route('/')
@app.route('/genre/<int:genre_id>/artists/')
def genrelist(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    creator = getUserInfo(genre.user_id)
    items = session.query(Artist).filter_by(genre_id = genre.id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicartists.html', items=items, genre=genre, creator=creator)
    else:
        return render_template('artist.html', genre=genre, items = items, creator=creator)

@app.route('/genre/<int:genre_id>/artists/<int:artist_id>/details/', methods=['GET', 'POST'])
def detailArtist(genre_id, artist_id):
    details = session.query(Artist).filter_by(id=artist_id).one()
    if 'username' not in login_session:
        return render_template('artist_public_details.html', genre_id = genre_id, artist_id = artist_id, i = details)
    else:
        return render_template('artist_details.html', genre_id = genre_id, artist_id = artist_id, i = details)



@app.route('/genre/<int:genre_id>/new/', methods=['GET', 'POST'])
def newArtist(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    currentGenre = session.query(Genre).filter_by(id=genre_id).one()
    if login_session['user_id'] != currentGenre.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add menu items to this restaurant. Please create your own restaurant in order to add items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newAct = Artist(name=request.form['name'], bio=request.form['bio'], album=request.form['album'], 
        albumImg=request.form['albumImg'], wikiLink=request.form['wikiLink'], release_year=request.form['release_year'], 
        genre_id=genre_id, user_id=currentGenre.user_id)
        session.add(newAct)
        session.commit()
        flash('new artist created')
        return redirect(url_for('genrelist', genre_id=genre_id))
    else:
        return render_template('new_artist.html', genre_id=genre_id)

@app.route('/genre/<int:genre_id>/<int:artist_id>/edit/', methods=['GET', 'POST'])
def editArtist(genre_id, artist_id):
    editedArtist = session.query(Artist).filter_by(id = artist_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if login_session['user_id'] != editedArtist.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit menu items to this restaurant. Please create your own restaurant in order to edit items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedArtist.name = request.form['name']
        if request.form['bio']:
            editedArtist.bio = request.form['bio']
        if request.form['album']:
            editedArtist.album = request.form['album']
        if request.form['albumImg']:
            editedArtist.albumImg = request.form['albumImg']
        if request.form['release_year']:
            editedArtist.release_year = request.form['release_year']
        if request.form['wikiLink']:
            editedArtist.wikiLink = request.form['wikiLink']
        session.add(editedArtist)
        session.commit()
        flash('artist has been edited')
        return redirect(url_for('genrelist', genre_id = genre_id))
    else:
        return render_template('edit_artist.html', genre_id = genre_id, artist_id = artist_id, i = editedArtist)


@app.route('/genre/<int:genre_id>/<int:artist_id>/delete/', methods=['GET', 'POST'])
def deleteArtist(genre_id, artist_id):
    
    if 'username' not in login_session:
        return redirect('/login')
    delArtist = session.query(Artist).filter_by(id=artist_id).one()
    if login_session['user_id'] != delArtist.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete menu items to this restaurant. Please create your own restaurant in order to delete items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(delArtist)
        session.commit()
        flash('artist has been deleted')
        return redirect(url_for('genrelist', genre_id = genre_id))
    else:
        return render_template('delete_artist.html', item=delArtist)




if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
