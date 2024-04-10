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
import os
from werkzeug.utils import secure_filename
from verification import user_session, logout_user, login_required, admin_login_required


app = Flask(__name__)
app.config.from_object(Config)
#mysql = MySQL(app)
#mysql.init_app(app)
cnx = mysql.connector.connect(user='root', password='V13laukums@!',
 host='localhost',
 database='mydatabase')

# routes
@app.route('/delete/<product_id>', methods=['GET'])
@login_required
def delete_product(product_id):
    cur = cnx.cursor()
    user_id = session.get('user_id')
    try:
        query_string = '''SELECT cart_id FROM cart WHERE user_id = %s'''
        cur.execute(query_string, (user_id,))
        cart_id = cur.fetchone()[0]  # Assuming cart_id is the first element of the tuple
        cnx.commit()
        cur.close()
        cur = cnx.cursor()
        query_string = '''DELETE FROM cart_items WHERE product_id = %s and cart_id = %s'''
        cur.execute(query_string, (product_id, cart_id))
        cnx.commit()
        cur.close()
        flash("Product deleted successfully", "success")
        return redirect("/products")
    except Exception as e:
        flash("Database error: " + str(e), "error")
        return redirect("/products")

@app.route('/add_to_cart/<product_id>', methods=['GET'])
@login_required
def add_to_cart(product_id):
    cur = cnx.cursor()
    user_id = session.get('user_id')
    try:
        query_string = '''SELECT cart_id FROM cart WHERE user_id = %s'''
        cur.execute(query_string, (user_id,))
        cart_id = cur.fetchone()[0]  # Assuming cart_id is the first element of the tuple
        query_string = '''INSERT INTO cart_items (id, product_id, cart_id) VALUES (%s, %s, %s)'''
        val1 = (str(uuid4()), product_id, cart_id)
        cur.execute(query_string, val1)
        cnx.commit()
        cur.close()
        flash("Product added to cart successfully", "success")
        return redirect("/products")
    except Exception as e:
        flash("Database error: " + str(e), "error")
        return redirect("/products")

@app.route('/admin_products', methods=['GET', 'POST'])
@admin_login_required
def admin_products():
    if request.method == "POST":
        name = request.form.get('prod_name')
        kategorija = request.form.get('kategorija')
        cost = request.form.get('cost')
        size = request.form.get('size')
        image_file = request.files['image']
        description = request.form.get('description')

        # Save the image file to the 'images' folder
        if image_file:
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
        else:
            image_path = 'static/images/default_image.png'

        try:
            cur = cnx.cursor()
            query_string = """INSERT INTO products (product_id, prod_name, categ_id, cost, size, image_file, description) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            val = (str(uuid4()), name, kategorija, cost, size, image_path, description)
            cur.execute(query_string, val)
            cnx.commit()
            cur.close()
            flash("Product added successfully", "success")
            return redirect("/admin_products")
        except Exception as e:
            flash("Database error: " + str(e), "error")
            return redirect("/admin_products")

    else:
        try:
            cur = cnx.cursor()
            query_string = """SELECT products.prod_name, categories.kategorija, products.cost, products.size, products.image_file, products.description 
                            FROM products 
                            JOIN categories ON products.categ_id = categories.categ_id
                            """
            cur.execute(query_string)
            produkts = cur.fetchall()
            query_string = """SELECT * from categories"""
            cur.execute(query_string)
            kategorijas = cur.fetchall()
            cur.close()
            return render_template("admin_produkti.html", produkts=produkts, kategorijas=kategorijas)
            
        except Exception as e:
            flash("Database error: " + str(e), "error")


@app.route('/products', methods=['GET'])
def produkti():
    try:
        cur = cnx.cursor()
        query_string = """SELECT products.prod_name, categories.kategorija, products.cost, products.size, products.image_file, products.description, products.product_id
                        FROM products 
                        JOIN categories ON products.categ_id = categories.categ_id
                        """
        cur.execute(query_string)
        produkts = cur.fetchall()
        cur.close()
        print(produkts)
        return render_template("produkti.html", produkts=produkts)
        
    except Exception as e:
        flash("Database error: " + str(e), "error")
            
#categories
@app.route('/categ', methods=['POST', 'GET'])
@admin_login_required
def categ():
    if request.method == "POST":
        try:
            kategorija = request.form.get("kategorija")
            print("Received kategorija value:", kategorija)
            categ_id = str(uuid4())
            cur = cnx.cursor()
            add_category = ("INSERT INTO mydatabase.categories "
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
            query_string = "SELECT * FROM categories"
            cur.execute(query_string)
            kategorijas = cur.fetchall()
            cur.close()
            print(kategorijas)
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
                    user_session(user, username)
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
        user_id = str(uuid4())
        newUserSql = ''' INSERT INTO users (user_id, username, password, first_name, last_name, e_mail, phone, adress, admin) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s) '''
        val1 = (user_id,
                username, 
                generate_password_hash(password), 
                first_name, 
                last_name, 
                e_mail, 
                phone,
                address,
                int(0))
        UserCartSql = ''' INSERT INTO cart (cart_id, user_id) VALUES (%s, %s)'''
        val2 = (str(uuid4()), user_id)
        try:
            cur = cnx.cursor()
            cur.execute(newUserSql, val1)
            cnx.commit()
            cur.execute(UserCartSql, val2)
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
@admin_login_required
def admin():
    if request.method=="POST":
        pass
    else:
        return render_template("admin.html")

#Logout
@app.route("/logout")
def logout():
    logout_user()
    flash("You are logged out")
    return redirect("/home")

#Cart
@app.route("/view_cart", methods=['POST', 'GET'])
@login_required
def view_cart():
    if request.method == "POST":
        pass
    else:
        try:
            cur = cnx.cursor()
            query_string = """SELECT products.product_id, products.prod_name, categories.kategorija, products.cost, products.size, products.image_file, products.description 
            FROM products
            JOIN categories ON products.categ_id = categories.categ_id
            WHERE product_id = (
            SELECT product_id FROM cart where user_id = %s)"""
            cur.execute(query_string, (session["user_id"], ))
            produkts = cur.fetchall()
            cur.close()
            print(produkts)
            return render_template("view_cart.html", produkts=produkts)
        except Exception as e:
            flash("Database error: " + str(e), "error")
    
        return render_template("view_cart.html")

if app.config["FLASK_ENV"] == "development":
    if __name__ == "__main__":
        app.run(debug=True)

cnx.close()
