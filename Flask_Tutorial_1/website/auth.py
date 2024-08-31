from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint('auth', __name__)

# Login page:
@auth.route('/login', methods=['GET', 'POST']) # Add ability of login page for both GET and POST HTTP requests
def login():
    #data = request.form
    #print(data)
    if request.method == 'POST':
        # Get user login details:
        email = request.form.get('email')
        password = request.form.get('password')

        # Query the database for entries with same email
        user = User.query.filter_by(email=email).first()
        # If user email already registered:
        if user:
            # Check password correctness:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True) # Login user and remember session
                return redirect(url_for('views.home')) # Redirect to homepage after successful login
            else:
                flash('Incorrect password! Try again!', category='error')
        # If user email not registered:
        else:
            flash('User account not created. Plase sign up!', category='error')
    
    return render_template('login.html',user=current_user)

# Logout page:
@auth.route('/logout') # Default only GET requests allowed
@login_required # Login required before logging out
def logout():
    logout_user() # Logout user
    return redirect(url_for('auth.login')) # Redirect to user login page

# Sign-up page:
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    #If user makes a post request (after entering details and clicking submit):
    if request.method == 'POST':
        # Get user sign-up details:
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Check input validity:
        # Use message flashing in flask to notify users:
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered!', category='error')
        elif(len(email) < 4):
            flash('Email must have at least 4 characters', category='error')
        elif(len(firstName) < 2):
            flash('Name must have at least 2 characters', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        elif len(password1) < 7:
            flash('Password must b at least 7 characters long', category='error')
        
        # Otherwise enter user details into database:
        else:
            new_user = User(email=email, first_name=firstName, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', category='success')
            login_user(new_user, remember=True) # Login user after signing up
            # Redirect back to home page (URL for the home function in views.py):
            return redirect(url_for('views.home'))

    return render_template('sign_up.html', user=current_user)