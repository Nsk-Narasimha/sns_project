# from flask import Flask,render_template,url_for,redirect,request
# import uuid
# app = Flask(__name__)
# @app.route('/')
# def home():
#     # return "flask is running"
#     return render_template('index.html')
# #
# @app.route('/register/')
# def register():
#     return render_template('register.html')
    

# @app.route('/login/',methods=['GET'])
# def login():
#     return render_template('login.html')

# @app.route('/dashboard/')
# def dashboard():
#     return render_template('dashboard.html')

# @app.route('/notes/')
# def notes():
#     return render_template('notes.html')

# if __name__ == "__main__":
#     app.run(host='0.0.0.0',port=5001,debug=True)
from huggingface_hub import upload_folder

from config import Config,emailTemplates
import mysql.connector as sql
import random
import smtplib
import bcrypt
from email.message import EmailMessage
from flask import Flask,render_template,url_for,redirect,request,session,flash,send_file
from itsdangerous import URLSafeTimedSerializer,BadSignature,SignatureExpired,TimedSerializer
from werkzeug.utils import secure_filename
import os,sys

if not os.path.exists('upload'):
    os.makedirs('upload')
app = Flask(__name__)
app.secret_key = 'nsk'
DBConfig = Config()
from_email=DBConfig.from_email
email_app_password=DBConfig.email_app_password
def generateHash(text):
    btext=text.encode('utf-8')
    # print(text,btext)
    cipher=bcrypt.hashpw(btext,bcrypt.gensalt(5))
    # print(cipher)
    return cipher.decode('utf-8')
# print(generateHash('123456'))
#we can use the DBConfig class to access the database configuration values
# we will use these values to connect to the database using mysql.connector
def getConnectionWithDB():
    db_host = DBConfig.db_host
    db_user = DBConfig.db_user
    db_port = DBConfig.db_port
    db_password = DBConfig.db_password
    db_name = DBConfig.db_name
    try:
        connection = sql.connect(
            host=db_host,
            user=db_user,
            port=db_port,
            password=db_password,
            database=db_name
        )
        return connection
    except:
        return "connection failed"
# print(getConnectionWithDB())
def insertUserRecord(user_data):
    name = user_data['name']
    email = user_data['email']
    password_hash = user_data['password_hash']
    connection = getConnectionWithDB()
    if connection == "connection failed":
        return False
    else:
        try:
            cursor = connection.cursor()
            # query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
            # values = (name, email, password)
            # cursor.execute(query, values)
            cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)", (name, email, password_hash))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except:
            print("data cannot be inserted")
            return False
# # define data
# data = [{
#     'name': 'Narasimha',
#     'email': 'narasimha123@gmail.com',
#     'password_hash': '123nsk'
# },{
#     'name': 'sai',
#     'email': 'sai123@gmail.com',
#     'password_hash': '123nsk'
# },{
#     'name': 'kumar',
#     'email': 'kumar123@gmail.com',
#     'password_hash': '123nsk'
# },{
#     'name': 'sanjay',
#     'email': 'sanjay123@gmail.com',
#     'password_hash': '123nsk'
# }]
# for d in data:
#     print(insertUserRecord(d))
# # insert data into database
# d={}
# d['name']=input("enter name:")
# d['email']=input("enter email:")
# d['password_hash']=input("enter password:")
# print(insertUserRecord(d))
def readUserRecords():
    connection=getConnectionWithDB()
    if(connection=='connection failed'):
        return False
    else:
        cursor=connection.cursor()
        cursor.execute("select *from users;")
        data=cursor.fetchall()
        records=[]
        for record in data:
            temp={}
            temp['id']=record[0]
            temp['name']=record[1]
            temp['email']=record[2]
            temp['password']=record[3]
            temp['isverified']=record[4]
            temp['created_at']=record[5]
            records.append(temp)
        cursor.close()
        connection.close()
        return records
#print(readUserRecords())

def readUserRecordByEmail(email):
    connection=getConnectionWithDB()
    if(connection=='connection failed'):
        return False
    else:
        try:
            cursor=connection.cursor()
            # cursor.execute(f"select *from users where email='{email}';")
            cursor.execute('select *from users where email=%s',(email,))
            data=cursor.fetchone()
            #print(data)
            record={
                'id':data[0],
                'name':data[1],
                'email':data[2],
                'password':data[3],
                'isverified':data[4],
                'created_at':data[5]
            }
            return record
        except:
            cursor.close()
            connection.close()
            return 'no records found'
