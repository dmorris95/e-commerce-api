Welcome to the E-commerce-api!

GitHub: https://github.com/dmorris95/e-commerce-api

*Create a virtual environment in the folder where the code will be running from. Before running any code or installing extensions, run the virtual environment. Also ensure the following are installed: flask, flask-sqlalchemy, marshmallow.

The e-commerce api is a flask framework python application that works in hand with marshmallow to create schemas and models for a more streamlined application. It uses SQL Alchemy to help with the database aspect as well as using Postman for testing HTTP requests.

1. Customers 
    - The api allows for customers to be added into the database with proper valdiation for email and phone numbers.
    - Allows for the calling of all customers within the database displaying their name, email, phone, and their unique ID
    - Deleting existing customers from the database based on their unique ID
    - Updating existing customers information such as the name, email, or phone

2. Customer Accounts - Customer Accounts has a one-to-one relationship with Customers meaning one customer can have only one account and only one account can have one customer associated with it.
    - Creating customer accounts with a unique username and validation on the password. 
    - Displaying a customer account with the associated Customer's information such as name and email.
    - Updating a customer's account username or password with validation to ensure that username does not already exist
    - Delete a customer account based on the account_id

3. Products
    - Creating products based on their name and price
    - Displaying Product information based on its unique ID
    - Update a product's information given the unique ID
    - Delete a product from the database based on the ID given
    - Displaying all products that are within the database

4. Orders - Orders has a many-to-many relationship with products and one-to-many relationship with Customers. As a product can be on many orders and an order can have many products. A customer can have many orders but an order can be for only one customer.
    - Placing an order by providing the product id, customer id, and date the order is being placed. It keeps track of which products belong to which orders.
    - Displaying a specific order and the products that belong to that order
    - Displaying all of a customer's orders they have along with the the products associated with them.

