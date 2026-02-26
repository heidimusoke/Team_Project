from flask import Flask, render_template, request, redirect, url_for
import sqlite3

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