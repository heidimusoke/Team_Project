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


# Customer Home Page
@app.route("/")
def userHome():
        return render_template("userHome.html")

# Admin Home Page
@app.route("/admin")
def home():
    return render_template("home.html")

@app.route("/adminLogin", methods = ["GET"])
def showAdminLogin():
    return render_template("adminLogin.html")

@app.route("/deletionConfirmed")
def deletionConfirmed():
    return render_template("deletionConfirmed.html")
# Admin login page
# @app.route("/login")
# def adminLogin():
#     return render_template("adminLogin.html")

# retrieve booking
@app.route("/retrieveBooking")
def retrieveBooking():
    return render_template("retrieveBooking.html")
# show terms page
@app.route("/terms")
def showTerms():
    return render_template("terms.html")

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
        cur.execute("DELETE FROM Seat WHERE flightNumber = ?", (flight_id,))
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
        date = request.form["departure-date"]

        conn = getDbConnection()
        flights = conn.execute("""
            SELECT * FROM Flight
            WHERE departure = ? AND destination = ? AND departureDate = ?
        """, (departure, destination,date,)).fetchall()
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
@app.route("/deleteFlight/<int:flightID>", methods = ["GET", "POST"])
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
@app.route("/addBooking", methods=["POST"])
def addBooking():
    flightID = request.form["flightID"]
    seatID = request.form["seatID"]

    name = request.form["customerName"]
    address = request.form["customerAddress"]
    email = request.form["customerEmail"]
    phone = request.form["customerPhoneNum"]

    cardName = request.form["creditCardName"]
    cardNumber = request.form["creditCardNumber"]
    cardCvv = request.form["creditCardCvv"]
    cardExpiry = request.form["creditCardExpiry"]

    conn = getDbConnection()
    cur = conn.cursor()

    # Create customer
    cur.execute("""
    INSERT INTO Customer (customerName, customerAddress, customerEmail, customerPhoneNum)
    VALUES (?, ?, ?, ?)
    """, (name, address, email, phone))

    customerID = cur.lastrowid

    # Create booking
    cur.execute("""
    INSERT INTO Booking
    (dateBooked, totalCost, creditCardName, creditCardNumber,
     creditCardCvv, creditCardExpiry, customerID, flightNumber, seatID)
    VALUES (DATE('now'), ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        100,
        cardName,
        cardNumber,
        cardCvv,
        cardExpiry,
        customerID,
        flightID,
        seatID
    ))

    bookingID = cur.lastrowid

    # Assign seat
    cur.execute("""
    UPDATE Seat
    SET bookingID = ?
    WHERE seatID = ?
    """, (bookingID, seatID))

    conn.commit()
    conn.close()

    return redirect(url_for("showBooking", bookingID=bookingID))

#show booking
@app.route("/showBooking/<int:bookingID>/", methods = ["GET"])
def showBooking(bookingID):
    conn = getDbConnection()
    booking = conn.execute("""
    SELECT 
        Booking.bookingID,
        Seat.seatNumber,
        Customer.customerName,
        Customer.customerEmail,
        Flight.departure,
        Flight.departureDate,
        Flight.departureTime,
        Flight.destination,
        Flight.arrivalDate,
        Flight.arrivalTime,
        Airline.airlineName

    FROM Booking

    LEFT JOIN Customer ON Booking.customerID = Customer.customerID
    LEFT JOIN Flight ON Booking.flightNumber = Flight.flightNumber
    LEFT JOIN Airline ON Flight.airlineID = Airline.airlineID
    LEFT JOIN Seat ON Booking.seatID = Seat.seatID

    WHERE Booking.bookingID = ?

    """, (bookingID,)).fetchone()
    conn.close()
    if booking is None:
        conn.close()
        return """
                    <script>
                        alert('Booking does not exist');
                        window.history.back();
                    </script>
                    """
    print("DEBUG: booking =", booking)
    return render_template("showBooking.html", booking = booking)

#edit booking
@app.route("/editBooking/<int:bookingID>", methods=["GET", "POST"])
def editBooking(bookingID):
    conn = getDbConnection()
    b = conn.execute("""SELECT * from Booking INNER JOIN Customer ON Booking.customerID = Customer.customerID INNER JOIN Seat on Booking.seatID = Seat.seatID WHERE Booking.bookingID = ?""", (bookingID,)).fetchone()
    #getting customer id
    custId = conn.execute("""SELECT customerID FROM Booking WHERE Booking.bookingID = ?""", (bookingID,)).fetchone()[0]

    if b is None:
        conn.close()
        return """<script>
        alert('Booking does not exist');
        window.history.back();
        </script>"""
    
    if request.method == "POST":
        email = request.form["customerEmail"]
        phone = request.form["customerPhoneNum"]
        seat = request.form["seatNumber"]

        conn.execute("""UPDATE Customer
                     SET customerEmail = ?, customerPhoneNum = ? WHERE customerID = ?""", (email, phone, custId))
        conn.commit()
        conn.close()
        return redirect(f"/showBooking/{bookingID}")

    # GET REQUEST FOR THE FORM
    booking = conn.execute("SELECT * FROM Booking INNER JOIN Customer ON Booking.customerID = Customer.customerID INNER JOIN Seat ON Booking.seatID = Seat.seatID WHERE Booking.bookingID =?", (bookingID,)).fetchone()
    conn.close()
    return render_template("editBooking.html", booking=booking)   

#delete booking
@app.route("/deleteBooking/<int:bookingID>", methods = ["GET","POST"])
def deleteBooking(bookingID):
    conn = getDbConnection()
    booking = conn.execute("SELECT * FROM Booking WHERE bookingID =?", (bookingID,)).fetchone()
    if booking is None:
        conn.close()
        return
    else:
        if request.method == "POST":
            conn.execute("""Delete FROM Booking
                        WHERE bookingID = ?""", (bookingID,))
            conn.commit()
            conn.close()
            return render_template("deletionConfirmed.html", booking = booking)
    
        #GET method
        conn.close()
        return render_template("deleteBooking.html", booking=booking)

#add baggage  (not done yet, i do more on weekend)
#app.route("/addBagge/<text:customerName>/", methods=["GET", "POST"])
#def addBaggage(customerName):
#  conn = getDbConnection()
#   b = conn.execute("""SELECT * from Booking WHERE cusomerName = ?""", (cusomerName,)).fetchone()

#   if b is None:
#       conn.close()
#       return 
#       """
#       <script>
#           alert('Booking does not exist');
#           window.history.back();
#       </script>
#       """



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
    airline = conn.execute("""SELECT * FROM Airline WHERE airlineID = ?""", (airlineID,))
    conn.close()
    return render_template("showAirline.html", airline = airline)

#edit airline
@app.route("/editAirline/<int:airlineID>", methods=["GET", "POST"])
def editAirline(airlineID):
    if not airlineID.isdigit():
        return """
<script>
    alert('You have input an invalid data type, please input an integer');
    window.history.back();
</script>
"""
    conn = getDbConnection()
    a = conn.execute("SELECT * FROM Airline WHERE airlineID = ?", (airlineID,)).fetchone()    
    conn.close()

    if a is None:
        conn.close()
        return """
<script>
    alert('airline ID does not exist');
    window.history.back();
</script>
"""

    if request.method == "POST":
        airlineName = request.form["Airline Name"]
        airlineAddress = request.form["Airline Address"]
        conn.execute("""UPDATE Airline
                     SET airlineName = ?, airlineAddress = ?, WHERE airlineID = ?""", (airlineName, airlineAddress))
        conn.commit()
        conn.close()
        return redirect(f"/showAirline/{airlineID}")

    # GET REQUEST FOR THE FORM
    airline = conn.execute("SELECT * FROM Airline WHERE airlineID =?", (airlineID,)).fetchone()
    conn.close()
    return render_template("editAirline.html", airline=airline)   


#delete airline
@app.route("/deleteAirline/<int:airlineID>", methods = ["POST"])
def deleteAirline(airlineID):
    conn = getDbConnection()
    conn.execute("DELETE FROM Airline WHERE airlineID = ?", (airlineID,))
    conn.commit()
    conn.close()
    return redirect("/admin")

################################################################
#Seat
################################################################
@app.route("/selectSeat/<int:flightID>")
def selectSeat(flightID):

    conn = getDbConnection()

    seats = conn.execute("""
        SELECT seatID, seatNumber, bookingID
        FROM Seat
        WHERE flightNumber = ?
    """, (flightID,)).fetchall()

    conn.close()

    return render_template("selectSeat.html", seats=seats, flightID=flightID)
################################################################
#Customer
###############################################################



###############################################################
#Admin
##############################################################

@app.route("/adminLogin", methods=["POST"])
def adminLogin():
    conn = getDbConnection()

    username = request.form["username"]
    password = request.form["password"]

    a = conn.execute(
        "SELECT * FROM Admin WHERE username = ?",(username,)).fetchone()

    if a is None:
        conn.close()
        return """
        <script>
            alert('Incorrect login details');
            window.history.back();
        </script>
        """

    stored_password = a["password"]
    if stored_password != password:
        conn.close()
        return """
        <script>
            alert('Incorrect login details');
            window.history.back();
        </script>
        """

    conn.close()
    return render_template("home.html")



if __name__ == "__main__":
    app.run(debug=True)