#print(readUserRecordByEmail('sai123@gmail.com'))

def readUserRecordById(id):
    connection=getConnectionWithDB()
    if(connection=='connection failed'):
        return False
    else:
        cursor=connection.cursor()
        cursor.execute(f"select *from users where id='{id}';")
        #data=cursor.fetchall()
        data=cursor.fetchone()
        #print(data) 
        if data==None:
            return "no records found"
        else: 
            record={
                            'id':data[0],
                            'name':data[1],
                            'email':data[2],
                            'password':data[3],
                            'isverified':data[4],
                            'created_at':data[5]
                        }
            return record
#print(readUserRecordById(7))

def updateNameByIdorEmail(user_data):
    query_filter=""
    try:
        id=user_data['id']
        query_filter='id'
    except:
        email=user_data['email']
        query_filter='email'
    new_name=user_data['new_name']
    #email=user_data['email']
    connection=getConnectionWithDB()
    if connection == 'Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        if query_filter=='id':
            query="update users set name=%s where id=%s"
            #query="update users set name=%s,email=%s where id=%s"
            # values=(new_name,email,id)
            values=(new_name,id)
        elif query_filter=='email':
            query="update users set name=%s where email=%s"
            values=(new_name,email)
        cursor.execute(query,values)
        connection.commit()
        cursor.close()
        connection.close()
        return True
        
# user_data={'id':4,'new_name':'NSK','email':'nsk123@gmail.com'}
# print(updateNameByIdorEmail(user_data))

def updatePasswordByIdorEmail(user_data):
    query_filter=""
    try:
        id=user_data['id']
        query_filter='id'
    except:
        email=user_data['email']
        query_filter='email'
    new_password=user_data['new_password']
    connection=getConnectionWithDB()
    if connection == 'Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        if query_filter=='id':
            query="update users set password_hash=%s where id=%s"

            values=(new_password,id)
        elif query_filter=='email':
            query="update users set password_hash=%s where email=%s"
            values=(new_password,email)
        cursor.execute(query,values)
        connection.commit()
        cursor.close()
        connection.close()
        return True
            
# user_data={'email':'nsk123@gmail.com','new_password':'n1s2k3','confirm_password':'n1s2k3'}
# print(updatePasswordByIdorEmail(user_data))

def updateVerifiedByIdorEmail(user_data):
    query_filter=""
    try:
        id=user_data['id']
        query_filter='id'
    except:
        email=user_data['email']
        query_filter='email'
    verified=user_data['verified']
    connection=getConnectionWithDB()
    if connection == 'Connection Failed':
        return False
    else:
        cursor=connection.cursor()
        if query_filter=='id':
            query="update users set is_verified=%s where id=%s"
            values=(verified,id)
        elif query_filter=='email':
            query="update users set is_verified=%s where email=%s"
            values=(verified,email)
        cursor.execute(query,values)
        connection.commit()
        cursor.close()
        connection.close()
        return True
                
# user_data={'email':'sai123@gmail.com','verified':True}
# print(updateVerifiedByIdorEmail(user_data))

def generateOTP():
    otp=random.randint(1000,9999)
    return otp
# print(generateOTP())
# ylob fhec ssle gtsx
def sendOTPviaEmail(to_email,otp):
    message=EmailMessage()
    message['Subject']='otp notification'
    message['from']=from_email
    message['to']=to_email
    message.set_content(
        f"your otp is {otp}"
    )
    with smtplib.SMTP("smtp.gmail.com",587) as server:
        server.starttls()
        server.login(from_email,email_app_password)
        server.send_message(message)
    return True

# print(sendOTPviaEmail('knsknsk10@gmail.com'))

def sendEmail(to_email,subject,body):
    message=EmailMessage()
    message['Subject']=subject
    message['from']=from_email
    message['to']=to_email
    message.set_content(body)
    with smtplib.SMTP("smtp.gmail.com",587) as server:
        server.starttls()
        server.login(from_email,email_app_password)
        server.send_message(message)
    return True

