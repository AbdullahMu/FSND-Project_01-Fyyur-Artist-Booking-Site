#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.orm import load_only
from sqlalchemy import func, and_
from sqlalchemy.inspection import inspect

#----------------------------------------------------------------------------#
# app Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

# load configurations from config.py
app.config.from_object('config')

# Alternatively, set configurations manually:
'''
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
'''
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    description = db.Column(db.String(500), default='')
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    website = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy='dynamic')

    # def __repr__(self) -> str:
    #     table = inspect(self)
    #     key_value_pairs = " ".join([f"{attribute.key}={attribute.loaded_value!r}"
    #                       for attribute in table.attrs])
    #     return f"<Venue {key_value_pairs}>"
    def __repr__(self) -> str:
        return f'<Venue id: {self.id}, \
        name: {self.name}, \
        city: {self.city}, \
        state: {self.state}, \
        image_link: {self.image_link}, \
        address: {self.address}, \
        phone: {self.phone}, \
        facebook_link: {self.facebook_link}, \
        description: {self.description}, \
        seeking_talent: {self.seeking_talent}, \
        website: {self.website}, \
        genres: {self.genres}>'

    def as_dictionary(self) -> dict:
        '''
        '''
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'image_link': self.image_link,
            'address': self.address,
            'phone': self.phone,
            'facebook_link': self.facebook_link,
            'description': self.description,
            'seeking_talent': self.seeking_talent,
            'website': self.website,
            'genres': self.genres
        }

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref="artist", lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Artist id: {self.id}, \
        name: {self.name}, \
        city: {self.city}, \
        state: {self.state}, \
        phone: {self.phone}, \
        image_link: {self.image_link}, \
        genres: {self.genres}, \
        facebook_link: {self.facebook_link}, \
        seeking_venue: {self.seeking_venue}, \
        seeking_description: {self.seeking_description}>'

    def as_dictionary(self) -> dict:
        '''
        '''
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'image_link': self.image_link,
            'genres': self.genres,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description
        }


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__= 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self) -> str:
        return f'<Show id: {self.id}, \
        artist_id: {self.artist_id}, \
        venue_id: {self.venue_id}, \
        start_time: {self.start_time}>'

    def as_dictionary(self) -> dict:
        return {
            'id': self.id,
            'artist_id': self.artist_id,
            'venue_id': self.venue_id,
            'start_time': self.start_time
            }
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  # a query on Venues table aggregated by city and state names (areas)
    distinct_areas = Venue.query.options(load_only('city', 'state')).with_entities(Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()
# options(load_only(
    data = list()
    current_time = datetime.now()

  #loop over all areas to check for upcoming shows
    for area in distinct_areas:
        area_data = dict()
        area_data['city'], area_data['state'] = area
        venues = Venue.query.filter_by(city=area_data['city']).filter_by(state=area_data['state']).all()
        area_data['venues'] = [{
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": db.session.query(Show).filter(Show.venue_id==venue.id, Show.start_time>current_time).all()[0][0]
                  } for venue in venues]
        data.append(area_data)

    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # parse search term and use it for filter the query
    search_term = request.form.get('search_term', '')
    venue_search_result = db.session.query(Venue).options(load_only('id', 'name')).filter(Venue.name.like(f'%{search_term}%')).all()
    response = dict()
    response['count'] = len(venue_search_result)
    data = list()
    current_time = datetime.now()

  # loop over all search results from returned query and append it to list
    for venue in venue_search_result:
        venue_response = dict()
        venue_response['id'], venue_response['name'] = venue.id, venue.name
        upcoming_shows = db.session.query(Show).filter(and_(Show.venue_id == venue.id, Show.start_time > current_time)).all()
        venue_response['num_upcoming_shows'] = len(upcoming_shows)
        data.append(venue_response)

 # parse response dictionary
    response['data'] = data

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

    # query venues table by input venue_id
    venue = Venue.query.get(venue_id)

    current_time = datetime.now()

    # find past and upcoming shows using input venue_id and current time to filter query on showw table
    shows_query = db.session.query(Show).join(Artist).with_entities(Show.artist_id, Artist.name, Artist.image_link, Show.start_time).filter(Show.venue_id == venue_id).all()

    past_shows = list()
    upcoming_shows = list()

    shows_query_attributes = shows_query[0]._asdict().keys()

    for show in shows_query:
        shows_data = dict()
        for attribute in shows_query_attributes:
            if attribute in ['name', 'image_link']:
                shows_data['artist_' + attribute] = show._asdict()[attribute]
            else:
                shows_data[attribute] = show._asdict()[attribute]

        if show.start_time > current_time:
            upcoming_shows.append(shows_data)
        else:
            past_shows.append(shows_data)

     data = dict()

     # parse returned data dictionary
     data = {
       "id": venue.id,
       "name": venue.name,
       "genres": venue.genres,
       "address": venue.address,
       "city": venue.city,
       "state": venue.state,
       "phone": venue.phone,
       "website": venue.website,
       "facebook_link": venue.facebook_link,
       "seeking_talent": venue.seeking_talent,
       "seeking_description": venue.seeking_description,
       "image_link": venue.image_link,
       "past_shows": past_shows,
       "upcoming_shows": upcoming_shows,
       "past_shows_count": len(past_shows),
       "upcoming_shows_count": len(upcoming_shows),
     }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


# parse the entry of the venue table
data = dict()
venue_table_attributes = inspect(Venue).c
for attribute in venue_table_attributes:
    if attribute.name == 'genres':
        data[attribute.name] = request.form.getlist(attribute.name)
    elif attribute.name == 'seeking_talent':
        data[attribute.name] = bool(request.form[attribute.name])
    else:
        data[attribute.name] = request.form[attribute.name]
 # initialize an error handling variable to capture any error and exceptions in the following the try statement
  error = False

  try:
    venue = Venue(**data)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + data['name'] + ' was successfully listed!')

