from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import flash
from werkzeug.exceptions import abort


from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'secret-key'

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Todotask.sqlite3'

# Disable modification tracking as it is not needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy instance with the Flask app
db = SQLAlchemy(app)

# Initialize the Flask-Migrate instance with the Flask app and SQLAlchemy instance
migrate = Migrate(app, db)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    # Define the relationship between the User and Todo models
    todos = db.relationship('Todo', backref='user', lazy=True)

# Define the Todo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    status = db.Column(db.Enum('to do', 'doing', 'done'), default='to do')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@app.route('/')
def home():
    """
Redirects to the signup page.
 """
    return redirect(url_for('signup'))



@app.route('/todo')
def index():
    
    """Displays the list of todos for the logged-in user."""
    
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    user_id = session['user_id']
    
    # Get the User object for the logged-in user
    user = User.query.filter_by(id=user_id).first()
    
    # Get the list of todos for the logged-in user
    todo_list = Todo.query.filter_by(user_id=user_id).all()
    
    return render_template('base.html', todo_list=todo_list,user=user)



@app.route('/add', methods=["POST"])
def add():
    
    """Adds a new todo item for the logged-in user."""

    # add new item
    title = request.form.get("title")
    
    # Get the user ID from the session
    user_id = session.get('user_id')
    
    # Create a new Todo object with the title and user ID
    new_todo = Todo(title=title, user_id=user_id)
    
    # Add the new todo item to the database
    db.session.add(new_todo)
    db.session.commit()

    # Redirect to the todo list page
    return redirect(url_for("index"))


@app.route('/update/<int:todo_id>')
def update(todo_id):
    
    """Updates the status of the given todo item."""
    
    # Get the Todo object for the given ID
    todo = Todo.query.filter_by(id=todo_id).first()

    # Update the status of the todo item
    if todo.status == 'to do':
        todo.status = 'doing'
    elif todo.status == 'doing':
        todo.status = 'done'

    # Commit the changes to the database
    db.session.commit()

    # Redirect to the todo list page
    return redirect(url_for('index'))


@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    """Delete a todo item from the user's todo list."""
    
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    """Allow the user to create a new account.

    If the user is already signed in, redirect them to their todo list.
    """

    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return redirect(url_for('index'))
    return render_template('signup.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    
    """Allow the user to sign in to their account.

    If the user enters invalid credentials, flash an error message
    and redirect them to the signin page.
    """
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        print(user)  # debug statement
        print(email, password)  # debug statement
        if user:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')
            return redirect(url_for('signin'))
    return render_template('signin.html')


@app.route('/logout')
def logout():
    
    """Remove the user's session data and redirect to the signin page."""
    
    session.pop('user_id', None)
    return redirect(url_for('signin'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)