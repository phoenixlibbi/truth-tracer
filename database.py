from sqlalchemy import create_engine, text
from werkzeug.utils import secure_filename
import os

# from app import Session

engine = create_engine("mysql+pymysql://u529185484_test:zB&0Tf8B!@srv1335.hstgr.io:3306/u529185484_test")

def admin_exists(email, password):
    # Execute the query to check if admin exists with given email and password
    query = text("SELECT COUNT(*) FROM admin WHERE email = :userEmail AND password = :password")
    with engine.connect() as conn:
        result = conn.execute(query, {'userEmail': email, 'password': password})
        count = result.scalar()
    return count > 0

def user_exists(email, password):
    # Execute the query to check if user exists with given email and password
    query = text("SELECT COUNT(*) FROM user WHERE email = :email AND password = password")
    with engine.connect() as conn:
        result = conn.execute(query, {'email': email, 'password': password})
        count = result.scalar()
    return count > 0

def register_user(email, password):
    # Execute the query to insert user into the database
    query = text("INSERT INTO user (`email`, `password`) VALUES (:email, :password)")
    with engine.connect() as conn:
        try:
            if not user_exists(email, password):
                conn.execute(query, {'email': email, 'password': password})
                print("User registered successfully")
                # Commit the transaction
                conn.commit()
            else:
                print("User already exists")
        except Exception as e:
            print(f"Error: {e}")

def register_admin(email, password):
    # Execute the query to insert admin into the database
    query = text("INSERT INTO admin (`email`, `password`) VALUES (:email, :password)")
    with engine.connect() as conn:
        try:
            if not admin_exists(email, password):
                conn.execute(query, {'email': email, 'password': password})
                print("Admin registered successfully")
                # Commit the transaction
                conn.commit()
            else:
                print("Admin already exists")
        except Exception as e:
            print(f"Error: {e}")

# CREATE TABLE user_detail (
#     user_detail_id INT AUTO_INCREMENT PRIMARY KEY,
#     user_id INT,
#     full_name VARCHAR(100) NOT NULL,
#     email VARCHAR(100) UNIQUE NOT NULL,
#     interaction_date DATE NOT NULL,
#     interaction_time TIME NOT NULL,
#     address VARCHAR(255),
#     code VARCHAR(50),
#     results TEXT,
#     FOREIGN KEY (user_id) REFERENCES user(user_id)
# );

def get_logged_user_id(email):
    query = text("SELECT user_id FROM user WHERE email = :email")
    with engine.connect() as conn:
        result = conn.execute(query, {'email': email})
        user_id = result.scalar()
    print("User ID retrieved:", user_id)  # Add this line for debugging
    return user_id


# def add_user_details(userDetail):
#     logged_user_id = get_logged_user_id(userDetail['logged_user_email'])
#     query = text("INSERT INTO user_detail (`user_id`, `full_name`, `email`, `interaction_date`, `interaction_time`, `address`, `code`, `results`, `isAdmin`, `requested`) VALUES (:user_id, :full_name, :email, :interaction_date, :interaction_time, :address, :code, :results, 0, 0)")
#     with engine.connect() as conn:
#         # userDetail is a json object
#         try:
#             conn.execute(query, {'user_id': logged_user_id, 'full_name': userDetail['full_name'], 'email': userDetail['email'], 'interaction_date': userDetail['interaction_date'], 'interaction_time': userDetail['interaction_time'], 'address': userDetail['address'], 'code': userDetail['code'], 'results': userDetail['results']})
#             print("User details added successfully")
#             # Commit the transaction
#             conn.commit()
#             return True
#         except Exception as e:
#             print(f"Error: {e}")
        
