
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    flash,
    session)
#from flask_mysqldb import MySQL
#from flaskext.mysql import MySQL
from config import Config
from uuid import uuid4
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
#from flask_mysql_connector import MySQL
#import mysql.connector


app = Flask(__name__)
app.config.from_object(Config)
#mysql = MySQL(app)
#mysql.init_app(app)
cnx = mysql.connector.connect(user='root', password='#Password1',
 host='localhost',
 database='internetveikals')



# routes
#categories
@app.route('/categ', methods=['POST', 'GET'])
def categ():
    if request.method == "POST":
        try:
            kategorija = request.form.get("kategorija")
            print("Received kategorija value:", kategorija)
            categ_id = str(uuid4())
            cur = cnx.cursor()
            add_category = ("INSERT INTO internetveikals.categories "
                "(categ_id, kategorija) "
                "VALUES (%s,%s)")
            val = (categ_id, kategorija)
            cur.execute(add_category, val)
            cnx.commit()
            cur.close()
            flash("Category added successfully", "success")
            return redirect("/categ")
        except Exception as e:
            flash("Database error: " + str(e), "error")
            return redirect("/categ")
    else:
        try:
            cur = cnx.cursor()
            query_string = "SELECT * FROM internetveikals.categories"
            cur.execute(query_string)
            kategorijas = cur.fetchall()
            cur.close()
            return render_template("categ.html", manas_kategorijas=kategorijas)
            
        except Exception as e:
            flash("Database error: " + str(e), "error")
            return render_template("categ.html", categories=[])
#Home
@app.route('/', methods = ['GET'])
@app.route('/home', methods = ['GET'])
def home():
        return render_template("home.html")
#Login
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        try:
            cur = cnx.cursor()
            username = request.form["username"]
            password = request.form["password"]
            cur.execute("SELECT user_id, password, admin FROM users WHERE username = %s", (username, ))
            user = cur.fetchall()
            if len(user) > 0:
                if check_password_hash(user[0][1], password):
                    session["user_id"] = user[0][0]
                    session["user_name"] = username
                    session["user_role"] = user[0][2]
                    flash("You are logged in")
                else:
                    flash("Wrong password")
            else:
                flash("User not found, you are welcome to register")
                return redirect("/login")
            cur.close()
            return redirect("/home")
        except Exception as e:
            flash("Database error: " + str(e), "error")
            return render_template("login.html")
    else:
        return render_template("login.html")
#Register
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_check = request.form["password-check"]
        if password != password_check:
            flash("Passwords don't match")
            return redirect("/register")
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        e_mail = request.form["e-mail"]
        phone = request.form["phone"]
        address = request.form["address"]
        newUserSql = ''' INSERT INTO users (user_id, username, password, first_name, last_name, e_mail, phone, adress, admin) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s) '''
        val = (str(uuid4()),
                username, 
                generate_password_hash(password), 
                first_name, 
                last_name, 
                e_mail, 
                phone,
                address,
                int(0))
        try:
            cur = cnx.cursor()
            cur.execute(newUserSql, val)
            cnx.commit()
            cur.close()
            flash("Account created successfully!")
            return redirect("/login")
        except Exception as e:
            flash("Database error: " + str(e), "error")
            return redirect("/register")
    else:
        return render_template("register.html")
    
#Admin
@app.route("/admin", methods=['POST', 'GET'])
def admin():
    if request.method=="POST":
        pass
    else:
        return render_template("admin.html")

#Logout
@app.route("/logout")
def logout():
    del(session["user_id"])
    del(session["user_name"])
    del(session["user_role"])
    flash("You are logged out")
    return redirect("/home")

#Cart
@app.route("/view_cart", methods=['POST', 'GET'])
def view_cart():
    pass


if app.config["FLASK_ENV"] == "development":
    if __name__ == "__main__":
        app.run(debug=True, host='localhost', port=5000)
cnx.close()