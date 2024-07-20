from flask import Flask, render_template, request,send_from_directory, abort, jsonify, redirect, url_for, send_file,make_response, Response
from database import get_current_password, update_password, admin_exists, user_exists, register_admin, register_user, add_user_details, add_user_details_admin, get_all_user_details, updateUserBasedOnID, deleteRecognition, user_get_user_details, toggleRequest, updateUserWithVideo, getID
import json
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import LargeBinary
import asyncio
import websockets
import base64
import argparse

import cv2
import mediapipe as mp
from ffpyplayer.player import MediaPlayer

from datetime import datetime
from matplotlib import pyplot as plt
import mss
import numpy as np
from scipy.signal import find_peaks
from scipy.spatial import distance as dist

from fer import FER

import threading
import time
import sys
from io import BytesIO
import os
from sqlalchemy.exc import OperationalError

import sys
sys.path.append('./model')
from intercept import main

app=Flask(__name__)



userGmailforrecognitions = ""

# Create SQLAlchemy engine
engine = create_engine("mysql+pymysql://u529185484_test:zB&0Tf8B!@srv1335.hstgr.io:3306/u529185484_test")

# Create a Session class to handle database sessions
Session = sessionmaker(bind=engine)

# Create a base class for declarative class definitions
Base = declarative_base()

# Define the UserDetail model
class UserDetail(Base):
    __tablename__ = 'user_detail'

    user_detail_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    interaction_date = Column(String(100), nullable=False)
    interaction_time = Column(String(100), nullable=False)
    address = Column(String(255))
    code = Column(String(50))
    isAdmin = Column(Boolean)
    html_content = Column(Text)  # Store HTML content as text
    requested = Column(Boolean)
    results = Column(Text)
    video = Column(LargeBinary(length=(2**32)-1))
    positive = Column(Text)
    negative = Column(Text)



@app.route('/addUserDetailByAdmin', methods=['POST'])
def addUserDetailsByAdmin():
    data = request.form
    full_name = request.form['full_name']
    email = request.form['email']
    interaction_date = request.form['interaction_date']
    interaction_time = request.form['interaction_time']
    address = request.form['address']
    code = request.form['code']
    results = request.form['results']
    logged_user_email = request.form['logged_user_email']

    success = add_user_details_admin({'logged_user_email': logged_user_email, 'full_name': full_name, 'email': email, 'interaction_date': interaction_date, 'interaction_time': interaction_time, 'address': address, 'code': code, 'results': results})
    user_detail_id = getID(full_name)
    if success:
        return render_template('Dashboard.html', logged_user_email=logged_user_email, data = data, user_detail_id=user_detail_id)
    else:
        return "Error: Failed to add user details", 500


@app.route('/add_user_details_by_user', methods=['POST'])
def addUserDetails():
    data = request.form
    full_name = request.form['full_name']
    email = request.form['email']
    interaction_date = request.form['interaction_date']
    interaction_time = request.form['interaction_time']
    address = request.form['address']
    code = request.form['code']
    results = request.form['results']
    logged_user_email = request.form['logged_user_email']

    success = add_user_details({'logged_user_email': logged_user_email, 'full_name': full_name, 'email': email, 'interaction_date': interaction_date, 'interaction_time': interaction_time, 'address': address, 'code': code, 'results': results})
    user_detail_id = getID(full_name)
    if success:
        return render_template('UserDashboard.html', logged_user_email=logged_user_email, data=data, user_detail_id=user_detail_id)
    else:
        return "Error: Failed to add user details", 500

