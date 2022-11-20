# film_database
Film database using Python, Flask, SQLalchemy, Selenium,...



Film database is an web application written in Python using the Flask web framework. Bootstrap are used in templates.  Icons come from Bootstrap. 
Film data are from [themoviedb.org](https://www.themoviedb.org/) and scrapped from [ČSFD](https://www.csfd.cz/) with BeautifulSoup4.


If you sign up, you can add films to your users database, which will be saved in SQLalchemy database. 


[![fotka](https://user-images.githubusercontent.com/115080043/202891628-eadbe048-01fa-4c22-9e8c-4e3779931882.jpg)](https://youtu.be/wTnv6FAykDY)


### How to run:
1. Download film_database repo
2. Install dependencies (find them in requirements.txt file or writen bellow)
3. Run Main.py, than should see output similar to this:
```shell
 * Serving Flask app 'main'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: ***-***-***
```
Now you´ll be able to open the Film database application in your web browser by following the URL printed out in the last screen (* Running on http://127.0.0.1:5000). 






### requirements:

Flask==2.2.2
Flask_Bootstrap==3.3.7.1
flask_login==0.6.2
flask_sqlalchemy==3.0.2
Flask_WTF==1.0.1
requests==2.28.1
selenium==4.6.0
SQLAlchemy==1.3.23
webdriver_manager==3.8.4
Werkzeug==2.2.2
WTForms==3.0.1
