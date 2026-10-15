import re
from flask import Flask, render_template, request, flash, url_for, redirect 

from wtforms import Form, StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, DataRequired, ValidationError, EqualTo

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask( __name__ )
app.config[ 'SECRET_KEY' ] = 'mysecretkey'
app.config[ 'SQLALCHEMY_DATABASE_URI' ] = 'sqlite:///users.db'

db = SQLAlchemy( app )
migrate = Migrate( app, db )

def validate_email(form, field):
  if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", field.data):
    raise ValidationError('Please enter a valid email address')


class Namer( Form ):  
  name = StringField( 'Name', validators=[ InputRequired() ] )
  email = StringField( 'Email', validators=[ InputRequired(), validate_email ] )
 # password = PasswordField( 'Password', validators=[ InputRequired(), Length( min=6, max=20 ) ] )
  submit = SubmitField( 'Submit' )


class UserForm( Form ):
  name = StringField( 'Name', validators=[ InputRequired() ] )
  email = StringField( 'Email', validators=[ InputRequired(), validate_email ] )
  color  = StringField( 'Favorite Color' )
  password_hash = PasswordField( 'Password', validators=[ InputRequired(), Length( min=6, max=20 ), EqualTo('password_hash2', message='Passwords must match') ] )
  password_hash2 = PasswordField( 'Confirm Password', validators=[ InputRequired(), Length( min=6, max=20 ) ] )
  submit = SubmitField( 'Submit' )


class Users( db.Model ):
  id = db.Column( db.Integer, primary_key=True )
  name = db.Column( db.String(100), nullable=False )
  email = db.Column( db.String(120), nullable=False, unique=True )
  color = db.Column( db.String(20))
  date_added = db.Column( db.DateTime, default=lambda: datetime.now(timezone.utc) )

  password_hash = db.Column( db.String(128) )

  @property
  def password( self ):
    raise AttributeError( 'Password is not a readable attribute!' )

  @password.setter
  def password( self, password ):
    self.password_hash = generate_password_hash( password )

  def verify_password( self, password ):
    return check_password_hash( self.password_hash, password )

  def __str__( self ):
    return f"Name: {self.name} - Email: {self.email}"



@app.route('/')
def home( ):
  return render_template('index.html')


@app.route('/name', methods=['GET', 'POST'])
def name():
  name = None
  form = Namer( )
  if form.validate( ):
    name = form.name.data
    color = form.color.data
    form.name.data = ''
    flash( 'Form Submitted Son of a gun!', 'success' )
  return render_template('name.html', name=name,form=form)


@app.route('/user/<name>')
def user(name):
  return render_template('user.html', name=name)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
  form = UserForm(request.form)
  if request.method == 'POST' and form.validate():
    name = form.name.data
    email = form.email.data
    color = form.color.data 
    user = Users.query.filter_by(email=email).first()
    if user is None:
      user = Users(name=name, email=email, color=color)
      db.session.add(user)
      db.session.commit()
    form.name.data = ''
    form.email.data = ''
    form.color.data = ''
    flash('User Added Successfully!', 'success')
  our_users = Users.query.order_by(Users.date_added)
  return render_template('add_user.html', form=form, our_users=our_users)


@app.route( "/update/<int:id>", methods=['GET', 'POST'] )
def update( id ):
  form = UserForm( request.form )
  user_to_update = Users.query.get_or_404( id )
  if request.method == 'POST' and form.validate():
    user_to_update.name = form.name.data
    user_to_update.email = form.email.data
    user_to_update.color = form.color.data
    try:
      db.session.commit()
      flash('User Updated Successfully!', 'success')
      return render_template('update.html', form=form, user=user_to_update)
    except:
      flash('Error! Looks like there was a problem...try again!', 'danger')
      return render_template('update.html', form=form, user=user_to_update)
  else:
    form.name.data = user_to_update.name
    form.email.data = user_to_update.email
    form.color.data = user_to_update.color
    return render_template('update.html', form=form, user=user_to_update)


@app.route( "/delete/<int:id>", methods=['GET', 'POST'] )
def delete( id ):
  user_to_delete = Users.query.get_or_404( id )
  try:
    db.session.delete( user_to_delete )
    db.session.commit()
    flash('User Deleted Successfully!', 'success')
  except:
    flash('Error! Looks like there was a problem...try again!', 'danger')
  return redirect( url_for( 'add_user' ) )



@app.errorhandler( 404 )
def page_not_found( e ):
  return render_template( '404.html' ), 404

@app.errorhandler( 500 )
def internal_server_error( e ):
  return render_template( '500.html' ), 500


if __name__ == '__main__':
  app.run(debug=True)

