from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, session, redirect, flash
from models import db, connect_db, User, Feedback
from forms import FeedbackForm, LoginForm, UserForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

app.config['SECRET_KEY'] = "Cats_are_cool!"
debug = DebugToolbarExtension(app)

@app.route('/')
def show_homepage():
    """shows home page if registered/logged-in or redirects to registration"""
    if "username" not in session:
        return redirect("/register")
    return render_template("home.html")

@app.route('/register', methods=['GET', 'POST'])
def registration():
    """shows registration form and processes registrations"""
    form = UserForm()
    if 'username' in session:
        flash('logout to register a new account', "danger")
        return redirect("/")
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}
        new_user = User.register(**data)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please choose another username.')
            return render_template('register.html', form=form)
        session['username'] = new_user.username
        flash(f'Welcome {new_user.first_name}')
        return redirect(f"/users/{new_user.username}")
        
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """shows login form and processes logins"""
    if 'username' in session:
        flash("You're aleardy logged in", "danger")
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            flash(f'Welcome {user.first_name}')
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ['Invalid username/password.']
        
    return render_template('login.html', form=form)

@app.route('/users/<username>')
def show_user(username):
    if "username" not in session or session['username'] != username:
        flash("Oops! You don't have access to this page", "danger")
        return redirect('/')
    user = User.query.get_or_404(username)
    return render_template('user-details.html', user=user)

@app.route('/users/<username>/add', methods=['GET', 'POST'])
def add_feedback(username):
    """shows new feedback form and submits new feedback"""
    if "username" not in session or session['username'] != username:
        flash("Oops! You don't have access to this page", "danger")
        return redirect('/')
    form = FeedbackForm()
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}
        new_feedback = Feedback(**data, username=username)
        db.session.add(new_feedback)
        db.session.commit()
        flash(f"feedback '{new_feedback.title}' submitted!")
        return redirect(f"/users/{username}")
    return render_template("feedback.html", form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    """shows feedback update form and submits updates"""
    feedback = Feedback.query.get_or_404(feedback_id)
    if "username" not in session or session['username'] != feedback.username:
        flash("Oops! You don't have access to this page", "danger")
        return redirect('/')
    form = FeedbackForm(title=feedback.title, content=feedback.content)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        flash(f"feedback '{feedback.title}' updated!")
        return redirect(f"/users/{feedback.username}")
    return render_template('feedback.html', form=form)

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    """deletes feedback"""
    feedback = Feedback.query.get_or_404(feedback_id)
    if "username" not in session or session['username'] != feedback.username:
        flash("Oops! You don't have access to this page", "danger")
        return redirect('/')
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f"/users/{feedback.username}")

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """deletes user"""
    user = User.query.get_or_404(username)
    if "username" not in session or session['username'] != username:
        flash("Oops! You don't have access to this page", "danger")
        return redirect('/')
    db.session.delete(user)
    db.session.commit()
    session.pop('username')
    flash("Account has been deleted", "danger")
    return redirect("/")

@app.route('/logout')
def logout_user():
    session.pop('username')
    flash("Goodbye!", "info")
    return redirect('/')