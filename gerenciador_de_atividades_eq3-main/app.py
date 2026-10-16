from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, date

PRIORIDADES = ["baixa", "media", "alta"]
STATUS = {"a_fazer": "A fazer", "fazendo": "Fazendo", "concluida": "Concluída"}  
STATUS_ROTULOS = {**STATUS, "atrasada": "Atrasada"}

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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    prazo = db.Column(db.Date, nullable=True)
    prioridade = db.Column(db.String(10), default="media", nullable=False)
    status = db.Column(db.String(10), default="a_fazer", nullable=False)

    contact_id = db.Column(db.Integer, db.ForeignKey("contact.id"), nullable=True)
    contact = db.relationship("Contact", backref="tasks")
    @property
    def status_atual(self):
        if self.status != "concluida" and self.prazo and self.prazo < date.today():
            return "atrasada"
        return self.status

    @property
    def status_rotulo(self):
        return STATUS_ROTULOS[self.status_atual]


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
    tasks = Task.query.order_by((Task.status == "concluida").asc(), Task.created_at.desc()).all()
    contacts = Contact.query.order_by(Contact.name.asc()).all()
    return render_template("index.html", tasks=tasks, contacts=contacts, status_opcoes=STATUS)

@app.post("/add")
def add():
    title = request.form.get("title", "").strip()
    contact_id = request.form.get("contact_id", "").strip()
    prazo_str = request.form.get("prazo", "").strip()
    prioridade = request.form.get("prioridade", "media")

    if not title:
        flash("Digite a descrição da tarefa")
        return redirect(url_for("home"))

    try:
        prazo = date.fromisoformat(prazo_str)
    except ValueError:
        flash("Informe um prazo válido")
        return redirect(url_for("home"))

    if prioridade not in PRIORIDADES:
        flash("Prioridade inválida")
        return redirect(url_for("home"))

    contact = None

    if contact_id:
        contact = db.session.get(Contact, int(contact_id))

        if contact is None:
            flash("Contato inválido")
            return redirect(url_for("home"))

    task = Task(
        title=title,
        contact=contact,
        prazo=prazo,
        prioridade=prioridade,
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

@app.post("/status/<int:task_id>")
def set_status(task_id):
    task = db.get_or_404(Task, task_id)
    novo_status = request.form.get("status", "")

    if novo_status not in STATUS:
        flash("Status inválido")
        return redirect(url_for("home"))

    task.status = novo_status
    db.session.commit()
    flash("Status atualizado")
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)
