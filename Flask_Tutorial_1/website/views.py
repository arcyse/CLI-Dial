from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import  login_required, current_user
from . import db
from .models import Note
import json

#* Stores standard routes for the website

# Create a Blueprint for views:
views = Blueprint('views', __name__)

# Decorated function for homepage: @<blueprint_name>.route('<url_path>')
@views.route('/', methods=['GET', 'POST']) # No explicit route (since it is the homepage)
@login_required # Can only access home page if user is logged in
def home():
    # When user submits a note:
    if request.method == 'POST':
        # Get user input:
        user_text = request.form.get('note')
        user_id = current_user.id
        
        # Input validation:
        if len(user_text) < 1:
            flash('Note must be at least 1 characters long!', category='error')
        else:
            # Insert note into database (linked with user id through foreign key)
            from .models import Note
            from . import db
            note = Note(data=user_text, user_id=user_id)
            db.session.add(note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template('home.html', user=current_user)
    #return '<h1>Hello!</h1>' #Returns an HTML tag for home & site renders it

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})