@app.route('/update_user_detail_addingVideo_byUser', methods=['POST'])
def updateUSER():
    full_name = request.form['full_name']
    email = request.form['email']
    interaction_date = request.form['interaction_date']
    interaction_time = request.form['interaction_time']
    address = request.form['address']
    code = request.form['code']
    results = request.form['results']
    user_detail_id = request.form['user_detail_id']
    data = request.form

    positive_count = 0
    negative_count = 0
    try:
      with open(f"{full_name}_tell.txt", "r") as tell_file:
        for line in tell_file:
          tellX = int(line.strip())  # Read line, convert to int, and remove whitespace
          if tellX < 600:
            positive_count += 1
          else:
            negative_count += 1
    except FileNotFoundError:
      # Handle case where tellX file doesn't exist (optional)
      pass

    total_count = positive_count + negative_count
    positive_percentage = 0.0 if total_count == 0 else round((positive_count / total_count) * 100, 1)
    negative_percentage = 0.0 if total_count == 0 else round((negative_count / total_count) * 100, 1)

    # Call add_user_details function with userDetail dictionary
    success = updateUserWithVideo({
        'full_name': full_name,
        'user_detail_id': user_detail_id,
        'email': email,
        'interaction_date': interaction_date,
        'interaction_time': interaction_time,
        'address': address,
        'code': code,
        'results': results,
        'positive': positive_percentage,
        'negative': negative_percentage
    })

    logged_user_email = request.form['logged_user_email']
    user_detail_id = getID(full_name)
    
    user_detail_id = getID(full_name)
    if success:
        return render_template('UserDashboard.html', logged_user_email=logged_user_email, data=data, user_detail_id=user_detail_id)
    else:
        return "Error: Failed to add user details", 500
    

@app.route('/update_user_detail_addingVideo_byAdmin', methods=['POST'])
def updateUSERbyAdmin():
    full_name = request.form['full_name']
    user_detail_id = getID(full_name)
    email = request.form['email']
    interaction_date = request.form['interaction_date']
    interaction_time = request.form['interaction_time']
    address = request.form['address']
    code = request.form['code']
    results = request.form['results']
    # user_detail_id = request.form['user_detail_id']
    data = request.form

    positive_count = 0
    negative_count = 0
    try:
      with open(f"{full_name}_tell.txt", "r") as tell_file:
        for line in tell_file:
          tellX = int(line.strip())  # Read line, convert to int, and remove whitespace
          if tellX < 600:
            positive_count += 1
          else:
            negative_count += 1
    except FileNotFoundError:
      # Handle case where tellX file doesn't exist (optional)
      pass

    total_count = positive_count + negative_count
    positive_percentage = 0.0 if total_count == 0 else round((positive_count / total_count) * 100, 1)
    negative_percentage = 0.0 if total_count == 0 else round((negative_count / total_count) * 100, 1)

    # Call add_user_details function with userDetail dictionary
    success = updateUserWithVideo({
        'full_name': full_name,
        'user_detail_id': user_detail_id,
        'email': email,
        'interaction_date': interaction_date,
        'interaction_time': interaction_time,
        'address': address,
        'code': code,
        'results': results,
        'positive': positive_percentage,
        'negative': negative_percentage
    })

    
    logged_user_email = request.form['logged_user_email']

    if success:
        return render_template('Dashboard.html', logged_user_email=logged_user_email, data=data, user_detail_id=user_detail_id)
    else:
        return "Error: Failed to add user details", 500
    

@app.route('/downloadVideo', methods=['POST'])
def download_video():
    full_name = request.form['user_detail_id']
    if not full_name:
        return "Full name is required", 400

    filename = f"{full_name}.avi"
    if os.path.isfile(filename):
        # Send the file for download
        return send_from_directory(directory='.', path=filename, as_attachment=True)
    else:
        # File does not exist
        abort(404, description="File not found")



@app.route('/uploadFile', methods=['POST'])
def upload_html():
    user_detail_id = request.form['user_detail_id']
    
    if 'file' not in request.files:
        return jsonify({'message': 'No HTML file part'}), 400
    
    html_file = request.files['file']
    
    if html_file.filename == '':
        return jsonify({'message': 'No selected HTML file'}), 400
    data = get_all_user_details()
    logged_user_email = request.form['logged_user_email']
    # Read HTML content
    html_content = html_file.read().decode('utf-8')

    # Store HTML content in the database
    session = Session()
    user_detail = session.query(UserDetail).filter_by(user_detail_id=user_detail_id).first()
    user_detail.html_content = html_content
    user_detail.requested = False  # Toggle request to False
    session.commit()
    session.close()

    # return render_template('Admin.html', logged_user_email=logged_user_email, data=data)
    return redirect(url_for('ManageRecognition', logged_user_email=logged_user_email, data=data))


