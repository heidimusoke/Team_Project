from flask import Flask, render_template, request, redirect, url_for
import sqlite3
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
        conn.execute("""
            INSERT INTO Flight 
            (departure, destination, departureDate, departureTime, arrivalDate, arrivalTime, numberSeats)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (departure, destination, departureDate, departureTime, arrivalDate, arrivalTime, numberSeats))

        flight_id = sqlite3.Cursor.lastrowid
        #for loop to make seats based on how many seats in flight
        for i in range(1, numberSeats + 1):
            seat_number = f"S{i}"
            seat_cost = 100  # temp number we can change as we go on

            conn.execute("""
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


if __name__ == "__main__":
    app.run(debug=True)