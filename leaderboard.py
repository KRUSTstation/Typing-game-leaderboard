from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_db




bp = Blueprint("leaderboard", __name__)
@bp.route("/edit", methods=["GET", "POST"])
def edit():
   if request.method == "POST":
      name = request.form["name"]
      score = request.form["score"]
      phone_num = request.form["phone_num"]
      page = request.args.get("page", 1, type=int)
      if score and name:
         db = get_db()
         db.execute(
            "INSERT INTO leaderboard (name, score, phone_num) VALUES (?, ?, ?)",
            (name, score, phone_num)
         )
         db.commit()
         flash(f"Record added", category="success")
         return redirect(url_for("leaderboard.edit", page=page))
      else:
         flash(f"type the score/name bruh", category="error")

   db = get_db()
   page = request.args.get("page", 1, type=int)
   per_page = 10
   offset = (page - 1) * per_page

   leaderboard = db.execute(
      "SELECT * FROM leaderboard ORDER BY score DESC LIMIT ? OFFSET ?",
      (per_page, offset)
   ).fetchall()

   total = db.execute("SELECT COUNT(*) FROM leaderboard").fetchone()[0]
   total_pages = (total + per_page - 1) // per_page  # ceiling division

   return render_template("leaderboard/edit.html",
      leaderboard=leaderboard,
      page=page,
      total_pages=total_pages
   )
      

@bp.route("/lb")
def view():
   db = get_db()
   page = request.args.get("page", 1, type=int)
   per_page = 10
   offset = (page - 1) * per_page

   leaderboard = db.execute(
      "SELECT * FROM leaderboard ORDER BY score DESC LIMIT ? OFFSET ?",
      (per_page, offset)
   ).fetchall()

   total = db.execute("SELECT COUNT(*) FROM leaderboard").fetchone()[0]
   total_pages = (total + per_page - 1) // per_page  # ceiling division

   return render_template("leaderboard/view.html",
      leaderboard=leaderboard,
      page=page,
      total_pages=total_pages
   )

@bp.route("/delete/<int:id>", methods=["POST"])
def delete(id):
   db = get_db()
   db.execute("DELETE FROM leaderboard WHERE id = (?)", (id,))
   db.commit()
   flash(f"task {id} deleted", category="success")
   return redirect(url_for("leaderboard.edit"))