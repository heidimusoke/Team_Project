from flask import Flask, render_template, request, redirect
import sqlite3
from flask import jsonify

app = Flask(__name__)  



def getDbConnection():
    conn = sqlite3.connect("AirPlaneSystem.db")
    conn.row_factory = sqlite3.Row
    return conn
####################################################
#Flight
#################################################
@app.route("/showFlight/<int:flightID>", methods = ["GET"])
def showFlights(flightID):
    conn = getDbConnection()
    flight= conn.execute("Select * from Flight WHERE flightNumber = ?", (flightID,)).fetchone()
    conn.close()
    return render_template("showFlight.html", flight= flight)


@app.route("/editFlight/<int:flightID>", methods=["GET", "POST"])
def editFlight(flightID):
    conn = getDbConnection()

    if request.method == "POST":
        dept = request.form["Departure"]
        dest = request.form["Destination"]
        deptDate = request.form["Departure Date"]
        deptTime = request.form["Departure Time"]
        arrDate = request.form["Arrival Date"]
        arrTime = request.form["Arrival Time"]
        numSeats = request.form["Number of seats"]
        airlineID = request.form["Airline ID"]

        conn.execute("""UPDATE Flight
                     SET departure = ?, destination = ?, departureDate = ?, departureTime = ?, arrivalDate = ?, arrivalTime = ?, numberSeats =?, airlineID = ?  WHERE flightNumber = ?""", (dept, dest, deptDate, deptTime, arrDate, arrTime, numSeats, airlineID, flightID))
        conn.commit()
        conn.close()
        return redirect("/showFlight/{flightID}")
       


        # GET REQUEST FOR THE FORM
    flight = conn.execute("SELECT * FROM Flight WHERE flightNumber =?", (flightID,)).fetchone()
    conn.close()
    return render_template("editFlight.html", flight=flight)        



@app.route("/addFlight")
def addFlight():
    conn=getDbConnection()
    conn.close()

@app.route("/deleteFlight/<int:flightID>", methods = ["POST"])
def removeFlight(flightID):
    conn = getDbConnection()
    conn.close()

#################################################
#Booking
#################################################
@app.route("/addBooking")
def addBooking():
    conn=getDbConnection()
    conn.close()

@app.route("/showBooking/<int:bookingID>", methods = ["GET"])
def showBooking(bookingID):
    conn = getDbConnection()
    booking = conn.execute("Select * from Booking WHERE BookingID = ?", (bookingID,)).fetchone()
    conn.close()
    return render_template("showBooking.html", booking = booking)

@app.route("/editBooking/<int:bookingID>", methods=["GET", "POST"])
def editBooking(bookingID):
    conn = getDbConnection()

    if request.method == "POST":
        cardName = request.form["Credit Card Name"]
        cardNum = request.form["Credit Card Number"]
        cardCVV = request.form["CVV"]
        cardExpiry = request.form["Expiry"]

        conn.execute("""UPDATE Booking
                     SET creditCardName = ?, creditCardNumber = ?, creditCardCvv = ?, creditCardExpiry = ? WHERE bookingID = ?""", (cardName, cardNum, cardCVV, cardExpiry))
        conn.commit()
        conn.close()
        return redirect("/showBooking/{bookingID}")

    # GET REQUEST FOR THE FORM
    booking = conn.execute("SELECT * FROM Booking WHERE bookingID =?", (bookingID,)).fetchone()
    conn.close()
    return render_template("editBooking.html", booking=booking)   

@app.route("/deleteBooking/<int:bookingID>", methods = ["POST"])
def removeFlight(bookingID):
    conn = getDbConnection()
    conn.close()

#This must be at end of file
if __name__ == "__main__":
    app.run(debug=True)

#############################################
#Airline
#############################################
