#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)


# TODO: connect to a local postgresql database
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    genres = db.Column(db.ARRAY(db.String()))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show',backref='Venue',lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.address}{self.phone}{self.image_link}{self.facebook_link}{self.shows}{self.seeking_talent}{self.seeking_description}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show',backref='Artist',lazy=True)

    def __repr__(self):
        return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.phone}{self.genres}{self.shows}{self.facebook_link}{self.image_link} {self.seeking_venue}{self.seeking_description}>'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate
class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer , db.ForeignKey(Venue.id), nullable=False)
  artist_id = db.Column(db.Integer , db.ForeignKey(Artist.id) , nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)
  def upcoming_shows_query():
    upcoming_shows_query = Show.query.filter(Show.venue_id ==   Venue.id).filter(Show.start_time > datetime.now()).all()
    return upcoming_shows_query
    
  def past_shows_query():
    past_shows_query = Show.query.filter(Show.venue_id == Venue.id).filter(Show.start_time < datetime.now()).all()
    return past_shows_query


  def __repr__(self):
        return f'<Show {self.id} {self.venue_id} {self.artist_id} {self.start_time} >'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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

  cities = Venue.query.group_by(Venue.city,Venue.state,Venue.id).all() 
  data=[]
  for venue_city in cities:
    venue_info = []
    # appending info about city , state ,  and venues at each city to the end point 
    data.append({
      "city": venue_city.city,
      "state": venue_city.state, 
      "venues": venue_info
    })
    venues = Venue.query.filter_by(state=venue_city.state,city=venue_city.city).all()
    for venue in venues:  # appending data about each venue in the city 
      venue_info.append({
        "id": venue.id,
        "name": venue.name, 
        "num_upcoming_shows": len(Show.upcoming_shows_query())
      })
    
  
  
  return render_template('pages/venues.html',areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()

  result={
    "count": len(venues),
    "data": []
  }

  for venue in venues:
    result['data'].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(Show.upcoming_shows_query())
    })
  
  
  return render_template('pages/search_venues.html', results=result, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  venue = db.session.query(Venue).get(venue_id)
  venue_shows = venue.shows
  upcomingShowsList = []
  pastShowsList = []

  for show in venue_shows:
    show_data = { 
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    # using the upcoming_show_query method in Show model to filter shows and appending show_info to the upcomigShowsList
    if (show.upcoming_shows_query):
      upcomingShowsList.append(show_data)
    #if it's not an upcoming show append show_data to the pastShowsList  
    else:
      pastShowsList.append(show_data)

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
    "past_shows": pastShowsList,
    "upcoming_shows": upcomingShowsList,
    "past_shows_count": len(pastShowsList),
    "upcoming_shows_count": len(upcomingShowsList),
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
  error = False

  try: 
    name = request.form.get('name','')
    city = request.form.get('city','')
    state = request.form.get('state','')
    address = request.form.get('address','')
    phone = request.form.get('phone','')
    genres = request.form.getlist('genres')
    image_link = request.form.get('image_link','')
    facebook_link = request.form.get('facebook_link','')
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error: 
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + request.form.get('name','')+ ' could not be listed.')
    if not error: 
      flash('Venue ' + request.form.get('name','') + ' was successfully listed!')
  return render_template('pages/home.html')
      
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error:False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error: 
      flash(f'An error occurred. Venue {venue_id} could not be deleted.')
    if not error: 
      flash(f'Venue {venue_id} was successfully deleted.')
  return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  results = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  data = []
  response={
    "count": len(results),
    "data": data
  }

  for result in results:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(Show.upcoming_shows_query()),
    })
 
 
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  artist_shows = artist.shows
  pastShowsList = []
  upcomingShowsList = []

  for show in artist_shows:
    show_data ={
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "artist_image_link": show.Venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    # if the artist show is yet to come ,append the show data to the upcomingShowsList
    if (show.upcoming_shows_query):
      upcomingShowsList.append(show_data)
      # if the artist show is done , append the show data to the upcomingShowsList
    else:
      pastShowsList.append(show_data)

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": pastShowsList,
    "upcoming_shows": upcomingShowsList,
    "past_shows_count": len(pastShowsList),
    "upcoming_shows_count": len(upcomingShowsList),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  if artist: 
    artist.name = request.form.get('name','') 
    artist.city = request.form.get('city','')
    artist.state = request.form.get('state','')
    artist.phone = request.form.get('phone','')
    artist.genres = request.form.getlist('genres','')
    artist.facebook_link = request.form.get('facebook_link','')
    artist.image_link = request.form.get('image_link','')
    artist.website = request.form.get('website','')
    artist.seeking_venue = request.form.get('seeking_venue','')
    artist.seeking_description = request.form.get('seeking_description','')
  #artist={
    
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  error = False  
  artist = Artist.query.get(artist_id)

  try: 
    artist.name = request.form.get('name','')
    artist.city = request.form.get('city','')
    artist.state = request.form.get('state','')
    artist.phone = request.form.get('phone','')
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form.get('image_link','')
    artist.facebook_link = request.form.get('facebook_link','')
    artist.website = request.form.get('website','')
    artist.seeking_venue = True if 'seeking_venue' in request.form else False 
    artist.seeking_description = request.form.get('seeking_description','')

    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Artist could not be changed.')
  if not error: 
    flash('Artist was successfully updated!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue: 
    venue.name = request.form.get('name','') 
    venue.city = request.form.get('city','')
    venue.state = request.form.get('state','')
    venue.phone = request.form.get('phone','')
    venue.genres = request.form.getlist('genres','')
    venue.facebook_link = request.form.get('facebook_link','')
    venue.image_link = request.form.get('image_link','')
    venue.website = request.form.get('website','')
    venue.seeking_talent = request.form.get('seeking_talent','')
    venue.seeking_description = request.form.get('seeking_description','')
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False  
  venue = Venue.query.get(venue_id)

  try: 
    venue.name = request.form.get('name','')
    venue.city = request.form.get('city','')
    venue.state = request.form.get('state','')
    venue.address = request.form.get('address','')
    venue.phone = request.form.get('phone','')
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form.get('image_link','')
    venue.facebook_link = request.form.get('facebook_link','')
    venue.website = request.form.get('website','')
    venue.seeking_talent = True if 'seeking_talent' in request.form else False 
    venue.seeking_description = request.form.get('seeking_description','')
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
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
  error = False
  try: 
    name = request.form.get('name','')
    city = request.form.get('city','')
    state = request.form.get('state','')
    phone = request.form.get('phone','')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link','')
    image_link = request.form.get('image_link','')
    website = request.form.get('website','')
    seeking_venue = True if 'seeking_venue' in request.form else False
    seeking_description = request.form.get('seeking_description','')

    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
     # TODO: on unsuccessful db insert, flash an error instead.
     flash('An error occurred. Artist ' + request.form.get('name','')+ ' could not be listed.')
  if not error: 
     # on successful db insert, flash success
     flash('Artist ' + request.form.get('name','') + ' was successfully listed!')
  return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows=Show.query.all()
  data = []
  for show in shows: 
    if(show.upcoming_shows_query):
      data.append({
        "venue_id": show.venue_id,
        "venue_name": show.Venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.Artist.name, 
        "artist_image_link": show.Artist.image_link,
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
  error = False
  try: 
    artist_id = request.form.get('artist_id','')
    venue_id = request.form.get('venue_id','')
    start_time = request.form.get('start_time','')
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  if not error: 
    # on successful db insert, flash success
    flash('Show was successfully listed!')
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
