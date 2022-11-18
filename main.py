import requests
import werkzeug.security
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def find_score(look_for):
    options = Options()
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=options)
    driver.get(f"https://www.csfd.cz/hledat/?q={look_for}")

    try:
        cookie = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="didomi-notice-agree-button"]'))
        )
        cookies = driver.find_element(By.XPATH, '//*[@id="didomi-notice-agree-button"]').click()
        film_search = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="snippet--containerFilms"]/article[1]/figure/a'))
        )
        film_search = driver.find_element(By.XPATH, '//*[@id="snippet--containerFilms"]/article[1]/figure/a').click()
        rating = driver.find_element(By.XPATH,
                                     '//*[@id="page-wrapper"]/div/div[1]/aside/div[1]/div[2]/div[1]').text.strip("%")
        print(rating)
    finally:
        driver.quit()
    return rating

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = '920a9b69fb94acb591d1ceaf7cfbe3eaa1ca16b1346dea3694bafbf1ca10e532'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
BASE_WEB = "https://api.themoviedb.org/3/search/movie?"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(), nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(1000), nullable=True, unique=False)
    img_url = db.Column(db.String, nullable=False)


@login_manager.user_loader
def load_user(user):
    return User.query.get(user)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    def __repr__(self):
        return self.name


class AddMovie(FlaskForm):
    nazev = StringField("Zadej název filmu")
    submit = SubmitField("Okej")
class RateMovieForm(FlaskForm):
    review = StringField("Zadej receneci")
    submit = SubmitField("Done")

@app.route("/")
def home():
    all_films = db.session.query(Film).order_by(Film.rating.desc()).all()
    pocet = len(all_films)
    return render_template("indexa.html",films=all_films,pocet=pocet)

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.form:
        if db.session.query(User).filter_by(email=request.form.get("email")).first():
            flash("Email je už obsazený, zadej jiný!")
        else:
            new_user = User()
            new_user.name = request.form.get("name")
            new_user.email = request.form.get("email")
            new_user.password = werkzeug.security.generate_password_hash(password=request.form.get("password"),
                                                                         method="pbkdf2:sha256",
                                                                         salt_length=8)
            db.session.add(new_user)
            db.session.commit()
            print(new_user.name)
            login_user(new_user)
            return redirect(url_for("secrets",name=new_user.name))

    return render_template("register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.form:
        user = db.session.query(User).filter_by(email=request.form.get("email")).first()
        if user:
            if check_password_hash(pwhash=user.password,password=request.form.get("password")):
                login_user(user)
                return redirect(url_for("secrets",current_user=user))
            else:
                flash("Špatné heslo !")
        else:flash("Zadej správný email.")

    return render_template("login.html")

@app.route('/secrets', methods=["GET", "POST"])
def secrets():
    welcome = current_user
    return render_template("secrets.html",current_user=welcome)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route('/download')
def download():
    if current_user:
            return send_from_directory(directory="static",path="files/cheat_sheet.pdf")
    else:
        return render_template("login.html")





@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    film = Film.query.get(id)
    if request.form:
        film.review = request.form.get("edit")
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html",movie=film)

@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):
    Film.query.filter(Film.id == id).delete()
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/add", methods=["GET", "POST"])
def add():
    all_films = []
    parameters = {
        "api_key": "df1513738a434dad057e9d9937a2b160",
        "language": "cs-CZ",
        "query": request.form.get("find"),
    }
    if request.form :
        data = requests.get(BASE_WEB, params=parameters)
        film_data = data.json()
        for film in film_data["results"]:
            all_films.append(film)
        print(all_films)
        return render_template("select.html",films=all_films)
    return render_template("add.html")


@app.route("/find/<int:id>", methods=["GET", "POST"])
def add_film(id):
    find_movie = f"https://api.themoviedb.org/3/movie/{id}?"
    parameters = {
        "api_key": "df1513738a434dad057e9d9937a2b160",
        "language": "cs-CZ",
        "movie_id": id
    }
    data = requests.get(find_movie, params=parameters)
    film_data = data.json()
    score = find_score(look_for=film_data["original_title"])
    year = film_data["release_date"].split("-")
    film = Film(id=id, title=film_data["original_title"], year=year[0],
                img_url=f"https://image.tmdb.org/t/p/w500//{film_data['poster_path']}",
                description=film_data["overview"],rating=score)
    db.session.add(film)
    db.session.commit()
    return redirect(url_for("edit",id=id))




if __name__ == "__main__":
    app.run(debug=True)
