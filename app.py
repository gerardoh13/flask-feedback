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

@app.route("/")
def show_homepage():
    """redirects to registration"""
    return redirect("/register")

@app.route('/register', methods=['GET', 'POST'])
def registration():
    """shows registration form and processes registrations"""
    form = UserForm()
    if 'username' in session:
        user = session["username"]
        flash('logout to register a new account', "warning")
        return redirect(f"/users/{user}")
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
        flash(f'Welcome {new_user.first_name}!', "info")
        return redirect(f"/users/{new_user.username}")
        
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """shows login form and processes logins"""
    if 'username' in session:
        user = session["username"]
        flash("You're aleardy logged in", "warning")
        return redirect(f"/users/{user}")
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            flash(f'Welcome {user.first_name}!', "info")
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ['Invalid username/password.']
        
    return render_template('login.html', form=form)

@app.route('/users/<username>')
def show_user(username):
    if "username" not in session or session['username'] != username:
        flash("Oops! You don't have access to this page", "danger")
        return redirect('/401')
    user = User.query.get_or_404(username)
    return render_template('user-details.html', user=user)

@app.route('/users/<username>/add', methods=['GET', 'POST'])
def add_feedback(username):
    """shows new feedback form and submits new feedback"""
    if "username" not in session or session['username'] != username:
        flash("Oops! You don't have access to this page", "danger")
        return redirect('/401')
    form = FeedbackForm()
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}
        new_feedback = Feedback(**data, username=username)
        db.session.add(new_feedback)
        db.session.commit()
        flash(f"feedback '{new_feedback.title}' submitted!", "info")
        return redirect(f"/users/{username}")
    return render_template("feedback.html", form=form, username=username, action="Add")

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    """shows feedback update form and submits updates"""
    feedback = Feedback.query.get_or_404(feedback_id)
    if "username" not in session or session['username'] != feedback.username:
        flash("Oops! You don't have access to this page", "danger")
        return redirect('/401')
    form = FeedbackForm(title=feedback.title, content=feedback.content)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        flash(f"feedback '{feedback.title}' updated!", "info")
        return redirect(f"/users/{feedback.username}")
    return render_template('feedback.html', form=form, username=feedback.username, action="Edit")

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    """deletes feedback"""
    feedback = Feedback.query.get_or_404(feedback_id)
    if "username" not in session or session['username'] != feedback.username:
        flash("Oops! You don't have access to this page", "danger")
        return redirect('/401')
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f"/users/{feedback.username}")

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """deletes user"""
    user = User.query.get_or_404(username)
    if "username" not in session or session['username'] != username:
        flash("Oops! You don't have access to this page", "danger")
        return redirect('/401')
    db.session.delete(user)
    db.session.commit()
    session.pop('username')
    flash("Account has been deleted", "warning")
    return redirect("/register")

@app.route('/logout')
def logout_user():
    """logs user out"""
    session.pop('username')
    flash("Goodbye!", "info")
    return redirect('/register')

@app.route('/401')
def show_401_error():
    """shows 401 page"""
    if "username" in session:
        username = session["username"]
        route = f"/users/{username}"
    else:
        route = "/"
    return render_template('401.html', route=route)

@app.errorhandler(404)
def page_not_found(e):
    """shows 401 page"""
    if "username" in session:
        username = session["username"]
        route = f"/users/{username}"
    else:
        route = "/"
    return render_template('404.html', route=route), 404