def add_user_details(userDetail):
    logged_user_id = get_logged_user_id(userDetail['logged_user_email'])
    
    # Query to check if the user already exists based on full name
    check_query = text("SELECT COUNT(*) FROM user_detail WHERE full_name = :full_name")
    
    # Insert query
    insert_query = text("""
        INSERT INTO user_detail 
        (`user_id`, `full_name`, `email`, `interaction_date`, `interaction_time`, `address`, `code`, `results`, `isAdmin`, `requested`) 
        VALUES (:user_id, :full_name, :email, :interaction_date, :interaction_time, :address, :code, :results, 0, 0)
    """)

    with engine.connect() as conn:
        try:
            # Check if user exists
            result = conn.execute(check_query, {'full_name': userDetail['full_name']})
            user_exists = result.scalar() > 0  # Returns True if count > 0

            if user_exists:
                print("User already exists.")
                return True
            else:
                # Insert new user details
                conn.execute(insert_query, {
                    'user_id': logged_user_id, 
                    'full_name': userDetail['full_name'], 
                    'email': userDetail['email'], 
                    'interaction_date': userDetail['interaction_date'], 
                    'interaction_time': userDetail['interaction_time'], 
                    'address': userDetail['address'], 
                    'code': userDetail['code'], 
                    'results': userDetail['results']
                })
                print("User details added successfully")
                # Commit the transaction
                conn.commit()
                return True

        except Exception as e:
            print(f"Error: {e}")
            return False

def get_logged_admin_id(email):
    query = text("SELECT admin_id FROM admin WHERE email = :email")
    with engine.connect() as conn:
        result = conn.execute(query, {'email': email})
        user_id = result.scalar()
    print("User ID retrieved:", user_id)  # Add this line for debugging
    return user_id

from sqlalchemy import text

def add_user_details_admin(userDetail):
    logged_user_id = get_logged_admin_id(userDetail['logged_user_email'])
    
    # Query to check if the user already exists based on full name
    check_query = text("SELECT COUNT(*) FROM user_detail WHERE full_name = :full_name")
    
    # Insert query
    insert_query = text("""
        INSERT INTO user_detail 
        (`user_id`, `full_name`, `email`, `interaction_date`, `interaction_time`, `address`, `code`, `results`, `isAdmin`, `requested`) 
        VALUES (:user_id, :full_name, :email, :interaction_date, :interaction_time, :address, :code, :results, 1, 0)
    """)

    with engine.connect() as conn:
        try:
            # Check if user exists
            result = conn.execute(check_query, {'full_name': userDetail['full_name']})
            user_exists = result.scalar() > 0  # Returns True if count > 0

            if user_exists:
                print("User already exists.")
                return True
            else:
                # Insert new user details
                conn.execute(insert_query, {
                    'user_id': logged_user_id, 
                    'full_name': userDetail['full_name'], 
                    'email': userDetail['email'], 
                    'interaction_date': userDetail['interaction_date'], 
                    'interaction_time': userDetail['interaction_time'], 
                    'address': userDetail['address'], 
                    'code': userDetail['code'], 
                    'results': userDetail['results']
                })
                print("User details added successfully")
                # Commit the transaction
                conn.commit()
                return True

        except Exception as e:
            print(f"Error: {e}")
            return False



# def add_user_details_admin(userDetail):
#     logged_user_id = get_logged_admin_id(userDetail['logged_user_email'])
#     query = text("INSERT INTO user_detail (`user_id`, `full_name`, `email`, `interaction_date`, `interaction_time`, `address`, `code`, `results`, `isAdmin`, `requested`) VALUES (:user_id, :full_name, :email, :interaction_date, :interaction_time, :address, :code, :results, 1, 0)")
#     with engine.connect() as conn:
#         # userDetail is a json object
#         try:
#             conn.execute(query, {'user_id': logged_user_id, 'full_name': userDetail['full_name'], 'email': userDetail['email'], 'interaction_date': userDetail['interaction_date'], 'interaction_time': userDetail['interaction_time'], 'address': userDetail['address'], 'code': userDetail['code'], 'results': userDetail['results']})
#             print("User details added successfully")
#             # Commit the transaction
#             conn.commit()
#             return True
#         except Exception as e:
#             print(f"Error: {e}")
        

def get_user_details(email):
    query = text("SELECT * FROM user_detail WHERE email = :email")
    with engine.connect() as conn:
        result = conn.execute(query, {'email': email})
        user_detail = result.fetchone()
    return user_detail

def getID(full_name):
    with engine.connect() as conn:
        # Prepare SQL query
        query = text("SELECT user_detail_id FROM user_detail WHERE full_name = :full_name")

        # Execute the query
        result = conn.execute(query, {'full_name': full_name})

        # Fetch the user_detail_id
        row = result.fetchone()
        if row:
            return row[0]  # Return the user_detail_id
        else:
            return None

