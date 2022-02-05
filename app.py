"""Flask imports"""
import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
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
    # Check if user is authenticated
    if is_authenticated():
        if request.method == "POST":
            change = {"$set": {"image_url": request.form.get("image_url")}}
            mongo.db.users.update_one({"_id": ObjectId(image_id)}, change)
            flash("Profile image has been updated!")
            return redirect(url_for("my_profile"))
    image = mongo.db.users.find_one_or_404(
        {"_id": ObjectId(image_id)})
    return render_template("edit-image.html", image=image)





# Check if user is authenticated
def is_authenticated():
    """ Ensure that user is authenticated
    """
    return 'user' in session


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
