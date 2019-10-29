import numpy as np
import pandas as dp
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#engine = create_engine("sqlite:///Resources/hawaii.sqlite")
engine = create_engine("sqlite:////Users/joumanarahime/Documents/Vanderbilt BootCamp/sqlalchemy-challenge/Resources/hawaii.sqlite")
Base=automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session=Session(engine)


max_date = session.execute('select MAX(date) from measurement').fetchall()
max_date = max_date[0][0]

# Calculate the date 1 year ago from the last data point in the database
date_stamp = dt.datetime.strptime(max_date,'%Y-%m-%d')
year = date_stamp.year
month = date_stamp.month
day = date_stamp.day

prior_year = f'{year-1}-{month:02d}-{day:02d}'


#Create the app
app = Flask(__name__)


# index route
@app.route("/")
def home():
    """List of all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"------------------------<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>` and `/api/v1.0/<start>/<end>"
        )



# 4. /api/v1.0/precipitation

@app.route("/api/v1.0/precipitation")
def prec():
    session=Session(engine)
    results = session.query(Measurement.prcp, Measurement.date).filter(Measurement.date > prior_year).all()
    session.close()
    prec_data=[]

    for result in results:
        prec_dict = {result.date: result.prcp }
        prec_data.append(prec_dict)

    return jsonify(prec_data)





@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    results= session.execute('select station, count(*) as count from measurement group by station order by count(station) desc ').fetchall()

    station_data=[]
    for result in results:
        station_dict = {result.station: result.count}
        station_data.append(station_dict)
    
    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
 
    cal_temp = session.execute(f"select date, min(tobs), avg(tobs), max(tobs) from measurement where date> '{prior_year}'").fetchall()
   
    temp_dict= {
        "Date": cal_temp[0][0],
        "Low Temp": cal_temp[0][1],
        "Avg Temp": cal_temp[0][2],
        "Highest Temp": cal_temp[0][3]
    }
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>")
def start(start):
 
    sel= [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results= (session.query(*sel)
                    .filter(func.strftime("%Y-%m-%d", Measurement.date)>=start)
                    .all())
    dates=[]

    for result in results:
        start_dict={
                    "Date": result[0][0],
                    "Low Temp": result[0][1],
                    "Avg Temp": result[0][2],
                    "Highest Temp": result[0][3]    
                    }
        dates.append(start_dict)            
    return jsonify(dates)


@app.route("/api/v1.0/<start>/<end>")
def startEnd(start, end):
 
    sel= [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results= (session.query(*sel)
                    .filter(func.strftime("%Y-%m-%d", Measurement.date)>=start)
                    .filter(func.strftime("%Y-%m-%d", Measurement.date)<=end)
                    .all())

    dates=[]
    for result in results:
        startEnd_dict={}
        startEnd_dict={
                    "Date": result[0][0],
                    "Low Temp": result[0][1],
                    "Avg Temp": result[0][2],
                    "Highest Temp": result[0][3]    
                    }
        dates.append(startEnd_dict)
    return jsonify(dates)


if __name__ == "__main__":
    app.run(debug=True)