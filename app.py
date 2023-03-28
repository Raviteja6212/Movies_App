import base64
import csv
import datetime
import os
from flask import Flask, jsonify,  render_template, request, redirect, url_for
from jinja2 import Template
import sqlite3

app = Flask(__name__)

import jwt

# Define a secret key to sign the token
app.secret_key = 'my_secret_key'

# Define a function to generate a JWT token
def generate_token(user_id):
    payload = {
        'user_id': user_id
    }
    token = jwt.encode(payload, app.secret_key, algorithm='HS256')  
    return token


@app.route("/",methods=["GET","POST"])
def index(message=""):
    if request.method=="POST":
        username = request.form.getlist('username')[0]
        password = request.form.getlist('password')[0]
        try:
            sqliteConnection = sqlite3.connect('database.db')
            cursor = sqliteConnection.cursor()
            sqlite_select_Query = "select * from users_data;"
            cursor.execute(sqlite_select_Query)
            record = cursor.fetchall()
            venues_query = "select * from venues;"
            cursor.execute(venues_query)
            venues = cursor.fetchall()
            shows_query = "select * from shows;"
            cursor.execute(shows_query)
            shows = cursor.fetchall()
            venue_shows = {}
            for i in shows:
                if i[2] in venue_shows.keys():
                    venue_shows[i[2]]["shows"].append(i)
                else:
                    for j in venues:
                        if j[0]==i[2]:
                            venue_shows[i[2]]={}
                            venue_shows[i[2]]["venue"]=j
                            venue_shows[i[2]]["shows"]=[]
                            venue_shows[i[2]]["shows"].append(i)
                    
            cursor.close()

        except sqlite3.Error as err:
            print("Error while connecting to sqlite", err)
        
        print("venue shows are as follows")
        print(venue_shows)
        for i in record:
            if i[1]==username and i[2]==password:
                token = generate_token(i[0])
                return render_template("homepage.html",user_id=i[0],username=username,venuelist=venue_shows,token=jsonify({'token': token}))
        return render_template("errorpage.html")
    else:
        try:
            logout=request.args.get('logout')
            return render_template("index.html",logout=logout)
        except Exception as e:
            return render_template("index.html",logout=None)

@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="GET":
        return render_template("singupPage.html")
    else:
        username = request.form.getlist('username')[0]
        password = request.form.getlist('password')[0]
        try:
            sqliteConnection = sqlite3.connect('database.db')
            cursor = sqliteConnection.cursor()
            sqlite_select_Query = "select * from users_data;"
            cursor.execute(sqlite_select_Query)
            record = cursor.fetchall()
            admincode = request.form['admincode']

        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)
        
        for i in record:
            if i[1]==username:
                return render_template("singupPage.html",error="Username already exists !!")
        
        Insert_Query = "INSERT INTO users_data (username,password) VALUES (?,?)"
        cursor.execute(Insert_Query,(username,password))
        sqliteConnection.commit()
        cursor.close()
        
        return redirect(url_for('index',error="User created successfully, you can login now:)Y"))


@app.route("/showDetails",methods=["GET","POST"])
def ViewShow():
    if request.method=="POST":
        #user_id=request.form['user_id']
        show_id = request.args.get("show_id")
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        shows_query = "select * from shows;"
        cursor.execute(shows_query)
        shows = cursor.fetchall()
        venues_query = "select * from venues;"
        cursor.execute(venues_query)
        venues = cursor.fetchall()
        # code for already booked seats.
        # user_shows_query = "select * from user_shows;"
        # cursor.execute(user_shows_query)
        # user_shows = cursor.fetchall()
        # alreadyBooked=0
        # for i in user_shows:
        #     if i[1]==int(user_id) and i[2]==show_id:
        #         alreadyBooked+=i[3]
        for i in shows:
            if int(show_id)==i[0]: 
                for j in venues:
                    if j[0]==i[2]: # this show can be in many venues, checking the venue.
                        try:
                            tickets = int(request.form['tickets'])
                            if tickets>0 and tickets<i[8]:
                                return render_template("showdetails.html",showdata=i,venuedata=j,totalPrice=tickets*i[4],tickets=tickets)
                        except Exception as e:
                            return render_template("showdetails.html",showdata=i,venuedata=j,totalPrice="")
        
                
        return render_template("errorpage.html")
    else:
        show_id=request.args.get('show_id')
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        shows_query = "select * from shows;"
        cursor.execute(shows_query)
        shows = cursor.fetchall()
        venues_query = "select * from venues;"
        cursor.execute(venues_query)
        venues = cursor.fetchall()
        for i in shows:
            if int(show_id)==i[0]:     
                for j in venues:
                    if j[0]==i[2]:
                        return render_template("showdetails.html",showdata=i,venuedata=j,totalPrice="")
        return render_template("errorpage.html")

@app.route("/confirmBooking",methods=["GET","POST"])
def confirm():
    if request.method=="POST":
        print("Entered confirm booking")
        show_id = request.form['show_id']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        shows_query = "select * from shows;"
        cursor.execute(shows_query)
        shows = cursor.fetchall()
        venues_query = "select * from venues;"
        cursor.execute(venues_query)
        venues = cursor.fetchall()
        for i in shows:
            if int(show_id)==i[0]:     
                for j in venues:
                    if j[0]==i[2]:
                        try: 
                            print("Entered try booking")  
                            tickets = int(request.form['confirmtickets']) 
                            confirm=request.form['confirm']
                            if confirm=="Click To Confirm Tickets!":
                                user_id = request.form.get('user_id')                              
                                print("Entered the cofimr booking and about to update and user id - ")
                                cursor.execute('''UPDATE shows SET capacity = ? WHERE id = ?''', (i[8]-tickets, show_id))
                                conn.commit()
                                cursor.execute("INSERT INTO user_shows (user_id, show_id, tickets) VALUES (?, ?, ?)",(user_id,show_id,tickets))
                                conn.commit()
                                return redirect(url_for('ViewShow',show_id=show_id))
                        except Exception as e:
                            return redirect(url_for('ViewShow',show_id=show_id))
                            
        return render_template("errorpage.html")  
    
@app.route("/mybookings",methods=["GET","POST"])
def MyBookings():
        user_id=request.args.get('user_id')
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        user_shows_query = "select * from user_shows;"
        cursor.execute(user_shows_query)
        user_shows = cursor.fetchall()
        shows_query = "select * from shows;"
        cursor.execute(shows_query)
        shows = cursor.fetchall()
        this_user_shows_ids=[]
        this_user_shows=[]
        this_user_shows_details=[]
        shows_tickets={}
        for i in user_shows:
            if i[1]==int(user_id):
                if i[2] not in shows_tickets:
                    shows_tickets[i[2]]=i[3]
                else:
                    shows_tickets[i[2]]+=i[3]
                this_user_shows_ids.append(int(i[2]))
            
        for i in shows:
            if i[0] in this_user_shows_ids:
                this_user_shows.append(i)
                       
        return render_template('bookingspage.html',this_user_shows=this_user_shows,shows_tickets=shows_tickets)
                
@app.route("/myprofile",methods=["GET","POST"])
def MyProfile():
    user_id=request.args.get('user_id')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    user_shows_query = "select * from user_shows;"
    cursor.execute(user_shows_query)
    user_shows = cursor.fetchall()
    no_of_shows=0
    for i in user_shows:
        if i[1]==int(user_id):
            no_of_shows+=1
    return render_template("profilepage.html",no_of_shows=no_of_shows)

if __name__=="__main__":
    app.run(debug=True)
    