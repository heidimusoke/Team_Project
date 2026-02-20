import sqlite3
def getDbConnection():
    conn = sqlite3.connect("AirPlaneSystem.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/showFlight")
def showFlights():
    conn = getDbConnection()
    flights= conn.execute("Select * from Flight").fetchall()
    conn.close()


@app.route("/editFlight")
def editFlight():


@app.route("/addFlight")
def addFlight():
    conn=getDbConnection()
    conn.
