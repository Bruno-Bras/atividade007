from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projeto.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Contato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    tarefas = db.relationship('Tarefa', backref='contato', lazy=True, cascade='all, delete-orphan')

class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    prazo = db.Column(db.String(20), nullable=False)
    prioridade = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='a_fazer')
    contato_id = db.Column(db.Integer, db.ForeignKey('contato.id'), nullable=False)

class Cronograma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fase = db.Column(db.String(100), nullable=False)
    data_inicio = db.Column(db.String(20), nullable=False)
    data_fim = db.Column(db.String(20), nullable=False)
    tarefa_id = db.Column(db.Integer, db.ForeignKey('tarefa.id'), nullable=True)
    responsavel = db.Column(db.String(100), nullable=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return redirect(url_for('listar_tarefas'))

@app.route('/tarefas')
def listar_tarefas():
    tarefas = Tarefa.query.all()
    contatos = Contato.query.all()
    return render_template('tarefas.html', tarefas=tarefas, contatos=contatos)

@app.route('/tarefas/criar', methods=['POST'])
def criar_tarefa():
    descricao = request.form['descricao']
    prazo = request.form['prazo']
    prioridade = request.form['prioridade']
    status = request.form['status']
    contato_id = request.form['contato_id']

    nova = Tarefa(
        descricao=descricao,
        prazo=prazo,
        prioridade=prioridade,
        status=status,
        contato_id=contato_id
    )
    db.session.add(nova)
    db.session.commit()
    return redirect(url_for('listar_tarefas'))
