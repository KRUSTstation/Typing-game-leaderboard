from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_db
from extensions import socketio

bp = Blueprint("leaderboard", __name__)

def _get_leaderboard_data():
   """Fetch all leaderboard rows sorted ASC — used by both HTTP and socket emit."""
   db = get_db()
   rows = db.execute("SELECT * FROM leaderboard ORDER BY score DESC").fetchall()
   return [{**dict(row), "time": str(row["time"])} for row in rows]

@bp.route("/edit", methods=["GET", "POST"])
def edit():
   if request.method == "POST":
      name = request.form["name"]
      score_raw = request.form["score"]
      phone_num = request.form.get("phone_num") or None
      page = request.args.get("page", 1, type=int)
      try: score = int(score_raw)
      except (ValueError, TypeError): score = None
      if score is not None and name:
         db = get_db()
         db.execute(
            "INSERT INTO leaderboard (name, score, phone_num) VALUES (?, ?, ?)",
            (name, score, phone_num)
         )
         db.commit()
         socketio.emit("leaderboard_update", _get_leaderboard_data())
         flash("Record added", category="success")
         return redirect(url_for("leaderboard.edit", page=page))
      else:
         flash("Name and score are required", category="error")

   db = get_db()
   page = request.args.get("page",1, type=int)
   per_page = 10
   offset = (page-1) * per_page

   leaderboard_data = db.execute(
      "SELECT * FROM leaderboard ORDER BY score ASC LIMIT ? OFFSET ?",
      (per_page, offset)
   ).fetchall()

   total = db.execute("SELECT COUNT(*) FROM leaderboard").fetchone()[0]
   total_pages = max(1, (total+per_page-1) // per_page)

   return render_template("leaderboard/edit.html",
      leaderboard=leaderboard_data,
      page=page,
      total_pages=total_pages
   )


@bp.route("/lb")
def view():
   db = get_db()
   page = request.args.get("page", 1, type=int)
   per_page = 10
   offset = (page - 1) * per_page

   leaderboard_data = db.execute(
      "SELECT * FROM leaderboard ORDER BY score DESC LIMIT ? OFFSET ?",
      (per_page, offset)
   ).fetchall()

   total = db.execute("SELECT COUNT(*) FROM leaderboard").fetchone()[0]
   total_pages = max(1, (total + per_page - 1) // per_page)

   return render_template("leaderboard/view.html",
      leaderboard=leaderboard_data,
      page=page,
      total_pages=total_pages
   )


@bp.route("/delete/<int:id>", methods=["POST"])
def delete(id):
   db = get_db()
   db.execute("DELETE FROM leaderboard WHERE id = (?)", (id,))
   db.commit()
   socketio.emit("leaderboard_update", _get_leaderboard_data())
   flash("Record deleted", category="success")
   return redirect(url_for("leaderboard.edit"))