@app.route('/downloadFile/<int:user_detail_id>', methods=['GET'])
def download_html(user_detail_id):
    # Retrieve HTML content from the database
    session = Session()
    user_detail = session.query(UserDetail).filter_by(user_detail_id=user_detail_id).first()

    if user_detail:
        html_content = user_detail.html_content

        if html_content:
            # Send the HTML content as a response
            response = make_response(html_content)
            response.headers['Content-Type'] = 'text/html'
            response.headers['Content-Disposition'] = 'attachment; filename=file.html'
            # Remove the html_content from the user_detail record
            user_detail.html_content = None
            session.commit()
            session.close()

            return response
        else:
            session.close()
            return jsonify({'message': 'HTML content not found'})
    else:
        session.close()
        return jsonify({'message': 'User detail not found'})


@app.route('/requestReportbyAdmin', methods=['POST'])
def requestReportbyAdmin():
    getted = request.form
    user_detail_id = request.form['user_detail_id']
    toggleRequest(user_detail_id=user_detail_id)
    logged_user_email = request.args.get('logged_user_email')

    data = user_get_user_details(getted['logged_user_email'])
    return redirect(url_for('userManageRecognition', logged_user_email=getted['logged_user_email'] ))
    # return getted['logged_user_email']


@app.route('/admin')
def admin():
    return render_template('Admin.html')

@app.route('/manageUsersUpdateData', methods=['POST'])
def manageUsersUpdate():
    data = request.form
    full_name = request.form['full_name']
    email = request.form['email']
    interaction_date = request.form['interaction_date']
    interaction_time = request.form['interaction_time']
    address = request.form['address']
    code = request.form['code']
    logged_user_email = request.form['logged_user_email']
    results = request.form['results']

    user_detail_id = request.form['user_detail_id']
    
    # Call add_user_details function with userDetail dictionary
    success = updateUserBasedOnID({'user_detail_id': user_detail_id, 'full_name': full_name, 'email': email, 'interaction_date': interaction_date, 'interaction_time': interaction_time, 'address': address, 'code': code, 'results': results})
    data = get_all_user_details()
    if success:
        return render_template('ManageUsers.html', logged_user_email=logged_user_email, data=data)
    else:
        return "Error: Failed to add user details", 500
    
    

@app.route('/login')
def login():
    return render_template('Login.html')

@app.route('/adminLogin', methods=['POST'])
def adminLogin():
    admin_username = request.form['adminUsername']
    admin_password = request.form['adminPassword']
    if admin_exists(admin_username, admin_password):
        return render_template('Dashboard.html', logged_user_email=admin_username, data = {})
    else:
        return render_template('Login.html')
    # return (admin_username)
    

logUser = ""
@app.route('/userLogin', methods=['POST'])
def userLogin():
    user_username = request.form['userUsername']
    user_password = request.form['userPassword']
    logUser = user_username
    if user_exists(user_username, user_password):
        return render_template('UserDashboard.html', logged_user_email=user_username, data={})
    else:
        return render_template('Login.html')
    
@app.route('/userRegister', methods=['POST'])
def userRegister():
    user_email = request.form['registerEmail']
    user_password = request.form['registerPassword']
    register_user(user_email, user_password)
    return render_template('Login.html')

@app.route('/adminRegister', methods=['POST'])
def adminRegister():
    admin_email = request.form['registerEmail']
    admin_password = request.form['registerPassword']
    register_admin(admin_email, admin_password)
    return render_template('Login.html')

@app.route('/dashboard')
def dashboard():
    logged_user_email = request.args.get('logged_user_email')
    return render_template('Dashboard.html', logged_user_email=logged_user_email, data = {})


@app.route('/userDashboard')
def userDashboard():
    logged_user_email = request.args.get('logged_user_email')
    # return f"Logged user mail: {logged_user_mail}"
    return render_template('UserDashboard.html', logged_user_email=logged_user_email, data = {})

@app.route('/userManageRecognition')
def userManageRecognition():
    logged_user_email = request.args.get('logged_user_email')
    data = user_get_user_details(logged_user_email)
    return render_template('UserManageRecognition.html', logged_user_email=logged_user_email, data=data)

@app.route('/ManageRecognition')
def ManageRecognition():
    data = get_all_user_details()
    logged_user_email = request.args.get('logged_user_email')
    return render_template('Admin.html', logged_user_email=logged_user_email, data=data)