def validateData(user_data):
    errors=[]
    name=user_data['name']
    email=user_data['email']
    password=user_data['password']
    confirm_password=user_data['confirm_password']
    if ( name is None) or (len(name)<2):
        errors.append("invalid name")
    if email is None or len(email)<5:
        errors.append("invalid email")
    if password is None or len(password)<5:
        errors.append("invalid Password")
    if password != confirm_password:
        errors.append("password mismatch")
    return errors
# print(validateData({'name':'nsk','email':'gfdtfgk','password':'','confirm_password':''}))

def verifyDuplicateEmail(user_data):
    # email=user_data['email']
    record=readUserRecordByEmail(user_data)
    if(record=="no records found"):
        return False
    else:
        return True

serializer=URLSafeTimedSerializer(app.secret_key)
def resetPasswordTokenGenerate(email):
    token=serializer.dumps(email,salt='reset_password')
    return token

def validateToken(token):
    try:
        data=serializer.loads(token,salt='reset_password',max_age=600)
        return data
    except BadSignature:
        return "invalid"
    except TimedSerializer:
        return "timeout"

def getNotesByUserId(user_id,filename=None):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database connection Failed"
        else:
            cursor = connection.cursor(dictionary=True)
            query = "select * from notes where user_id=%s"
            values = [user_id]
            if filename:
                query +=" and title LIKE %s;"
                values.append("%" + filename + "%")
            print(f"Executing query: {query} with values: {values}")
            cursor.execute(query,tuple(values))
            notes = cursor.fetchall()
            connection.commit()
            cursor.close()
            connection.close()
            return True,notes
    except Exception as e:
        return False,f'Exception raised in add notes:{e}' 
    
# print(getNotesByUserId(16))

def getFilesAndNotesCount(user_id):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor()
            get_notes_count = """SELECT COUNT(*) FROM NOTES 
                             WHERE USER_ID = %s;"""
            cursor.execute(get_notes_count,(user_id,))
            notes_count=cursor.fetchone()[0]
            get_files_count="""select count(*) from file_data
                            where user_id=%s;"""
            cursor.execute(get_files_count,(user_id,))
            files_count = cursor.fetchone()[0]
            cursor.close()
            connection.close()
            return notes_count,files_count
    except Exception as e:
        return False,f'Exception raised in count:{e}'
def recentNotes(user_id):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor= connection.cursor(dictionary=True)
            get_recent_notes = """SELECT * FROM NOTES
                              WHERE USER_ID=%s ORDER BY updated_at
                              DESC LIMIT 3;"""
            cursor.execute(get_recent_notes,(user_id,))
            recent_notes = cursor.fetchall()
            cursor.close()
            connection.close()
            return True,recent_notes
    except Exception as e:
        return False,f"Exception raised in recent notes:{e}"
    

@app.route('/')
def home():
    # return "flask is running"
    return render_template('index.html')

@app.route('/register/',methods=['GET','POST'])
def register():
    global OTP
    if(request.method=="GET"):
        return render_template('register.html')
    elif(request.method=="POST"):
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        confirm_password=request.form['confirm_password']
        user_data={
            'name':name,
            'email':email,
            'password':password,
            'confirm_password':confirm_password
        }
        errors=validateData(user_data)
        if(len(errors)>0):
            return render_template('register.html',errors=errors)
        else:
            is_duplicate=verifyDuplicateEmail(email)
            if is_duplicate==False:
                #OTP=generateOTP()
                session['OTP']=generateOTP()
                password_hash=generateHash(user_data['password'])
                name=user_data['name']
                email=user_data['email']
                status=insertUserRecord({
                    'name':name,'email':email,'password_hash':password_hash
                })
                if status==True:
                    session['username']=email
                    OTP=session['OTP']
                    #sendOTPviaEmail(email,OTP)
                    sendEmail(subject=' verify your registration-notes managment,,otp notification',to_email=email,body=emailTemplates.send_otp_template(otp=OTP,username=name))
                    return redirect(url_for('verify'))
                    # return render_template('register.html',res='registration successful')
                else:
                    return render_template('register.html',err='registration failed')
            else:
                return render_template('register.html',err='account already exists')
    