def get_all_user_details():
    query = text("SELECT * FROM user_detail")
    with engine.connect() as conn:
        result = conn.execute(query)
        column_names = result.keys()
        user_details = [dict(zip(column_names, row)) for row in result.fetchall()]
    return user_details

details = get_all_user_details()
# print(details)

def user_get_user_details(email):
    user_id = get_logged_user_id(email)
    query = text("SELECT * FROM user_detail WHERE user_id = :user_id and isAdmin = 0")
    with engine.connect() as conn:
        result = conn.execute(query, {'user_id': user_id})
        column_names = result.keys()
        user_details = [dict(zip(column_names, row)) for row in result.fetchall()]
    return user_details

def updateUserBasedOnID(userDetail):
    query = text("UPDATE user_detail SET full_name = :full_name, email = :email, interaction_date = :interaction_date, interaction_time = :interaction_time, address = :address, code = :code, results = :results WHERE user_detail_id = :user_id")
    with engine.connect() as conn:
        try:
            conn.execute(query, {'full_name': userDetail['full_name'], 'email': userDetail['email'], 'interaction_date': userDetail['interaction_date'], 'interaction_time': userDetail['interaction_time'], 'address': userDetail['address'], 'code': userDetail['code'], 'results': userDetail['results'], 'user_id': userDetail['user_detail_id']})
            print("User details updated successfully")
            # Commit the transaction
            conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")

def updateUserWithVideo(userDetail):
    query = text("UPDATE user_detail SET full_name = :full_name, email = :email, interaction_date = :interaction_date, interaction_time = :interaction_time, address = :address, code = :code, results = :results, positive = :positive, negative = :negative WHERE user_detail_id = :user_id")
    with engine.connect() as conn:
        try:
            conn.execute(query, {'full_name': userDetail['full_name'], 'email': userDetail['email'], 'interaction_date': userDetail['interaction_date'], 'interaction_time': userDetail['interaction_time'], 'address': userDetail['address'], 'code': userDetail['code'], 'results': userDetail['results'], 'user_id': userDetail['user_detail_id'], 'positive': userDetail['positive'], 'negative': userDetail['negative']})
            print("User details updated successfully")
            # Commit the transaction
            conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")


def toggleRequest(user_detail_id):
    # Query to check if the user_detail_id exists in user_detail table
    query_check_user = text("SELECT COUNT(*) FROM user_detail WHERE user_detail_id = :user_id and isAdmin = 0")

    # Query to update the requested field in user_detail table
    query_update_requested = text("UPDATE user_detail SET requested = NOT requested WHERE user_detail_id = :user_id and isAdmin = 0")

    with engine.connect() as conn:
        try:
            # Check if user_detail_id exists in user_detail table
            result = conn.execute(query_check_user, {'user_id': user_detail_id})
            count = result.scalar()

            if count == 1:
                # Update the requested field
                conn.execute(query_update_requested, {'user_id': user_detail_id})
                print("Requested status toggled successfully")
                conn.commit()
                return True
            else:
                print("User not found")
                return False
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()
            return False


def deleteRecognition(user_id):
    query = text("DELETE FROM user_detail WHERE user_detail_id = :user_id")
    with engine.connect() as conn:
        try:
            conn.execute(query, {'user_id': user_id})
            print("User details deleted successfully")
            # Commit the transaction
            conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")



# Function to store file content in MySQL
def store_file_content(user_detail_id, file_content):
    query = text("UPDATE user_detail SET pdf_file = :file_content WHERE user_detail_id = :user_id")
    with engine.connect() as conn:
        conn.execute(query, {'file_content': file_content, 'user_id': user_detail_id})

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

def get_current_password(email):
    session = Session()
    try:
        result = session.execute(text("SELECT password FROM admin WHERE email = :email"), {'email': email})
        current_password = result.scalar()
    finally:
        session.close()
    return current_password

def update_password(email, new_password):
    session = Session()
    try:
        session.execute(text("UPDATE admin SET password = :new_password WHERE email = :email"), {'new_password': new_password, 'email': email})
        session.commit()
    finally:
        session.close()