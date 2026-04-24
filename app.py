from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# ------------------ MODELS ------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200))
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    tasks = Task.query.filter_by(user_id=session["user_id"]).all()
    return render_template("index.html", tasks=tasks)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            return "User already exists"

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session["user_id"] = user.id
            return redirect("/")
        else:
            return "Invalid credentials"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")

@app.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect("/login")

    content = request.form["task"]
    new_task = Task(content=content, user_id=session["user_id"])
    db.session.add(new_task)
    db.session.commit()
    return redirect("/")

@app.route("/complete/<int:id>")
def complete(id):
    task = Task.query.get(id)
    task.done = True
    db.session.commit()
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return redirect("/")

# ------------------ RUN ------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)