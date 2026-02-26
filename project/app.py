from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from flask import jsonify
#Important notes if conflused
# app.route is the way to webpages which i put in templates folder as flask only reads templates (got an error so changed it to templates)
#so far add is a work in progress show is there and search too will try booking soon
#seats are generated now when we put numberSeats they are asigned to the flight id so that there is no overlapping seats on differnt flights
#
app = Flask(__name__)

def getDbConnection():
    conn = sqlite3.connect("AirPlaneSystem.db")
    conn.row_factory = sqlite3.Row
    return conn


# Home Page
@app.route("/")
def home():
    return render_template("home.html")


# Show All Flights
@app.route("/showFlights")
def showFlights():
    conn = getDbConnection()
    flights = conn.execute("SELECT * FROM Flight").fetchall()
    conn.close()
    return render_template("showFlights.html", flights=flights)


# Add Flight (Admin later)
@app.route("/addFlight", methods=["GET", "POST"])
def addFlight():
    if request.method == "POST":
        departure = request.form["departure"]
        destination = request.form["destination"]
        departureDate = request.form["departureDate"]
        departureTime = request.form["departureTime"]
        arrivalDate = request.form["arrivalDate"]
        arrivalTime = request.form["arrivalTime"]
        numberSeats = request.form["numberSeats"]

        conn = getDbConnection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Flight 
            (departure, destination, departureDate, departureTime, arrivalDate, arrivalTime, numberSeats)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (departure, destination, departureDate, departureTime, arrivalDate, arrivalTime, numberSeats))

        flight_id = cur.lastrowid
        #for loop to make seats based on how many seats in flight
        for i in range(1, int(numberSeats) + 1):
            seat_number = f"S{i}"
            seat_cost = 100  # temp number we can change as we go on

            cur.execute("""
            INSERT INTO Seat (seatNumber, seatCost, bookingID, flightNumber)
                VALUES (?, ?, NULL, ?)
            """, (seat_number, seat_cost, flight_id))

        conn.commit()
        conn.close()

        return redirect(url_for("showFlights"))

    return render_template("addFlight.html")


# Search Flights
@app.route("/searchFlights", methods=["GET", "POST"])
def searchFlights():
    flights = []
    if request.method == "POST":
        departure = request.form["departure"]
        destination = request.form["destination"]

        conn = getDbConnection()
        flights = conn.execute("""
            SELECT * FROM Flight
            WHERE departure = ? AND destination = ?
        """, (departure, destination)).fetchall()
        conn.close()

    return render_template("searchFlights.html", flights=flights)

#edit flight
@app.route("/editFlight/<int:flightID>", methods=["GET", "POST"])
def editFlight(flightID):
    conn = getDbConnection()
    f = conn.execute("SELECT * FROM Flight WHERE flightNumber =?", (flightID,)).fetchone()
    if f is None:
        conn.close()
        return """
<script>
    alert('Flight ID does not exist');
    window.history.back();
</script>
"""


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
        return redirect(f"/showFlights")

    # GET REQUEST FOR THE FORM
    flight = conn.execute("SELECT * FROM Flight WHERE flightNumber =?", (flightID,)).fetchone()
    conn.close()
    return render_template("editFlight.html", flight=flight)

#delete flight
@app.route("/deleteFlight/<int:flightID>", methods = ["POST"])
def removeFlight(flightID):
    conn = getDbConnection()
    f = conn.execute("SELECT * FROM Flight WHERE flightNumber =?", (flightID,)).fetchone()
    if f is None:
        conn.close()
        return
    else:
        conn.execute("""Delete FROM Flight
                     WHERE flightNumber = ?""", (flightID,))
        conn.commit()
        conn.close()
        return redirect(f"/showFlights")

#################################################
#Booking
#################################################

#add booking
@app.route("/addBooking", methods=["GET", "POST"])
def addBooking():
    if request.method == "POST":
        flightID = request.form["flightID"]
        passengerName = request.form["passengerName"]
        passengerEmail = request.form["passengerEmail"]
        conn = getDbConnection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Booking 
            (flightID, passengerName, passengerEmail)
            VALUES (?, ?, ?)
        """, (flightID, passengerName, passengerEmail))
        conn.commit()
        conn.close()
        return redirect("/showBooking")

    return render_template("addBooking.html")

#show booking
@app.route("/showBooking/<int:bookingID>", methods = ["GET"])
def showBooking(bookingID):
    conn = getDbConnection()
    booking = conn.execute("""SELECT * WHERE bookingID = ?""", (bookingID,))
    conn.close()
    return render_template("showBooking.html", booking = booking)

#edit booking
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
        return redirect(f"/showBooking/{bookingID}")

    # GET REQUEST FOR THE FORM
    booking = conn.execute("SELECT * FROM Booking WHERE bookingID =?", (bookingID,)).fetchone()
    conn.close()
    return render_template("editBooking.html", booking=booking)   

#delete booking
@app.route("/deleteBooking/<int:bookingID>", methods = ["POST"])
def deleteBooking(bookingID):
    conn = getDbConnection()
    f = conn.execute("SELECT * FROM Booking WHERE bookingID =?", (bookingID,)).fetchone()
    if f is None:
        conn.close()
        return
    else:
        conn.execute("""Delete FROM Booking
                     WHERE bookingID = ?""", (bookingID,))
        conn.commit()
        conn.close()
        return render_template("home.html")

#############################################################
#Airline
#############################################################
#add airline
@app.route("/addAirline", methods=["GET", "POST"])
def addAirline():
    if request.method == "POST":
        airlineName = request.form["airlineName"]
        airlineAddress = request.form["airlineAddress"]
        conn = getDbConnection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Airline 
            (airlineName, airlineAddress)
            VALUES (?, ?)
        """, (airlineName, airlineAddress))
        conn.commit()
        conn.close()
        return redirect("/showAirline")
    return render_template("addAirline.html")

#show airline
@app.route("/showAirline/<int:airlineID>", methods = ["GET"])
def showAirline(airlineID):
    conn = getDbConnection()
    booking = conn.execute("""SELECT * FROM Airline WHERE airlineID = ?""", (airlineID,))
    conn.close()
    return render_template("showAirline.html", booking = booking)

#edit airline
@app.route("/editBooking/<int:bookingID>", methods=["GET", "POST"])
def editAirline(airlineID):
    conn = getDbConnection()

    if request.method == "POST":
        airlineName = request.form["Airline Name"]
        airlineAddress = request.form["Airline Address"]
        conn.execute("""UPDATE Booking
                     SET airlineName = ?, airlineAddress = ?, WHERE airlineID = ?""", (airlineName, airlineAddress))
        conn.commit()
        conn.close()
        return redirect(f"/showAirline/{airlineID}")

    # GET REQUEST FOR THE FORM
    booking = conn.execute("SELECT * FROM Booking WHERE bookingID =?", (airlineID,)).fetchone()
    conn.close()
    return render_template("editBooking.html", booking=booking)   

if __name__ == "__main__":
    app.run(debug=True)