import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# 1. import Flask
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
# 2. Create an app, being sure to pass __name__
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Home route
@app.route("/")
def welcome():
    session = Session(engine)
    return (
        f"Welcome to the API Homepage<br/>"
        f"<br/>"
        f"Available routes:<br/>"
        f"<br/>" 
        f"The list of precipitation data with dates:<br/>" 
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"  
        f"The list of stations and names:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"  
        f"The list of temprture observations:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"  
        f"Temperatures for given start date: (USE 'yyyy-mm-dd' format):<br/>"
        f"/api/v1.0/min_max_avg/&lt;start date&gt;<br/>"
        f"<br/>"
        f"Tempratures for given start and end date: (USE 'yyyy-mm-dd'/'yyyy-mm-dd' format):<br/>"
        f"/api/v1.0/min_max_avg/&lt;start date&gt;/&lt;end date&gt;<br/>"
        f"<br/>"
        f"i.e. <a href='/api/v1.0/min_max_avg/2012-01-01/2016-12-31' target='_blank'>/api/v1.0/min_max_avg/2012-01-01/2016-12-31</a>"
    )

##################################################################
# Precipitation route
@app.route('/api/v1.0/precipitation/')
def precipitation():
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    first_date = last_date - dt.timedelta(days=365)
    last_year_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= first_date).all()
    last_year_data = list(np.ravel(last_year_data))

    session.close()
    
    return jsonify(last_year_data)

# Return a JSON-list of stations from the dataset.
@app.route('/api/v1.0/stations/')
def stations():
    session = Session(engine)
    stations = session.query(Station.station,Station.name).all()
    stations = list(np.ravel(stations))

    session.close()

    return jsonify(stations)


##################################################################
# Return a JSON-list of Temperature Observations from the dataset.
@app.route('/api/v1.0/tobs/')
def tobs():
    session = Session(engine)
    stations = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    most_active_station = stations[0][0]
    station_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).all()
    station_data = list(np.ravel(station_data))

    session.close()

    return jsonify(station_data)


##################################################################
# create start route
@app.route("/api/v1.0/min_max_avg/<start>")
def start(start):
    session = Session(engine)

    """Return a JSON list of the temperature for a given start date."""

    # take any date and convert to yyyy-mm-dd format for the query
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).all()

    session.close()

    # list to hold results
    t_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["Tmin"] = result[0]
        r["Tavg"] = result[1]
        r["Tmax"] = result[2]
        t_list.append(r)

    # jsonify the result
    return jsonify(t_list)

##################################################################
@app.route("/api/v1.0/min_max_avg/<start>/<end>")
def start_end(start, end):
    session = Session(engine)

    """Return a JSON list of the temperature for a given start and end date."""
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    end_dt = dt.datetime.strptime(end, "%Y-%m-%d")
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).filter(Measurement.date <= end_dt)

    session.close()

    # list to hold results
    t_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["EndDate"] = end_dt
        r["Tmin"] = result[0]
        r["Tavg"] = result[1]
        r["Tmax"] = result[2]
        t_list.append(r)

    # jsonify the result
    return jsonify(t_list)

##########################################################
#run the app
if __name__ == "__main__":
    app.run(debug=True)