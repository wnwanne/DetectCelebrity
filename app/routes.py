from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User
from werkzeug.urls import url_parse
import boto3


bucket_name = "winnie-analyzevid-ab2"

s3 = boto3.client("s3")

@app.route("/", methods=['post', 'get'])
@app.route("/index", methods=['post', 'get'])
def index():
    if request.method == "POST":
        try:
            img = request.files['img']
            filename = img.filename
            if img:
                s3.put_object(
                    Bucket = bucket_name,
                    Body = img,
                    Key=filename
                )
                return("<h1>upload successful<h1>")
        except Exception as e:
            return (str(e))
    return render_template("index.html")

    # return '''<form method=POST enctype=multipart/form-data action="upload">
    #     <input type=file name=myfile>
    #     <input type=submit>
    #     </form>'''

# @app.route('/upload', methods=['POST'])
# def upload():
#     s3 = boto3.resource('s3')
#
#     s3.Bucket('winnie-analyzevid-ab2').put_object(Key='colortracingshot.mov', Body=request.files['myfile'])
#
#     return '<h1>File saved to S3</h1>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username  or  password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
