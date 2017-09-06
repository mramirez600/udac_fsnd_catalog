from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Artist


engine = create_engine('sqlite:///musicartists.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


app = Flask(__name__)


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
    # return "This page will show all my restaurants"
    return render_template('genres.html', genre=genre)


# Create a new genre
@app.route('/genre/new/', methods=['GET', 'POST'])
def newGenre():
    if request.method == 'POST':
        newGenres = Genre(name=request.form['name'])
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
@app.route('/genre/<int:genre_id>/')
def genrelist(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    items = session.query(Artist).filter_by(genre_id = genre.id)
    return render_template('artist.html', genre=genre, items = items)

@app.route('/genre/<int:genre_id>/<int:artist_id>/detail/', methods=['GET', 'POST'])
def detailArtist(genre_id, artist_id):
    details = session.query(Artist).filter_by(id=artist_id).one()
    return render_template('artist_details.html', genre_id = genre_id, artist_id = artist_id, i = details)



@app.route('/genre/<int:genre_id>/new/', methods=['GET', 'POST'])
def newArtist(genre_id):
    if request.method == 'POST':
        newAct = Artist(name=request.form['name'], genre_id=genre_id)
        session.add(newAct)
        session.commit()
        flash('new artist created')
        return redirect(url_for('genrelist', genre_id=genre_id))
    else:
        return render_template('new_artist.html', genre_id=genre_id)

@app.route('/genre/<int:genre_id>/<int:artist_id>/edit/', methods=['GET', 'POST'])
def editArtist(genre_id, artist_id):
    editedArtist = session.query(Artist).filter_by(id = artist_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedArtist.name = request.form['name']
        if request.form['bio']:
            editedArtist.bio = request.form['bio']
        if request.form['album']:
            editedArtist.album = request.form['album']
        if request.form['release_year']:
            editedArtist.release_year = request.form['release_year']
        session.add(editedArtist)
        session.commit()
        flash('artist has been edited')
        return redirect(url_for('genrelist', genre_id = genre_id))
    else:
        return render_template('edit_artist.html', genre_id = genre_id, artist_id = artist_id, i = editedArtist)


@app.route('/genre/<int:genre_id>/<int:artist_id>/delete/', methods=['GET', 'POST'])
def deleteArtist(genre_id, artist_id):
    delArtist = session.query(Artist).filter_by(id=artist_id).one()
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