@app.route('/login/',methods=['GET','POST'])
def login():
    if(request.method=="GET"):
        return render_template('login.html')
    elif(request.method=="POST"):
        email=request.form['email']
        password=request.form['password']
        record=readUserRecordByEmail(email)
        if(record=="no records found"):
            return render_template('login.html',err='account does not exist')
        elif(record['isverified']==False):
            return render_template('login.html',err='account is not verified')
        else:
            password_hash=record['password']
            if bcrypt.checkpw(password.encode('utf-8'),password_hash.encode('utf-8')):
                session['username']=email
                session['id'] = record['id']
                session['name'] = record['name']
                return redirect(url_for('dashboard'))
            
            else:
                return render_template('login.html',err='invalid password')
    #password=request.form['password']
    return render_template('login.html')

@app.route('/verify/',methods=['GET','POST'])
def verify():
    if(request.method=="GET"):
        return render_template('verify.html')
    elif(request.method=="POST"):
        otp=request.form['otp']
        otp=int(otp)
        # verify the otp with the one sent to the email
        # if otp is correct, update the is_verified field in the database
        # else, return an error message
        if otp==session['OTP']:
            is_verify=True
            updateVerifiedByIdorEmail({'email':session['username'],'verified':is_verify})
            return redirect(url_for('login'))
        else:
            return render_template('verify.html',err='invalid otp')
        # if(record=="no records found"):
        #     return render_template('verify.html',err='account does not exist')
        # else:
        #     if(otp==record['otp']):
        #         updateVerifiedByIdorEmail({'email':email,'verified':True})
        #         return render_template('verify.html',res='account verified successfully')
        #     else:
        #         return render_template('verify.html',err='invalid otp')
@app.route('/dashboard')
def dashboard():
    #if the user data is not in the session redirect to login page
    if "id" not in session:
        return redirect("/login")
    userid = session['id']
    notes_count,files_count = getFilesAndNotesCount(userid)
    _,recent_notes = recentNotes(userid)
    print(recent_notes)
    return render_template('dashboard.html',
                           username= session['name'],total_notes = notes_count,
                           total_files=files_count,notes=recent_notes)

# @app.route('/notes/')
# def notes():
#     return render_template('notes.html')

@app.route('/user/profile/',methods=['GET'])
def profile():
    if 'id' not in session:
        return redirect('/login/')
    name=session['name']
    email=session['username']
    return render_template('profile.html',name=name,email=email)

@app.route('/notes/',methods=['GET','POST'])
def mynotes():
    if "id" not in session:
        return redirect('/login/')
    if request.method == "GET":
        #get user notes from the database
        status,notes = getNotesByUserId(user_id=session['id'])
        print(notes)
        if status == True:
            return render_template("notes.html",notes = notes)
        else:
            return render_template('notes.html',err=notes)
    if request.method == "POST":
        notes_name = request.form.get('searchnotes','').strip()
        status,notes = getNotesByUserId(
            user_id=session['id'],
            filename=notes_name
        )
        if status == True:
            return render_template('notes.html',notes=notes)
        else:
            return render_template('notes.html',err=notes)

#logout route
@app.route("/logout/",methods=['GET'])
def logout():
    #if id in session
    session.pop('id',None)
    session.pop('name',None)
    session.pop('email',None)
    return redirect('/login/')

