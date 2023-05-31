from flask import Flask, render_template, request,redirect,url_for,session
from flask_socketio import SocketIO
from threading import Lock
from datetime import datetime
from paho.mqtt import client as mqtt_client
from email.message import EmailMessage
import random
import json
import pymysql
import pymysql.cursors
import re
import ssl
import smtplib
import secrets
import string
user=''
'''
    EMAIL PARAMETERS
'''
email_sender='carlosarzez25@gmail.com'
email_password='ohkkhnkblfckdmhn'
email_receiver=''
subject="Envio contraseña y password"
body=""
"""
    MQTT BROKER PARAMETERS
"""
broker = 'ec2-54-243-0-32.compute-1.amazonaws.com'
port = 1883
topic = "WSNPIITopic"
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'carlos'
password = 'carlos123'
usernameDisplay=''
"""Store data to database"""
def storedata(data):
    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='Carlos123#',
                             database='WSNProjectII')
    with connection:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `devices` (`value`, `description`,`node`,`registerDate`) VALUES (%s,%s,%s,%s)"
            cursor.execute(sql,(str(data["humidity"]), 'Dato enviado del sensor de humedad',str(1),datetime.now()))
            cursor.execute(sql,(str(data["temperature"]), 'Dato enviado del sensor de temperatura',str(2),datetime.now()))
            cursor.execute(sql,(str(data["co2"]), 'Dato enviado del sensor de dioxido de carbono',str(3),datetime.now()))
            cursor.execute(sql,(str(data["uv"]), 'Dato enviado del sensor de radiación uv',str(4),datetime.now()))
            sql = "INSERT INTO `nodestates` (`description`,`nodeState`,`registerDate`) VALUES (%s,%s,%s)"
            cursor.execute(sql,('Sensor de humedad',str(data["nodehumidity"]),datetime.now()))
            cursor.execute(sql,('Sensor de temperatura',str(data["nodetemperature"]),datetime.now()))
            cursor.execute(sql,('Sensor de uv',str(data["nodeuv"]),datetime.now()))
            cursor.execute(sql,('Sensor CO2',str(data["nodeco2"]),datetime.now()))
        connection.commit()
"""Get data from database"""
def Getdata(name,password):
    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='Carlos123#',
                             database='WSNProjectII')
    with connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `user` WHERE name=%s AND password = SHA1(%s)"
            cursor.execute(sql, (name,password))
            result = cursor.fetchone()
            return result
    
"""
Connect MQTT broker
"""
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client
"""
Subscribe MQTT broker
"""
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        x=msg.payload.decode()
        y=json.loads(x)
        print(y)
        storedata(y)
        socketio.emit('updateSensorData', {'value':y["humidity"], "date": get_current_datetime()})
        socketio.emit('updateSensorData2', {'value':y["temperature"], "date": get_current_datetime()})
        socketio.emit('updateSensorData3', {'value':y["co2"], "date": get_current_datetime()})
        socketio.emit('updateSensorData4', {'value':y["uv"], "date": get_current_datetime()})
        socketio.emit('updateSensorState', {'value':y["nodeuv"], "date": get_current_datetime()})
        socketio.emit('updateSensorState2', {'value':y["nodehumidity"], "date": get_current_datetime()})
        socketio.emit('updateSensorState3', {'value':y["nodetemperature"], "date": get_current_datetime()})
        socketio.emit('updateSensorState4', {'value':y["nodeco2"], "date": get_current_datetime()})
        socketio.sleep(0.2)
    client.subscribe(topic)
    client.on_message = on_message
    print (client.on_message)
   
"""
Background Thread
"""
thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'donsky!'
socketio = SocketIO(app, cors_allowed_origins='*')

"""
Get current date time
"""
def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")

def background_thread():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

