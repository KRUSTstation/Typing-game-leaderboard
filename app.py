import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from extensions import socketio
import leaderboard, database

load_dotenv()

def create_app():
   app = Flask(__name__)
   app.config.from_prefixed_env()




   if app.config.get("DATABASE") and not os.path.isabs(app.config["DATABASE"]):
      os.makedirs(app.instance_path, exist_ok=True)
      app.config["DATABASE"] = os.path.join(app.instance_path, app.config["DATABASE"])

   database.init_app(app)
   socketio.init_app(app)

   app.register_blueprint(leaderboard.bp)

   @app.route("/")
   def home():
      #whatever the home code belongs here
      return redirect(url_for("leaderboard.view")) #change this to render template for home page lol

   print(f"Current environment: {os.getenv("ENVIRONMENT")}")
   print(f"Using Database: {app.config.get("DATABASE")}")
   return app