@app.route('/forgot_password/',methods=['GET','POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')
    elif request.method == 'POST':
        email = request.form['email']
        record = readUserRecordByEmail(email)
        if 'id' in record:
            token = resetPasswordTokenGenerate(email)
            reset_link = url_for('reset_password', token=token, _external=True)
            email_status = sendEmail(subject='Reset your password', to_email=email, body=emailTemplates.reset_password_template(username=record['name'],reset_link=reset_link,time=10))
            if email_status:
                return render_template('forgot_password.html', res='Password reset link sent to your email.')
            else:
                return render_template('forgot_password.html', err='Failed to send email. Please try again later.')
        else:
            return render_template('forgot_password.html', err='Account does not exist.')

@app.route('/reset_password/<string:token>/', methods=['GET', 'POST'])
def reset_password(token):
    email = validateToken(token)
    if email == "invalid":
        return render_template('forgot_password.html', err='Invalid token.')
    elif email == "timeout":
        return render_template('forgot_password.html', err='Token has expired. Please request a new password reset link.')
    
    if request.method == 'GET':
        return render_template('reset_password.html', email=email, token=token)
    elif request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        print(f"New password: {new_password}, Confirm password: {confirm_password}, Email: {email}")
        if new_password != confirm_password:
            return render_template('reset_password.html', err='Passwords do not match.',email=email, token=token)
        
        password_hash = generateHash(new_password)
        update_status = updatePasswordByIdorEmail({'email': email, 'new_password': password_hash})
        print(f"Password update status for {email}: {update_status}")
        if update_status:
            return redirect('/login/')
        else:
            return render_template('reset_password.html', err='Failed to reset password. Please try again later.', email=email, token=token)

#insert notes records in table
def addNotesRecord(user_id:int,title:str,content:str):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor()
            add_notes_query = """INSERT INTO NOTES(user_id,
            title,content) values(%s,%s,%s);"""
            cursor.execute(add_notes_query,(user_id,
                                            title,content))
            connection.commit()
            cursor.close()
            connection.close()
            return True,"Notes Saved"
    except Exception as e:
        return False,f'Exception raised in add notes:{e}'
    
#add notes route
@app.route('/notes/addnotes',methods=['GET','POST'])
def add_notes():
    if "id" not in session:
        return redirect('/login')
    #GET request
    if request.method == "GET":
        return render_template('addnotes.html')
    #POST request
    if request.method == "POST":
        title = request.form.get('Title',"No Title")
        content = request.form.get('content',"No Content")
        #store in database
        id=session['id']
        status,msg = addNotesRecord(
            user_id = session['id'],
            title = title,
            content=content
        )
        _,notes = getNotesByUserId(user_id=id)
        if status == True:
            #redirect to notes dashboard
            return render_template('notes.html',notes=notes,msg=msg)
        else:
            return render_template('notes.html',err=msg)

#get notes by id
def getNotesById(notes_id):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor(dictionary=True)
            get_notes_by_id = """select title,content from notes
            where id=%s;"""
            cursor.execute(get_notes_by_id,(notes_id,))
            notes = cursor.fetchone()
            cursor.close()
            connection.close()
            return True,notes
    except Exception as e:
        return False,f'Exception raised in View Notes:{e}'

# print(getNotesById(1))
#view notes route
@app.route('/notes/view/<int:note_id>')
def view_notes(note_id):
    #get notes from thedatabase based on notesid
    status,notes = getNotesById(notes_id=note_id)
    if status == True:
        title = notes['title']
        content = notes['content']
        return render_template('viewnotes.html',title=title,content=content)
    else:
        return render_template('notes.html',err=notes)
#update notes by id
def updateNotesByID(notes_id:int,title:str,content:str):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor= connection.cursor()
            update_notes_by_id = """update notes 
            set title=%s,content=%s where id=%s;"""
            cursor.execute(update_notes_by_id,(title,
                                               content,notes_id))
            connection.commit()
            cursor.close()
            connection.close()
            return True,"Notes Updated"
    except Exception as e:
        return False,f"Exception raised in update notes:{e}"
#edit notes route
@app.route('/notes/edit/<int:note_id>',methods=['GET','POST'])
def edit_notes(note_id):
    #get notes from the database
    if request.method == "GET":
        status,notes=getNotesById(notes_id=note_id)
        if status == True:
            return render_template('updatenotes.html',
                                   title=notes['title'],
                                   content=notes['content'],
                                   notes_id=note_id)
        else:
            return render_template('notes.html',err=notes)
    #post request
    if request.method == "POST":
        title = request.form.get('title')
        content = request.form.get('content')
        print(title,content)
        #update notes content in database as per notes id
        status,msg = updateNotesByID(
            title=title,content=content,notes_id=note_id)
        _,notes = getNotesByUserId(user_id=session['id'])
        if status == True:
            return render_template('notes.html',msg=msg,
                                   notes=notes)
        else:
            return render_template('notes.html',err=msg,
                                   notes=notes)

#delete notes by id
def deleteNotesById(notes_id):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor()
            delete_notes_by_id = """delete from notes
            where id=%s;"""
            cursor.execute(delete_notes_by_id,(notes_id,))
            connection.commit()
            cursor.close()
            connection.close()
            return True,"Notes Deleted"
    except Exception as e:
        return False,f'Exception raised in delete notes:{e}'

#delete notes route
@app.route('/notes/delete/<int:note_id>',methods=['GET','POST'])
def delete_notes(note_id):
    #delete notes from database based on the note_id
    status,msg = deleteNotesById(notes_id=note_id)
    _,notes = getNotesByUserId(user_id=session['id'])
    if status==True:
        return render_template('notes.html',msg=msg,
                               notes=notes)
    else:
        return render_template('notes.html',err=msg,
                               notes=notes)

def getFilesById(user_id,filename=None):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM file_data WHERE user_id = %s"
            values = [user_id]
            if filename:
                query += " AND stored_name LIKE %s"
                values.append("%" + filename + "%")
            #get_file_by_userid = """select * from file_data
            #where user_id=%s;"""
            #cursor.execute(get_file_by_userid,(userid,))
            cursor.execute(query, tuple(values))
            files = cursor.fetchall()
            connection.commit()
            cursor.close()
            connection.close()
            return True,files
    except Exception as e:
        return False,f'Exception raised in Search Files:{e}'



@app.route('/files/',methods=['GET','POST'])
def myfiles():
    # 1. Check whether the user is logged in
    if "id" not in session:
        return redirect('/login/')
    if request.method == "GET":
        # 2. Get logged-in user's ID
        user_id = session['id']
        print("Logged-in User ID:", user_id)

        # 3. Fetch files belonging to this user
        status, files = getFilesById(user_id)

        print("Files:", files)

        # 4. Check database result
        if status:
            return render_template(
                'files.html',
                files=files
            )
        else:
            return render_template(
                'files.html',
                err=files,
                files=[]
            )
    if request.method == "POST":
        filename = request.form.get('searchfiles', '').strip()
        status, files = getFilesById(
            user_id=session['id'],
            filename=filename
        )
        if status == True:
            return render_template('files.html', files=files)
        else:
            flash(files, "err")
            return render_template('files.html')

def checkFileAllowed(filename):
    allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'mp3', 'mp4', 'avi', 'mkv','zip', 'rar', '7z','py'}

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def checkFileDuplicate(userid,filename):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor(dictionary=True)
            check_file_duplicate_query = """SELECT * FROM FILE_DATA WHERE
            USER_ID = %s AND STORED_NAME = %s;"""
            cursor.execute(check_file_duplicate_query,(userid,filename))
            file_record = cursor.fetchone()
            connection.commit()
            cursor.close()
            connection.close()
            if file_record:
                return False,f'File with name {filename} already exists for user {userid}'
            else:
                return True,f'No duplicate file found for user {userid} with name {filename}'
    except Exception as e:
        return False,f'Exception raised in check file duplicate:{e}'
    # Implement logic to check if the file already exists in the database for the user
    # For demonstration, we'll just return False (no duplicate)
    
