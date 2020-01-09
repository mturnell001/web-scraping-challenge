from flask import Flask, render_template, redirect
from pymongo import MongoClient
import scrape_mars

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
client = MongoClient("mongodb://localhost:27017")
nasa_db = client.nasa_db

# Route to render index.html template using data from Mongo
@app.route("/")
def home():

    # Find the first record of data from the mongo database
    try:
        nasa_data = nasa_db.mars.find()[0]
    except:
        return redirect("/scrape")
    else:
        # Return template and data
        return render_template("index.html", nasa=nasa_data)


# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():

    # Run the scrape function
    nasa_data = scrape_mars.scrape()

    # Update the Mongo database using update and upsert=True
    nasa_db.mars.update({}, nasa_data, upsert=True)

    # Redirect back to home page
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
