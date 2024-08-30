from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from marshmallow import ValidationError
from sqlalchemy import insert, select

#ensure proper environment is being used

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:<your_password>@127.0.0.1/e_commerce_db'

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)

#Set Customer Schema
class CustomerSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    email = fields.String(required=True)
    phone = fields.String(required=True, validate=validate.Length(min=10))

    class Meta:
        fields = ("id", "name", "email", "phone")

#Set Products Schema
class ProductSchema(ma.Schema):
    
    name = fields.String(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))

    class Meta:
        fields = ("id", "name", "price")

#Set Customer Accounts Schema
class CustomerAccountsSchema(ma.Schema):

    username = fields.String(required=True, validate=validate.Length(min=1))
    password = fields.String(required=True, validate=validate.Length(min=1))
    customer_id = fields.Integer(required=True)
    customer = fields.Nested(CustomerSchema(only=("name","email", "phone")))

    class Meta:
        fields = ("username", "password", "customer_id", "id", "customer")

#Set Orders Products Schema
class OrderProductSchema(ma.Schema):
    
    product = fields.Nested(ProductSchema)

    class Meta:
        fields = ("name", "price")

#Set Orders Schema
class OrderSchema(ma.Schema):
    customer_id = fields.Integer(required=True)
    date = fields.Date(required=True)
    products = fields.Nested(OrderProductSchema, many=True)

    class Meta:
        fields = ("id", "customer_id", "date", "products")


order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

cust_account_schema = CustomerAccountsSchema()

product_schema = ProductSchema()
products_schema = ProductSchema(many=True) #for gathering multiple products

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

class Customer(db.Model): #setup customers table
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    orders = db.relationship('Order', backref='customer') #one to many relationship

class Order(db.Model): #setup order table
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))

#one-to-one relationship
class CustomerAccount(db.Model):
    __tablename__ = 'Customer_Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer = db.relationship('Customer', backref='customer_account', uselist=False)

#many-to-many relationship
order_product = db.Table('Order_Product',
        db.Column('order_id', db.Integer, db.ForeignKey('orders.id'), primary_key=True),
        db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    orders = db.relationship('Order', secondary=order_product, backref=db.backref('products'))


@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers)

@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    query = select(Customer).filter(Customer.id == id)
    result = db.session.execute(query).scalars().first()
    if result is None:
        return jsonify({"error": "Customer not found"})
    customer = result
    return customer_schema.jsonify(customer)

@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        #validate and deserialize
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "New customer added successfully"}), 201

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']
    db.session.commit()
    return jsonify({"message": "Customer successfully updated"}), 200


@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer removed successsfully"}), 200

#CustomerAccounts endpoints
@app.route('/customeraccounts/<int:id>', methods=['GET'])
def get_custaccount(id):
    customer_account = CustomerAccount.query.get_or_404(id)
    return cust_account_schema.jsonify(customer_account)

@app.route('/customeraccounts', methods=['POST'])
def add_custaccount():
    try:
        account_data = cust_account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_account = CustomerAccount(username=account_data['username'], password=account_data['password'], customer_id=account_data['customer_id'])
    db.session.add(new_account)
    db.session.commit()
    return jsonify({"message": "New Customer Account added successfully"}), 201

@app.route('/customeraccounts/<int:id>', methods={'PUT'})
def update_custaccount(id):
    cust_account = CustomerAccount.query.get_or_404(id)
    try:
        account_data = cust_account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    cust_account.username = account_data['username']
    cust_account.password = account_data['password']
    db.session.commit()
    return jsonify({"message": "Customer account successfully updated"}), 200

@app.route('/customeraccounts/<int:id>', methods=['DELETE'])
def delete_custaccount(id):
    cust_account = CustomerAccount.query.get_or_404(id)
    db.session.delete(cust_account)
    db.session.commit()
    return jsonify({"message": "Customer account deleted successfully"})

#Orders Endpoints
#post
@app.route('/orders/<int:id>', methods=['POST'])
def add_order(id):
    product = Product.query.get_or_404(id) #verify product exists
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_order = Order(date=order_data['date'], customer_id=order_data['customer_id'])
    db.session.add(new_order)
    db.session.commit()
    db.session.refresh(new_order) #gets id of the new order
    #Insert the order to the association table
    stm = insert(order_product).values(order_id = str(new_order.id), product_id = str(id))
    db.session.execute(stm)
    db.session.commit()
    return jsonify({"message" : "New order successfully created"})

#Added new route to handle multiple products for one order
@app.route('/order/<int:ids>', methods=['POST'])
def add_multiple_products(ids):
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_order = Order(date=order_data['date'], customer_id=order_data['customer_id'])
    db.session.add(new_order)
    db.session.commit()
    db.session.refresh(new_order) #gets id of the new order
    #Set Ids into list for iteration
    id_list = [int(n) for n in str(ids)]
    for n in id_list:
        db.session.refresh(new_order) #gets id of the new order
        stm = insert(order_product).values(order_id = str(new_order.id), product_id = str(n))
        db.session.execute(stm)
        db.session.commit()
    return jsonify({"message" : "New order successfully created"})

#get specifc order
@app.route('/orders/<int:id>', methods=['GET'])
def get_order_details(id):
    product_order = Order.query.get_or_404(id)
    return order_schema.jsonify(product_order)

#get all orders for specific customer
@app.route('/orders/by-customer_id', methods=['GET'])
def get_all_customer_orders():
    #query to get order ids/dates for customer_id
    customer_id = request.args.get('customer_id')
    orders = Order.query.filter_by(customer_id=customer_id).all()
    if orders:
        return orders_schema.jsonify(orders)
    else:
        return jsonify({"message" : "Customer not found"})

#Product endpoints
@app.route('/products', methods=['POST'])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_product = Product(name=product_data['name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "New product added successfully"}), 201

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    query = select(Product).filter(Product.id == id)
    result = db.session.execute(query).scalars().first()
    if result is None:
        return jsonify({"error": "Product not found"})
    product = result
    return product_schema.jsonify(product)

@app.route('/products', methods=['GET'])
def get_all_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    product.name = product_data['name']
    product.price = product_data['price']
    db.session.commit()
    return jsonify({"message": "Product successfully updated"}), 200

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product successfully deleted"}), 200

#intialize database and create tables

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