def UploadFileInDB(userid,filename,stored_name,file_size,file_type,path):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor()
            upload_file_query = """INSERT INTO FILE_DATA(USER_ID,
            ORIGINAL_NAME,STORED_NAME,size_bytes,mime_type,storage_path) values(%s,%s,%s,%s,%s,%s)"""
            cursor.execute(upload_file_query,(userid,
                                            filename,stored_name,file_size,file_type,path))
            connection.commit()
            cursor.close()
            connection.close()
            return True,"File Uploaded"
    except Exception as e:
        return False,f'Exception raised in Upload File:{e}'

def getFileByFileId(file_id):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor(dictionary=True)
            get_file_by_id_query = """SELECT * FROM FILE_DATA WHERE
            ID = %s;"""
            cursor.execute(get_file_by_id_query,(file_id,))
            file_record = cursor.fetchone()
            connection.commit()
            cursor.close()
            connection.close()
            if file_record:
                return True,file_record
            else:
                return False,f'No file found with ID {file_id}'
    except Exception as e:
        return False,f'Exception raised in get file by id:{e}'

@app.route('/files/upload',methods=['GET','POST'])
def upload_file():
    if "id" not in session:
        return redirect('/login/')
    if request.method == "GET":
        return render_template('uploadfile.html')
    elif request.method == "POST":
        file = request.files['file']
        print(f"Received file: {file}")
        if file and file.filename == '' or file is None:
            return render_template('uploadfile.html', err='No file selected.')
        # Save the file to the server or database
        # For demonstration, we'll just print the filename
        # print(f"Received file: {file.filename}")
        file_name = file.filename
        if not checkFileAllowed(file_name):
            return render_template('uploadfile.html', err='File type not allowed.')
        file_name_secure = secure_filename(file_name)
        
        if not checkFileDuplicate(userid=session['id'],filename=file_name_secure)[0]:
            flash(f'File with name {file_name} already exists.')
            return redirect('/files/upload')
        
        # Create upload folder inside the project
        upload_folder = os.path.join(app.root_path, 'upload')
        os.makedirs(upload_folder, exist_ok=True)

        # Complete file path
        file_path = os.path.join(upload_folder, file_name_secure)

        # Save file
        file.save(file_path)

        # Get file details
        file_size = os.path.getsize(file_path)
        file_type = os.path.splitext(file_name_secure)[1].lower()  # Get file extension as type
        print(f"File saved: {file_name_secure}, Size: {file_size} bytes")
        # Implement logic to save file information to the database
        status,msg = UploadFileInDB(userid=session['id'],filename=file_name,stored_name=file_name_secure,file_size=file_size,file_type=file_type,path=f'upload/{file_name_secure}')
        _,file_record=getFilesById(session['id'])
        if status == True:
            return render_template('files.html', res=msg,files=file_record)  
        else:
            flash(msg)
            return redirect('/files/upload')
        