except Exception as error:
 # rollback pending changes on error
    db.session.rollback()
    flash('An error occurred. Venue ' + data['name'] + ' could not be listed.')

  finally:
 # close current session
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
 # retrieve entry of the venue table by input venue_id and delete it
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash(f'Venue {venue_id} was successfully deleted.')

  except Exception as error:
# rollback pending changes on error
    db.session.rollback()
    flash(f'An error occurred. Venue {venue_id} could not be deleted.')

  finally:
# close curent session
    db.session.close()

  return None

'''
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None
'''

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  # retrieve all entries in artist table
  artists_data = db.session.query(Artist).with_entities(Artist.id, Artist.name).all()
  data =  [{'id': artist.id, 'name': artist.name} for artist in artists_data]

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  # parse search term and use it for filter the query
  search_term = request.form.get('search_term', '')
  search_result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()

  data = []

  # loop over all search results from returned query and append it to list
  for result in search_result:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == result.id).filter(Show.start_time > datetime.now()).all()),
    })

  # parse response dictionary
  response={
    "count": len(search_result),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # query artist table by input artist_id
  artist_query = db.session.query(Artist).get(artist_id)

  # return 404 error for empty query
  if not artist_query:
    return render_template('errors/404.html')

  # find past shows and upcoming using input artist_id and current time to filter query on showw table
  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()

  # loop over all past shows results from returned query and append it to list
  past_shows = []

  for show in past_shows_query:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  # loop over all upcoming shows results from returned query and append it to list
  upcoming_shows = []

  for show in upcoming_shows_query:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  # parse returned data dictionary
  data = {
    "id": artist_query.id,
    "name": artist_query.name,
    "genres": artist_query.genres,
    "city": artist_query.city,
    "state": artist_query.state,
    "phone": artist_query.phone,
    "website": artist_query.website,
    "facebook_link": artist_query.facebook_link,
    "seeking_venue": artist_query.seeking_venue,
    "seeking_description": artist_query.seeking_description,
    "image_link": artist_query.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # populate form with fields from artist with ID <artist_id>
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  if artist:
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  # initialize an error handling variable to capture any error and exceptions in the following the try statement
  error = False

  # retrieve artist record from artist table with input artist_id
  artist = Artist.query.get(artist_id)

  try:
    # update existing record attributes with input values from submitted form by assigning it to retrieved ORM object
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.seeking_description = request.form['seeking_description']

    # commit ORM object changes to database
    db.session.commit()

  except:
    # rollback pending changes on error
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    # close current session and parse submission message
    db.session.close()
  if error:
    flash('An error occurred. Artist could not be changed.')
  if not error:
    flash('Artist was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # populate form with fields from venue with ID <venue_id>
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue:
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  # initialize an error handling variable to capture any error and exceptions in the following the try statement
  error = False

  # retrieve venue record from venue table with input venue_id
  venue = Venue.query.get(venue_id)

  try:
  # update existing record attributes with input values from submitted form by assigning it to retrieved ORM object
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False
    venue.seeking_description = request.form['seeking_description']

    # commit ORM object changes to database
    db.session.commit()

  except:
    # rollback pending changes on error
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    # close curent session and parse venue update submission message
    db.session.close()
  if error:
    flash(f'An error occurred. Venue could not be changed.')
  if not error:
    flash(f'Venue was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # initialize an error handling variable to capture any error and exceptions in the following the try statement
  error = False

  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres'),
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website = request.form['website']
    seeking_venue = True if 'seeking_venue' in request.form else False
    seeking_description = request.form['seeking_description']

    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
  # close current session
    db.session.close()

  # on successful db insert, flash success
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name']+ ' could not be listed.')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  # perform left joins on show table with other tables to get info about all shows
  shows_query = db.session.query(Show).join(Artist).join(Venue).all()

  data = []

  # loop over retrieved shows info and append data from ORM object to list
  for show in shows_query:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # initialize an error handling variable to capture any error and exceptions in the following the try statement
  error = False

  try:
  # assign submitted values to attributes
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    print(request.form)

  # parse the entry from submitted values by creating an ORM object then insert it to database
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()

  except:
  # rollback pending changes on error
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
  # close curent session
    db.session.close()

  # on successful db insert, flash success
  if not error:
      flash('Show was successfully listed!')
  else:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Show could not be listed.')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
