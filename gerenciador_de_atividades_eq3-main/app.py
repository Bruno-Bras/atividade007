from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, date

PRIORIDADES = ["baixa", "media", "alta"]
STATUS = ["a_fazer", "fazendo", "concluida"]


app=Flask(__name__)


app.config['SECRET_KEY'] = "the-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), nullable=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    prazo = db.Column(db.Date, nullable=True)
    prioridade = db.Column(db.String(10), default="media", nullable=False)
    status = db.Column(db.String(10), default="a_fazer", nullable=False)

    contact_id = db.Column(db.Integer, db.ForeignKey("contact.id"), nullable=True)
    contact = db.relationship("Contact", backref="tasks")


with app.app_context():
    db.create_all()

@app.post("/contacts/add")
def add_contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()

    if not name:
        flash("Digite o nome do contato")
        return redirect(url_for("home"))

    contact = Contact(name=name, email=email or None)
    db.session.add(contact)
    db.session.commit()
    flash("Contato adicionado com sucesso!")
    return redirect(url_for("home"))

@app.get("/")
def home():
    tasks = Task.query.order_by(Task.done.asc(), Task.created_at.desc()).all()
    contacts = Contact.query.order_by(Contact.name.asc()).all()
    return render_template("index.html", tasks=tasks, contacts=contacts)

@app.post("/add")
def add():
    title = request.form.get("title", "").strip()
    contact_id = request.form.get("contact_id", "").strip()

    if not title:
        flash("Digite a descrição da tarefa")
        return redirect(url_for("home"))

    contact = None

    if contact_id:
        contact = db.session.get(Contact, int(contact_id))

        if contact is None:
            flash("Contato inválido")
            return redirect(url_for("home"))

    task = Task(
        title=title,
        contact=contact
    )

    db.session.add(task)
    db.session.commit()

    flash("Tarefa adicionada com sucesso!")
    return redirect(url_for("home"))


@app.post("/delete/<int:task_id>")
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Atividade deletada ")
    return redirect(url_for("home"))

@app.post("/toggle/<int:task_id>")
def toggle(task_id):
    task = Task.query.get_or_404(task_id)
    task.done = not task.done
    db.session.commit()
    flash("Marcado como concluído" if task.done else "Ativo")
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)