"""
Serve root index file
"""
@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        global usernameDisplay
        name = request.form['username']
        usernameDisplay=name
        password = request.form['password']
        account=Getdata(name,password)
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[7]
            session['role'] = account[9]
            if(session['role'] == 'administrador'):
                return redirect(url_for('home'))
            else:
                return redirect(url_for('homeuser'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('pages/login.html', msg=msg)
@app.route('/home')
def home():
    global usernameDisplay
    return render_template('pages/index.html',username=usernameDisplay)
@app.route('/homeuser')
def homeuser():
    global usernameDisplay
    return render_template('pages/homeuser.html',username=usernameDisplay)
@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))
@app.route('/create',methods=['GET','POST'])
def create():
    global email_sender
    global email_password
    global email_receiver
    global subject
    global body
    global usernameDisplay
    if request.method == 'GET':
        connection = pymysql.connect(host='localhost',
                             user='root',
                             password='Carlos123#',
                             database='WSNProjectII')
        curs=connection.cursor()
        curs.execute("SELECT * FROM user WHERE status=1")
        users=curs.fetchall()
        return render_template('pages/userCRUD.html',users=users,username=usernameDisplay)
    if request.method == 'POST':
        connection = pymysql.connect(host='localhost',
                                user='root',
                                password='Carlos123#',
                                database='WSNProjectII')
        with connection:
            with connection.cursor() as cursor:
                if request.form['1']=='1':
                    ci = request.form['ci']
                    firstname = request.form['firstname']
                    lastname = request.form['lastname']
                    secondLastname = request.form['secondLastname']
                    gender = request.form['gender']
                    password = ''.join((secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(8)))
                    name = 'user'+''.join((secrets.choice(string.ascii_letters) for i in range(8)))
                    role = request.form['role']
                    email = request.form['email']
                    birthdate=request.form['birthdate']
                    registerDate=datetime.now()
                    sql = "INSERT INTO `user` (`ci`, `firstname`,`lastname`,`secondLastname`,`birthdate`,`gender`,`name`,`password`,`role`,`email`,`registerDate`,`userID` ) VALUES (%s,%s,%s, %s,%s, %s,%s,SHA1(%s),%s, %s,%s,%s)"
                    cursor.execute(sql, (ci, firstname,lastname,secondLastname,birthdate,gender,name,password,role,email,registerDate,1))
                    em=EmailMessage()
                    email_receiver=email
                    em['From']=email_sender
                    em['To']=email_receiver
                    em['Subject']=subject
                    body='Username: '+name+' Password: '+password
                    em.set_content(body)
                    context=ssl.create_default_context()
                    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
                        smtp.login(email_sender,email_password)
                        smtp.sendmail(email_sender,email_receiver,em.as_string())
                if request.form['1']=='2':
                    ci2 = request.form['ci2']
                    sql = "UPDATE user SET status = 0 WHERE ci=%s; "
                    cursor.execute(sql, (ci2))
                if request.form['1']=='3':
                    ci = request.form['ci3']
                    firstname = request.form['firstname3']
                    lastname = request.form['lastname3']
                    secondLastname = request.form['secondLastname3']
                    gender = request.form['gender3']
                    role = request.form['role3']
                    email = request.form['email3']
                    birthdate=request.form['birthdate3']
                    lastupdate=datetime.now()
                    sql = "UPDATE user SET ci=%s,firstname=%s,lastname=%s,secondLastname=%s,birthdate=%s,gender=%s,role=%s,email=%s,lastUpdate=%s,userID=%s WHERE ci=%s; "
                    cursor.execute(sql, (ci, firstname,lastname,secondLastname,birthdate,gender,role,email,lastupdate,1,ci))
            connection.commit()
        return redirect(url_for('create'))
@app.route('/historicstate')
def historicstate():
    global usernameDisplay
    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='Carlos123#',
                             database='WSNProjectII')
    curs=connection.cursor()
    curs.execute("SELECT * FROM nodestates")
    states=curs.fetchall()
    return render_template('pages/historicstates.html',states=states,username=usernameDisplay)
@app.route('/historic')
def historic():
    global usernameDisplay
    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='Carlos123#',
                             database='WSNProjectII')
    legend = 'Humidity Data'
    legend2 = 'Temperature Data'
    legend3= 'CO2 Data'
    legend4= 'UV Data'
    curs=connection.cursor()
    curs.execute("SELECT * FROM devices WHERE node=1")
    mesParameter=[]
    value=[]
    for row in curs:
        if(row[1]>0):
            mesParameter.append(row[4])
            value.append(row[1])
    labels = mesParameter
    curs.execute("SELECT * FROM devices WHERE node=2")
    mesParameter2=[]
    value2=[]
    for row in curs:
        if(row[1]>0):
            mesParameter2.append(row[4])
            value2.append(row[1])
    labels2 = mesParameter2
    curs.execute("SELECT * FROM devices WHERE node=3")
    mesParameter3=[]
    value3=[]
    for row in curs:
        if(row[1]>0):
            mesParameter3.append(row[4])
            value3.append(row[1])
    labels3 = mesParameter3
    curs.execute("SELECT * FROM devices WHERE node=4")
    mesParameter4=[]
    value4=[]
    for row in curs:
        if(row[1]>0):
            mesParameter4.append(row[4])
            value4.append(row[1])
    labels4 = mesParameter4
    curs.execute("SELECT * FROM devices")
    devices=curs.fetchall()
    return render_template('pages/historic.html',legend4=legend4,
                           legend3=legend3,legend2=legend2,legend=legend,
                           labels=labels,labels2=labels2,labels3=labels3,
                           labels4=labels4,values=value,values2=value2,values3=value3,
                           values4=value4,devices=devices,username=usernameDisplay)
"""
Decorator for connect
"""
@socketio.on('connect')
def connect():
    global thread
    print('Client connected')

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)

"""
Decorator for disconnect
"""
@socketio.on('disconnect')
def disconnect():
    print('Client disconnected',  request.sid)

if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0',port=5000,debug=True)
    