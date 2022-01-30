import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for, abort)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

@app.route("/")
@app.route("/get_gigs")
def get_gigs():
    gigs = mongo.db.gigs.find()
    return render_template("gigs.html", gigs=gigs)


@app.route("/gig_info/<gig_id>")
def gig_info(gig_id):
    # Find specific gig from collection using primary id
    # if not found return a 404 redirect
    gig = mongo.db.gigs.find_one_or_404({"_id": ObjectId(gig_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
        "gig-info.html", gig=gig, categories=categories)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
