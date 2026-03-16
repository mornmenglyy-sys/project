from flask import Flask, redirect,render_template,request, url_for
import pymysql
import os
import uuid

app = Flask(__name__)


UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER


def connect_db():
    connect= pymysql.connect(
    host="localhost",
    user="root",
    password="",
    db="projcet"
    
    )
    if (not connect):
        print("can not connect to database 🥲")

    print("connect success 😂")
    return connect


connect_db()    

@app.route("/")
def index():
    connection=connect_db()
    cursor=connection.cursor()

    cursor.execute("SELECT * FROM  product")
    products= cursor.fetchall()
    connection.close()
    return render_template("index.html",products=products)

@app.route('/templates/products.html')
def products():
    connection=connect_db()
    cursor=connection.cursor()

    cursor.execute("SELECT * FROM product")
    products=cursor.fetchall()
    connection.close()

    return render_template("products.html",products=products)

@app.route("/templates/addproduct.html", methods=["GET","POST"])
def add_products():
    if request.method == "POST":
        connection = connect_db()
        cursor = connection.cursor()

        name = request.form.get('name')
        price = request.form.get('price')
        qty = request.form.get('qty')

        file = request.files.get('image')

        filename = ""
        if file and file.filename != "":
            ext = os.path.splitext(file.filename)[1]
            filename = str(uuid.uuid4()) + ext
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Always insert into DB even if file is empty
        sql = "INSERT INTO product (name,price,qty,image) VALUES (%s,%s,%s,%s)"
        cursor.execute(sql, (name, price, qty, filename))
        connection.commit()
        connection.close()
        return redirect(url_for('products'))

    # For GET request, always return template
    return render_template("add_products.html")
 
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM product WHERE id=%s", (id,))
    product = cursor.fetchone()

    if not product:
        connection.close()
        return "Product not found", 404

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        qty = request.form.get('qty')

        file = request.files.get('image')
        filename = product['image']  # keep old image if no new upload
        if file and file.filename != "":
            ext = os.path.splitext(file.filename)[1]
            filename = str(uuid.uuid4()) + ext
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        sql = "UPDATE product SET name=%s, price=%s, qty=%s, image=%s WHERE id=%s"
        cursor.execute(sql, (name, price, qty, filename, id))
        connection.commit()
        connection.close()
        return redirect(url_for('products'))

    connection.close()
    return render_template('edit_add_products.html', product=product)



@app.route('/update',methods=['POST'])
def update():
    if request.method=="POST":
        conection = connect_db()
        cursor = conection.cursor()

        name = request.form['name']
        price = request.form['price']
        qty = request.form['qty']
        id = request.form['id']


        sql = "UPDATE product SET name = %s, price=%s,qty=%s WHERE id = %s"
        cursor.execute(sql,(name,price,qty,id))
        conection.commit()

        return redirect(url_for('index'))
    return render_template("update.html")


@app.route('/delete', methods=["POST"])
def delete():
    connection = connect_db()
    cursor = connection.cursor()
    id = request.form.get('id')

    sql = "DELETE FROM product WHERE id = %s"
    cursor.execute(sql, (id,))
    connection.commit()
    connection.close()
    return redirect(url_for("index"))

if __name__=="__main__":
    print("server is running ...🎉🥳❤️")
    app.run(debug=True)
