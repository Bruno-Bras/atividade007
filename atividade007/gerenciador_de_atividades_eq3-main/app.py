"""Gerenciador de Atividades — Atividade 007 (Equipe 3).

Rodar: run.cmd (Windows) ou python app.py  ->  http://127.0.0.1:5000
"""

import os
import webbrowser
from datetime import date, datetime, timedelta, timezone
from threading import Timer

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy


# --- Configuração do Flask e do banco ---------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "atividade007")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///todo.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# --- Rótulos usados nas telas -----------------------------------------------
PRIORIDADES = ["baixa", "media", "alta"]
PRIORIDADE_ROTULOS = {"baixa": "Baixa", "media": "Média", "alta": "Alta"}

STATUS = {
    "a_fazer": "A fazer",
    "fazendo": "Fazendo",
    "concluida": "Concluída",
}
STATUS_ROTULOS = {**STATUS, "atrasada": "Atrasada"}
STATUS_ORDEM = ["atrasada", "fazendo", "a_fazer", "concluida"]

MESES_PT = [
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


# --- Tabelas do banco -------------------------------------------------------
class Contact(db.Model):
    """Responsável pelas tarefas."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), nullable=True)

    @property
    def total_tarefas(self):
        return len(self.tasks)

    @property
    def resumo_status(self):
        """Quantidade de tarefas por status."""
        resumo = {chave: 0 for chave in STATUS_ORDEM}
        for tarefa in self.tasks:
            resumo[tarefa.status_atual] += 1
        return resumo


class Task(db.Model):
    """Tarefa do projeto."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)          # descrição
    etapa = db.Column(db.String(80), nullable=True)            # fase do projeto
    data_inicio = db.Column(db.Date, nullable=True)
    duracao = db.Column(db.Integer, nullable=True)             # em dias
    prazo = db.Column(db.Date, nullable=True)                  # data final
    prioridade = db.Column(db.String(10), default="media", nullable=False)
    status = db.Column(db.String(10), default="a_fazer", nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    contact_id = db.Column(db.Integer, db.ForeignKey("contact.id"), nullable=True)
    contact = db.relationship("Contact", backref="tasks")

    @property
    def inicio(self):
        """Data inicial (falta? usa a final)."""
        return self.data_inicio or self.data_fim

    @property
    def data_fim(self):
        """Prazo informado ou início + duração - 1."""
        if self.prazo:
            return self.prazo
        if self.data_inicio and self.duracao:
            return self.data_inicio + timedelta(days=self.duracao - 1)
        return self.data_inicio

    @property
    def duracao_dias(self):
        if self.data_inicio and self.data_fim:
            return (self.data_fim - self.data_inicio).days + 1
        return self.duracao or 1

    @property
    def status_atual(self):
        """Prazo vencido e não concluída = atrasada."""
        if self.status != "concluida" and self.prazo and self.prazo < date.today():
            return "atrasada"
        return self.status

    @property
    def status_rotulo(self):
        return STATUS_ROTULOS[self.status_atual]

    @property
    def prioridade_rotulo(self):
        return PRIORIDADE_ROTULOS.get(self.prioridade, self.prioridade)

    @property
    def esta_atrasada(self):
        return self.status_atual == "atrasada"


# --- Funções de apoio -------------------------------------------------------
def iniciais(nome):
    """Até duas letras para o avatar. Ex.: Bruno Bras -> BB."""
    partes = [p for p in (nome or "").split() if p]
    if not partes:
        return "?"
    if len(partes) == 1:
        return partes[0][:2].upper()
    return (partes[0][0] + partes[-1][0]).upper()


def data_br(valor, formato="%d/%m/%Y"):
    """Data como dia/mês/ano."""
    return valor.strftime(formato) if valor else "—"


app.jinja_env.filters["initials"] = iniciais
app.jinja_env.filters["data_br"] = data_br


def ler_data(texto, nome):
    """Texto -> data. Devolve (data, erro)."""
    if not texto:
        return None, None
    try:
        return date.fromisoformat(texto), None
    except ValueError:
        return None, f"{nome} inválida."


def ler_formulario_tarefa():
    """Lê o formulário e devolve (dados, erro)."""
    title = request.form.get("title", "").strip()
    if not title:
        return None, "Digite a descrição da tarefa."

    prioridade = request.form.get("prioridade", "media")
    if prioridade not in PRIORIDADES:
        return None, "Prioridade inválida."

    status = request.form.get("status", "a_fazer")
    if status not in STATUS:
        return None, "Status inválido."

    data_inicio, erro = ler_data(request.form.get("data_inicio", "").strip(), "Data inicial")
    if erro:
        return None, erro
    prazo, erro = ler_data(request.form.get("prazo", "").strip(), "Prazo")
    if erro:
        return None, erro

    duracao = None
    duracao_texto = request.form.get("duracao", "").strip()
    if duracao_texto:
        try:
            duracao = int(duracao_texto)
        except ValueError:
            return None, "Duração deve ser um número inteiro de dias."
        if duracao < 1:
            return None, "A duração deve ser de pelo menos 1 dia."

    # Com duração informada, o prazo é recalculado (regra do vídeo).
    if duracao and data_inicio:
        prazo = data_inicio + timedelta(days=duracao - 1)

    if not data_inicio and not prazo:
        return None, "Informe a data inicial ou o prazo da tarefa."
    if not data_inicio:
        data_inicio = prazo
    if not prazo:
        prazo = data_inicio + timedelta(days=(duracao - 1) if duracao else 0)

    contact = None
    contact_id = request.form.get("contact_id", "").strip()
    if contact_id:
        try:
            contact = db.session.get(Contact, int(contact_id))
        except ValueError:
            contact = None
        if contact is None:
            return None, "Responsável inválido."

    return {
        "title": title,
        "etapa": request.form.get("etapa", "").strip() or None,
        "data_inicio": data_inicio,
        "duracao": duracao,
        "prazo": prazo,
        "prioridade": prioridade,
        "status": status,
        "contact": contact,
    }, None


def ordenar_tarefas(tarefas):
    """Não concluídas primeiro, depois pelo prazo."""
    return sorted(
        tarefas,
        key=lambda t: (
            t.status == "concluida",
            t.prazo is None,
            t.prazo or date.max,
            (t.title or "").lower(),
        ),
    )


def estatisticas(tarefas):
    """Contagem por status. Ex.: {'total': 10, 'a_fazer': 4, ...}."""
    stats = {"total": len(tarefas), **{chave: 0 for chave in STATUS_ORDEM}}
    for tarefa in tarefas:
        stats[tarefa.status_atual] += 1
    return stats


def montar_gantt(tarefas):
    """Monta a grade do cronograma (dias, meses e etapas)."""
    hoje = date.today()
    com_data = [t for t in tarefas if t.inicio and t.data_fim]

    if com_data:
        primeiro = min(t.inicio for t in com_data)
        ultimo = max(t.data_fim for t in com_data)
    else:
        primeiro = hoje
        ultimo = hoje + timedelta(days=13)

    # Grade alinhada a semanas (segunda a domingo), sempre incluindo hoje.
    primeiro = min(primeiro, hoje)
    ultimo = max(ultimo, hoje)
    inicio_grade = primeiro - timedelta(days=primeiro.weekday())
    fim_grade = ultimo + timedelta(days=(6 - ultimo.weekday()))

    dias = []
    dia = inicio_grade
    while dia <= fim_grade:
        dias.append(dia)
        dia += timedelta(days=1)

    meses = []
    for dia in dias:
        chave = (dia.year, dia.month)
        if meses and meses[-1]["chave"] == chave:
            meses[-1]["span"] += 1
        else:
            meses.append({
                "chave": chave,
                "label": f"{MESES_PT[dia.month]} de {dia.year}",
                "span": 1,
            })

    grupos = {}
    for tarefa in com_data:
        grupos.setdefault(tarefa.etapa or "Outras tarefas", []).append(tarefa)
    ordem = sorted(grupos.items(), key=lambda item: min(t.inicio for t in item[1]))
    fases = [
        {"nome": nome, "tarefas": sorted(itens, key=lambda t: (t.inicio, t.data_fim))}
        for nome, itens in ordem
    ]

    return {
        "dias": dias,
        "meses": meses,
        "fases": fases,
        "hoje": hoje,
        "inicio": inicio_grade,
        "fim": fim_grade,
        "sem_data": [t for t in tarefas if not (t.inicio and t.data_fim)],
    }


# Cria o banco na primeira execução.
with app.app_context():
    db.create_all()


# --- Rotas (páginas e ações) ------------------------------------------------
@app.get("/")
def home():
    """Painel inicial."""
    tarefas = ordenar_tarefas(Task.query.all())
    contatos = Contact.query.order_by(Contact.name.asc()).all()
    return render_template(
        "index.html",
        nav="home",
        tarefas=tarefas,
        contatos=contatos,
        stats=estatisticas(tarefas),
        status_opcoes=STATUS,
        prioridade_rotulos=PRIORIDADE_ROTULOS,
    )


@app.get("/tarefas")
def tarefas():
    """Tarefas agrupadas por responsável, com filtros."""
    contatos = Contact.query.order_by(Contact.name.asc()).all()
    filtro_responsavel = request.args.get("responsavel", "").strip()
    filtro_status = request.args.get("status", "").strip()
    filtro_prioridade = request.args.get("prioridade", "").strip()

    def passa(tarefa):
        if filtro_responsavel == "sem":
            if tarefa.contact_id is not None:
                return False
        elif filtro_responsavel:
            if str(tarefa.contact_id) != filtro_responsavel:
                return False
        if filtro_status and tarefa.status_atual != filtro_status:
            return False
        if filtro_prioridade and tarefa.prioridade != filtro_prioridade:
            return False
        return True

    filtradas = [t for t in ordenar_tarefas(Task.query.all()) if passa(t)]

    grupos = []
    for contato in contatos:
        itens = [t for t in filtradas if t.contact_id == contato.id]
        if itens:
            grupos.append({"contact": contato, "tarefas": itens})
    sem = [t for t in filtradas if t.contact_id is None]
    if sem:
        grupos.append({"contact": None, "tarefas": sem})

    return render_template(
        "tarefas.html",
        nav="tarefas",
        grupos=grupos,
        contatos=contatos,
        total=len(filtradas),
        stats=estatisticas(filtradas),
        status_opcoes=STATUS,
        filtro_responsavel=filtro_responsavel,
        filtro_status=filtro_status,
        filtro_prioridade=filtro_prioridade,
    )



@app.get("/contatos")
def contatos():
    """Lista de responsáveis."""
    lista = Contact.query.order_by(Contact.name.asc()).all()
    return render_template(
        "contatos.html",
        nav="contatos",
        contatos=lista,
        status_opcoes=STATUS,
        total=len(lista),
    )


@app.post("/contacts/add")
def add_contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    if not name:
        flash("Digite o nome do contato.", "erro")
        return redirect(request.form.get("next") or url_for("home"))
    db.session.add(Contact(name=name, email=email or None))
    db.session.commit()
    flash("Contato adicionado com sucesso!", "ok")
    return redirect(request.form.get("next") or url_for("home"))


@app.post("/contacts/<int:contact_id>/delete")
def delete_contact(contact_id):
    """Remove o contato; as tarefas dele ficam sem responsável."""
    contact = db.get_or_404(Contact, contact_id)
    for tarefa in list(contact.tasks):
        tarefa.contact = None
    db.session.delete(contact)
    db.session.commit()
    flash("Contato removido. As tarefas dele ficaram sem responsável.", "ok")
    return redirect(request.form.get("next") or url_for("contatos"))


@app.post("/add")
def add():
    dados, erro = ler_formulario_tarefa()
    if erro:
        flash(erro, "erro")
        return redirect(url_for("home"))
    db.session.add(Task(**dados))
    db.session.commit()
    flash("Tarefa adicionada com sucesso!", "ok")
    return redirect(url_for("home"))


@app.route("/editar/<int:task_id>", methods=["GET", "POST"])
def editar(task_id):
    if request.method == "POST":
        dados, erro = ler_formulario_tarefa()
        if erro:
            flash(erro, "erro")
            return redirect(url_for("editar", task_id=task_id))
        tarefa = db.get_or_404(Task, task_id)
        for campo, valor in dados.items():
            setattr(tarefa, campo, valor)
        db.session.commit()
        flash("Tarefa atualizada!", "ok")
        return redirect(url_for("tarefas"))

    return render_template(
        "editar.html",
        nav="tarefas",
        tarefa=db.get_or_404(Task, task_id),
        contatos=Contact.query.order_by(Contact.name.asc()).all(),
        status_opcoes=STATUS,
    )


@app.post("/delete/<int:task_id>")
def delete(task_id):
    tarefa = db.get_or_404(Task, task_id)
    db.session.delete(tarefa)
    db.session.commit()
    flash("Tarefa apagada.", "ok")
    return redirect(request.form.get("next") or url_for("home"))


@app.post("/status/<int:task_id>")
def set_status(task_id):
    tarefa = db.get_or_404(Task, task_id)
    novo_status = request.form.get("status", "")
    if novo_status not in STATUS:
        flash("Status inválido.", "erro")
        return redirect(request.form.get("next") or url_for("home"))
    tarefa.status = novo_status
    db.session.commit()
    flash("Status atualizado.", "ok")
    return redirect(request.form.get("next") or url_for("home"))


if __name__ == "__main__":
    # Abre o navegador sozinho.
    Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(debug=True, use_reloader=False)
