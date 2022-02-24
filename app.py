"""Flask imports"""
import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for, abort)
from datetime import datetime
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
# Home page
@app.route("/home")
def home():
    """Function to return the home page"""
    return render_template("home.html")


# All gigs page
@app.route("/get_gigs")
def get_gigs():
    """Function to return all gigs"""
    if is_authenticated():
        gigs = mongo.db.gigs.find().sort('date', 1)
        return render_template("gigs.html", gigs=gigs)
    flash("You must be a band member to access this page!")
    return redirect(url_for("login"))


# Gig info page
@app.route("/gig_info/<gig_id>")
def gig_info(gig_id):
    """Show individual gigs using object id"""
    # Find specific gig from collection using primary id
    # if not found return a 404 redirect
    gig = mongo.db.gigs.find_one_or_404({"_id": ObjectId(gig_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
        "gig-info.html", gig=gig, categories=categories)


# Log in page
@app.route("/login", methods=["GET", "POST"])
def login():
    """Function to allow user login"""
    if request.method == "POST":
        username = request.form.get("username").lower()
        password = request.form.get("password")
        session["user"] = username
        existing_user = mongo.db.users.find_one(
            {"username": username})
        existing_password = mongo.db.users.find_one({"password": password})

        if existing_user:
            if existing_password:
                session["user"] = username
                flash("Welcome, {}!".format(username.capitalize()))
                return redirect(url_for("get_gigs"))
            else:
                # Password does not match
                flash("Incorrect password and/or username")
                return redirect(url_for("login"))

        flash("Incorrect password and/or username")
        return redirect(url_for("login"))

    return render_template("login.html")


# Log out
@app.route("/logout")
def logout():
    """Function to allow user to logout"""
    # If user is authenticated
    if is_authenticated():
        # Remove user from session cookies
        flash("You have successfully logged out")
        session.pop("user")

    return redirect(url_for("login"))


# Profile page
@app.route("/profile/", methods=["GET", "POST"])
def my_profile():
    """Function to show user's profile page"""
    # Check if user name is authenticated
    if is_authenticated():
        profiles = list(mongo.db.users.find())
        # Retrieve active username from database
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]

        if session["user"]:
            return render_template(
                "profile.html", username=username, profiles=profiles)

    return redirect(url_for("login"))


# Edit profile picture
@app.route("/edit_profile/<image_id>", methods=["GET", "POST"])
def edit_profile(image_id):
    """Function to edit profile image"""
    if request.method == "POST":
        change = {"$set": {"image_url": request.form.get("image_url")}}
        mongo.db.users.update_one({"_id": ObjectId(image_id)}, change)
        flash("Your profile image has been updated!")
        return redirect(url_for("my_profile"))
    # Check if user is authenticated
    if is_authenticated():
        image = mongo.db.users.find_one_or_404(
            {"_id": ObjectId(image_id)})
        return render_template("edit-image.html", image=image)
    return redirect(url_for('login'))


# Add gigs form
@app.route("/add_gigs", methods=["GET", "POST"])
def add_gigs():
    """Function to add gigs"""
    if request.method == "POST":
        date_time_str = request.form.get("date")
        date_time_obj = datetime.strptime(date_time_str, '%b %d, %y')
        # Create dictionary to collect all form data
        add = {
            "category_name": request.form.get("category_name").lower(),
            "arrival_time": request.form.get("arrival_time").lower(),
            "couple_name": request.form.get("couple_name"),
            "venue": request.form.get("venue"),
            "package_type": request.form.get("package_type"),
            "first_dance": request.form.get("first_dance"),
            "set_up_time": request.form.get("set_up_time"),
            "gig_date": request.form.get("gig_date"),
            "date": date_time_obj,
            "directions": request.form.get("directions"),
            "image_url": request.form.get("image_url")
        }

        # Insert all form data to mongodb gigs collection
        mongo.db.gigs.insert_one(add)
        flash("Gig added!")
        return redirect(url_for('get_gigs'))
    # Check if user is authenticated
    if is_authenticated():  
        # Create categories variable to alphabetically sort html select
        categories = mongo.db.gig_categories.find().sort("category_name", 1)
        if session["user"] == "adminjoe2308":
            return render_template("add-gigs.html", categories=categories)
        flash("You must be an Admin to perform that operation!")
    return redirect(url_for('login'))


# Edit gigs form
@app.route("/edit_gigs/<gig_id>", methods=["GET", "POST"])
def edit_gigs(gig_id):
    """ Function to edit gigs """
    # Check if user is authenticated
    if is_authenticated():
        # Check if object id is valid

        if request.method == "POST":
            date_time_str = request.form.get("date")
            date_time_obj = datetime.strptime(date_time_str, '%b %d, %y')
            # Create dictionary to collect all form data
            add = {
                "category_name": request.form.get("category_name").lower(),
                "arrival_time": request.form.get("arrival_time").lower(),
                "couple_name": request.form.get("couple_name"),
                "venue": request.form.get("venue"),
                "package_type": request.form.get("package_type"),
                "first_dance": request.form.get("first_dance"),
                "set_up_time": request.form.get("set_up_time"),
                "gig_date": request.form.get("gig_date"),
                "date": date_time_obj,
                "directions": request.form.get("directions"),
                "image_url": request.form.get("image_url")
            }

            # Update mongodb sneakers collection
            mongo.db.gigs.replace_one({"_id": ObjectId(gig_id)}, add)
            flash("Gig has been updated!")
            return redirect(url_for('get_gigs'))

    gig = mongo.db.gigs.find_one_or_404({"_id": ObjectId(gig_id)})

    categories = mongo.db.gig_categories.find().sort("category_name", 1)
    return render_template(
        "edit-gigs.html", gig=gig, categories=categories)


# Delete gigs
@app.route("/delete_gigs/<gig_id>")
def delete_gigs(gig_id):
    """ Function to delete gigs"""
    # Check if user is authenticated
    if is_authenticated():
        # Check if object id is valid

        mongo.db.gigs.delete_one({"_id": ObjectId(gig_id)})
        flash("Gig successfully deleted")
        return redirect(url_for('get_gigs'))

    flash("You must be an admin to delete gigs")
    return redirect(url_for("login"))


# Check if object id is valid
def is_object_id_valid(id_value):
    """ Validate is the id_value is a valid ObjectId
    """
    return id_value != "" and ObjectId.is_valid(id_value)


# Check if user is authenticated
def is_authenticated():
    """ Ensure that user is authenticated
    """
    return 'user' in session


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
