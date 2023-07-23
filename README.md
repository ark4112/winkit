#Winkit
Fresh eatables ordering service created using Python, Sanic framework and PostgreSQL.

Database design are as follows: 

User Table:
user_id (Primary Key)
username
password_hash (encrypted)
last_login

Category Table:
category_id (Primary Key)
category_name

Item Table:
item_id (Primary Key)
item_name
price
inventory_count
category_id (Foreign Key)

Cart Table:
cart_id (Primary Key)
user_id (Foreign Key)
item_id (Foreign Key)
quantity

Order Table:
order_id (Primary Key)
user_id (Foreign Key)
order_date
delivery_address_id (Foreign Key)

OrderItem Table:
order_item_id (Primary Key)
order_id (Foreign Key)
item_id (Foreign Key)
quantity
status (e.g., Delivered, In Progress, etc.)

DeliveryAddress Table:
address_id (Primary Key)
user_id (Foreign Key)
address
is_default (Boolean)

