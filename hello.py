from datetime import (
    datetime,
    timezone,
)
import os
from flask import (
    Flask,
    request,
    render_template,
    session,
    redirect,
    url_for,
    flash
)
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'trudny do odgadnięcia ciąg znaków?'


class NameForm(FlaskForm):
    name = StringField('Jak masz na imię?', validators=[DataRequired()])
    submit = SubmitField('Wyślij')


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self) -> str:
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self) -> str:
        return '<User %r>' % self.username


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.route('/tmp/user/<name>')
def tmp(name):
    comments = ["Aaa...", "Bbb....", "Ccc..."]
    return render_template(
        '/tmp/info.html',
        user=name,
        comments=comments
    )


@app.route('/tmp/index')
def index_user():
    return render_template('/tmp/user.html', user="One Two")


@app.route('/browser')
def browser():
    user_agent = request.headers.get('User-Agent')
    # request_headers = dict(request.headers)
    headers = "<br>".join(map(': '.join, request.headers.items()))
    return f"<p>Twoją przeglądarką jest <b>{user_agent}</b></p><h2>Header</h2><p>{headers}</p>"


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/time')
def show_time():
    return render_template('time.html', current_time=datetime.now(timezone.utc))


@app.route('/forms', methods=['GET', 'POST'])
def forms():
    name = None
    form = NameForm()
    if form.validate_on_submit():  # Czy POST?
        name = form.name.data
        form.name.data = ''  # puste pole formularza
    return render_template('forms.html', form=form, name=name)


@app.route('/forms2', methods=['GET', 'POST'])
def forms2():
    form = NameForm()
    if form.validate_on_submit():  # Czy POST?
        session['name'] = form.name.data
        return redirect(url_for('forms2'))
    return render_template('forms.html', form=form, name=session.get('name'))


@app.route('/forms3', methods=['GET', 'POST'])
def forms3():
    form = NameForm()
    if form.validate_on_submit():  # Czy POST?
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Wygląda na to, że teraz nazywasz się inaczej!')
        session['name'] = form.name.data
        return redirect(url_for('forms3'))
    return render_template('forms.html', form=form, name=session.get('name'))