@app.route('/userLieDetectionSession')
def userLieDetectionSession():
    logged_user_email = request.args.get('logged_user_email')
    data = user_get_user_details(logged_user_email)
    return render_template('UserLieDetectionSession.html', logged_user_email=logged_user_email, data=data)

@app.route('/LieDetectionSession')
def LieDetectionSession():
    logged_user_email = request.args.get('logged_user_email')
    data = get_all_user_details()
    return render_template('LieDetectionSession.html', logged_user_email=logged_user_email, data=data)

@app.route('/ManageUsers')
def ManageUsers():
    logged_user_email = request.args.get('logged_user_email')
    data = get_all_user_details()
    return render_template('ManageUsers.html', logged_user_email=logged_user_email, data=data)
    
@app.route('/helpAndSupport')
def HelpAndSupport():
    logged_user_email = request.args.get('logged_user_email')
    data = get_all_user_details()
    def is_positive(value):
        try:
            return int(value) > 0
        except ValueError:
            return False
    
    positive_count = sum(1 for item in data if is_positive(item['results']))
    return render_template('HelpAndSupport.html', logged_user_email=logged_user_email, data=data, positive_count=positive_count)


# @app.route('/updatePassword')
# def updatePassword():
#     logged_user_email = request.form['logged_user_email']
#     cpass = request.form['cpass']
#     npass = request.form['npass']
#     rpass = request.form['rpass']
#     data = get_all_user_details()

#     # change password db function

#     render_template('SettingsAndPreference.html', logged_user_email=logged_user_email, data=data)
@app.route('/updatePassword', methods=['POST'])
def update_password_route():
    logged_user_email = request.form['logged_user_email']
    cpass = request.form['cpass']  # Current password
    npass = request.form['npass']  # New password
    rpass = request.form['rpass']  # Repeat new password

    # Get the current password from the database
    current_password = get_current_password(logged_user_email)

    # Check if the provided current password matches
    if cpass != current_password:
        return "Current password is incorrect", 400

    # Check if the new passwords match
    if npass != rpass:
        return "New passwords do not match", 400

    # Update the password in the database
    update_password(logged_user_email, npass)

    return redirect(url_for('settingsAndPreference', logged_user_email=logged_user_email))


@app.route('/settingsAndPreference')
def settingsAndPreference():
    logged_user_email = request.args.get('logged_user_email')
    data = get_all_user_details()
    return render_template('SettingsAndPreference.html', logged_user_email=logged_user_email, data=data)

@app.route('/deleteLiebyAdmin', methods=['POST'])
def delLie():
    user_detail_id = request.form['user_detail_id']
    logged_user_email = request.form['logged_user_email']
    deleteRecognition(user_detail_id)
    data = get_all_user_details()
    return render_template('LieDetectionSession.html', logged_user_email=logged_user_email, data=data, user_detail_id=user_detail_id)

@app.route('/deleteLiebyUser', methods=['POST'])
def delLiebyUser():
    user_detail_id = request.form['user_detail_id']
    logged_user_email = request.form['logged_user_email']
    deleteRecognition(user_detail_id)
    data = user_get_user_details(logged_user_email)
    return render_template('UserLieDetectionSession.html', logged_user_email=logged_user_email, data=data, user_detail_id=user_detail_id)

@app.route('/deleteRecognitioinUsingIDByAdmin', methods=['POST'])
def deleteRecognitionUsingID():
    user_detail_id = request.form['user_detail_id']
    logged_user_email = request.form['logged_user_email']
    # data = request.form
    deleteRecognition(user_detail_id)
    data = get_all_user_details()
    # return data
    return render_template('Admin.html', logged_user_email=logged_user_email, data=data, user_detail_id=user_detail_id)

@app.route('/deleteRecognitioinUsingIDByUser', methods=['POST'])
def deleteRecognitionUsingIDbyUser():
    user_detail_id = request.form['user_detail_id']
    logged_user_email = request.form['logged_user_email']
    deleteRecognition(user_detail_id)
    data = user_get_user_details(logged_user_email)
    return render_template('UserManageRecognition.html', logged_user_email=logged_user_email, data=data, user_detail_id=user_detail_id)


@app.route('/')
def index():
    return render_template('Login.html')

@app.route('/video')
def video():
    full_name = request.args.get('full_name')
    return Response(main(full_name),mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)