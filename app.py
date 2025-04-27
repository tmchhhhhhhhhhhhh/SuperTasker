from flask import Flask, render_template, request, redirect, url_for, flash
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app=Flask(__name__)
app.secret_key = 'supersecretkey123'


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask2site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

class MyTask(db.Model):
    name = db.Column(db.String(80), primary_key=True)
    priority = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    status = db.Column(db.String(10), nullable=False)   
    
    def __repr__(self) -> str:
        return f"Task('{self.name}', '{self.priority}', '{self.due_date}', '{self.status}')"

@app.route("/",methods=["POST", "GET"])
def index():
    if request.method == "POST":
        current_task = request.form["task_name"]
        priority = int(request.form["task_priority"])
        status = request.form["task_status"]
        new_task = MyTask(name=current_task, priority=priority, status=status)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for("index"))
        except Exception as e:
            db.session.rollback()
            flash("Error adding task: " + str(e), "error")

        flash("Task added successfully!", "success")
        return redirect(url_for("index"))
    else:
        tasks= MyTask.query.order_by(MyTask.priority).all()
        return render_template("index.html", tasks=tasks)

@app.route("/delete/<string:task_name>")
def delete_task(task_name: str):
    task_to_delete = MyTask.query.get_or_404(task_name)
    if task_to_delete:
        try:
            db.session.delete(task_to_delete)
            db.session.commit()
            flash("Task deleted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("Error deleting task: " + str(e), "error")
    else:
        flash("Task not found!", "error")
    return redirect("/")




@app.route("/update/<string:task_name>", methods=["GET", "POST"])
def update_task(task_name: str):
    task_to_update = MyTask.query.get_or_404(task_name)

    if request.method == "POST":
        task_to_update.name = request.form["task_name"]
        task_to_update.priority = int(request.form["task_priority"])
        task_to_update.status = request.form["task_status"]
        db.session.commit()
        flash("Task updated successfully!", "success")
        return redirect(url_for("index")) 
    return render_template("update.html", task=task_to_update)


if __name__ == "__main__":
    app.run(debug=True)