#get file metadata by file id
def getFileByFileId(fileid):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor(dictionary=True)
            get_file_by_userid = """select * from file_data
                                where id = %s;"""
            cursor.execute(get_file_by_userid,(fileid,))
            file=cursor.fetchone()
            cursor.close()
            connection.close()
            return True,file
    except Exception as e:
        return False,f'Exception rasied in View File:{e}'


import mimetypes

@app.route('/files/view/<int:file_id>')
def view_file(file_id):
    if "id" not in session:
        return redirect('/login/')
    # Implement the logic to retrieve the file from the database or server based on file_id
    # For demonstration, we'll just return a placeholder response
    if request.method == "GET":
        #get the file by file_id
        status,file = getFileByFileId(fileid=file_id)
        if status == True:
            secure_filename = file['stored_name']
            mime_type,_ = mimetypes.guess_type(secure_filename)
            return send_file(
                f'upload/{secure_filename}',
                mimetype=mime_type,
                as_attachment=False
            )
        else:
            flash(file,'err')
            return redirect('/files')

@app.route('/files/download/<int:file_id>')
def download_file(file_id):
    if "id" not in session:
        return redirect('/login/')
    # Implement the logic to retrieve the file from the database or server based on file_id
    # For demonstration, we'll just return a placeholder response
    if request.method == "GET":
        #get file by file_id
        status,file = getFileByFileId(fileid=file_id)
        if status == True:
            secure_filename = file['stored_name']
            mime_type, _ = mimetypes.guess_type(
                secure_filename)
            return send_file(
                f'upload/{secure_filename}',
                mimetype=mime_type,
                as_attachment=True
            )
        else:
            flash(file,"err")
            return redirect('/files')

def deleteFileByFileId(fileid):
    try:
        connection = getConnectionWithDB()
        if connection == "Connection Failed":
            return False,"Database Connection Failed"
        else:
            cursor = connection.cursor()
            delete_file_by_userid = """delete from file_data
                                where id = %s;"""
            cursor.execute(delete_file_by_userid,(fileid,))
            connection.commit()
            cursor.close()
            connection.close()
            return True,"File Deleted Successfully"
    except Exception as e:
        return False,f'Exception raised in View File:{e}'


@app.route('/files/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    if "id" not in session:
        return redirect('/login/')
    # Implement the logic to delete the file from the database or server based on file_id
    # For demonstration, we'll just return a placeholder response
    if request.method == "GET":
            #get file by file_id
            status,msg = deleteFileByFileId(fileid=file_id)
            if status == True:
                flash(msg,"msg")
                return redirect('/files')
            else:
                flash(msg,"err")
                return redirect('/files')

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5001,debug=True)    











