import requests
import sqlalchemy.exc
import werkzeug.security
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import requests
from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def find_score(look_for,rok):
    """
    :param look_for: exact name of film you look for
    :return: scrapped score of film on CSFD
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_experimental_option("detach", True)
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.google.com/search?q={look_for}+{rok}+csfd")
    try:
        cookie = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="W0wltc"]/div'))
        )
        cookies = driver.find_element(By.XPATH, '//*[@id="W0wltc"]/div').click()
        source = driver.page_source
        final = 0
        word = "Hodnocení"
        if word in source:
            index = source.index("Hodnocení")
            final = source[index + 11:index + 13]
            print(final)
    finally:
        pass
    return final

#app settings
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = '920a9b69fb94acb591d1ceaf7cfbe3eaa1ca16b1346dea3694bafbf1ca10e532'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://sql7588422:wMcIYFWNix@sql7.freesqldatabase.com:3306/sql7588422'

BASE_WEB = "https://api.themoviedb.org/3/search/movie?"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# M:M relationship database
user_film = db.Table("user_film",
                     db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
                     db.Column("film_id", db.Integer, db.ForeignKey("film.id")),
                     db.Column("user_comment", db.String)
                     )
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
    following = db.relationship("Film", secondary=user_film, backref="following")
    def __repr__(self):
        return self.name


@app.route("/")
def home():
    """
    Home page rendered. Try: make current_user film list. If there is no current_user, create list from DB
    :return: homepage with film list
    """
    all_films = db.session.query(Film).order_by(Film.rating.desc()).all()
    all_films_id = db.session.query(Film.id).distinct()
    try:
        seznam = db.session.query(user_film)
        user_film_list = [[],[]]
        for film in seznam:
            if film[0] == current_user.id:
                user_film_list[0].append(film[1])
                user_film_list[1].append(film[2])
        print(user_film_list)
    except AttributeError:
        user_film_list = all_films_id

    return render_template("indexa.html",films=all_films,user_films=user_film_list)



#user block
@app.route('/register', methods=["GET", "POST"])
def register():
    """
    register new user
    :return: redirect to secrets
    """
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
            return render_template("secrets.html")

    return render_template("register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    """
    login user
    :return: redirect to secrets html
    """
    if request.form:
        user = db.session.query(User).filter_by(email=request.form.get("email")).first()
        if user:
            if check_password_hash(pwhash=user.password,password=request.form.get("password")):
                login_user(user)
                return render_template("secrets.html")
            else:
                flash("Špatné heslo !")
        else:flash("Zadej správný email.")

    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    """
    log out user
    :return: redirect to home
    """
    logout_user()
    return redirect(url_for("home"))


# film block
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    """

    :param id: id of film in database Film you want to edit review
    :return: edited film, redirect to home
    """
    film= Film.query.get(id)
    if request.form:
        rew = request.form.get("edit")
        db.engine.execute(f"UPDATE user_film SET user_comment = '{rew}' WHERE user_id = {current_user.id} AND film_id = {id}")

        return redirect(url_for("home"))
    return render_template("edit.html",movie=film)

@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):
    """
    delete film in users film database
    :param id: id of film
    :return: redirect to home
    """
    db.engine.execute(f"delete from user_film where film_id = {id} and user_id = {current_user.id}")
    return redirect(url_for("home"))

@app.route("/add", methods=["GET", "POST"])
def add():
    """
    Ask you to type in a film you want to look for. Dont have to be exactly.
    :return: Redirect to select . Get list of films by your typed name.
    """
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
    """
    select film by click on hrefs
    :param id: id of film you choosed
    :return: film added to database, render edit page
    """
    is_in_database = Film.query.get(id)

    if is_in_database:
        film = Film.query.get(id)
        current_user.following.append(film)
        print("OK")
        db.session.commit()

    elif not is_in_database:
        find_movie = f"https://api.themoviedb.org/3/movie/{id}?"
        parameters = {
            "api_key": "df1513738a434dad057e9d9937a2b160",
            "language": "cs-CZ",
            "movie_id": id
        }
        data = requests.get(find_movie, params=parameters)
        film_data = data.json()
        year = film_data["release_date"].split("-")
        score = find_score(look_for=film_data["original_title"], rok=year[0])
        film = Film(id=id, title=film_data["original_title"], year=year[0],
                    img_url=f"https://image.tmdb.org/t/p/w500//{film_data['poster_path']}",
                    description=film_data["overview"], rating=score)
        current_user.following.append(film)
        db.session.add(film)
        db.session.commit()


    return redirect(url_for("edit",id=id))



@app.route("/stats")
def stats():
    # TODO napiš dokumentaci a uprav výstupy v databázi
    # sežeň filmy z databáze
    times = []
    names = []
    most_add_movies = db.engine.execute(f"SELECT count(film_id) as f, film_id FROM user_film GROUP BY film_id ORDER by f DESC limit 5")
    for movie in most_add_movies.all():
        film = Film.query.get(movie[1])
        times.append(movie[0])
        names.append(film.title)

    #sežeň počet uživatelů s alespoň 1 filmem v databázi.
    uzivatele = []
    users = db.engine.execute(f"SELECT count(user_id) as filmu, user_id FROM user_film GROUP BY user_id ORDER by filmu DESC")
    for user in users.all():
        this_user = User.query.get(user[1])
        uzivatele.append((this_user.name, user[0], user[1]))
    return render_template("stats.html",times=times,names=names, uzivatele=uzivatele)



@app.route("/<int:id>")
def list(id):
    seznam = db.session.query(user_film)
    user_film_list = [[],[]]
    for film in seznam:
        if film[0] == id:
            user_film_list[0].append(Film.query.get(film[1]))
            user_film_list[1].append(film[2])
    print(user_film_list)

    this_user = User.query.get(id)
    sortedByName = [sorted(user_film_list[0], key=lambda x: x.rating, reverse=True)] + [user_film_list[1]]
    print(sortedByName)
    return render_template("user_list.html",films=sortedByName,uzivatel=this_user.name)

# with app.app_context():
#     db.create_all()


#TODO udělat koláčový graf , naučit se jak udělat graf z SQL
"""
1. zjistit jak získat data z databáze ----------------------------------------------------------ok
2. zjistit jak udělat vizualizaci dat-----------------------------------------------------------ok
3. stránku nastylovat tak aby tam bylo možné vložit statistiky, koláče a tak----------dodělat
4. Vytvořit stránku s žebříčkem/statistikou uživatelů.-------------------------------- možná ok?
5. po kliknutí na uživatele se zobrazí jeho databáze avšak bez možností mazat či upravovat   ok
"""


if __name__ == "__main__":
    app.run(debug=True)
