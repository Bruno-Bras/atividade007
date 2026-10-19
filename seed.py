"""Cria os dados de exemplo (contatos da Equipe 3 e cronograma do projeto).

Uso: python seed.py  |  python seed.py --reset
"""

import sys
from datetime import date, timedelta

from app import app, db, Contact, Task

HOJE = date.today()
INICIO_PROJETO = HOJE - timedelta(days=7)

CONTATOS = [
    ("Gustavo Guarlott", "gustavo@exemplo.com"),
    ("Bruno Brás Barros", "bruno@exemplo.com"),
    ("Cláudio Von Ehnert", "claudio@exemplo.com"),
]

# (titulo, etapa, offset_de_dias, duracao, responsavel, prioridade, status)
TAREFAS = [
    # Etapa 1 - Estrutura de dados
    ("Definir as colunas base: Tarefa, Data Inicial, Duração e Data Final",
     "1. Estrutura de dados", 0, 2, "Gustavo Guarlott", "alta", "concluida"),
    ("Preencher as tarefas do projeto com suas datas e durações",
     "1. Estrutura de dados", 2, 3, "Bruno Brás Barros", "media", "concluida"),
    ("Implementar a fórmula Data Final = [Data Inicial] + [Duração] − 1",
     "1. Estrutura de dados", 5, 2, "Cláudio Von Ehnert", "alta", "fazendo"),

    # Etapa 2 - Cabeçalho do calendário
    ("Montar o cabeçalho de datas do calendário",
     "2. Cabeçalho do calendário", 7, 2, "Gustavo Guarlott", "media", "fazendo"),
    ('Aplicar o formato de número personalizado "d" no cabeçalho',
     "2. Cabeçalho do calendário", 9, 2, "Bruno Brás Barros", "baixa", "a_fazer"),

    # Etapa 3 - Fórmula lógica dinâmica
    ('Escrever a fórmula =SE(E(G$2>=$C3;G$2<=$E3);"OK";"")',
     "3. Fórmula lógica dinâmica", 11, 3, "Cláudio Von Ehnert", "alta", "a_fazer"),
    ("Replicar a fórmula com referências absolutas e relativas ($)",
     "3. Fórmula lógica dinâmica", 14, 2, "Gustavo Guarlott", "media", "a_fazer"),

    # Etapa 4 - Formatação condicional
    ('Criar a regra condicional "Texto é exatamente OK"',
     "4. Formatação condicional", 16, 2, "Bruno Brás Barros", "media", "a_fazer"),
    ("Pintar fundo e texto com #2196F3 para formar as barras do Gantt",
     "4. Formatação condicional", 18, 2, "Cláudio Von Ehnert", "alta", "a_fazer"),
    ("Validar a atualização dinâmica ao alterar datas e durações",
     "4. Formatação condicional", 20, 3, "Gustavo Guarlott", "alta", "a_fazer"),
]


def seed(reset=False):
    with app.app_context():
        if reset:
            Task.query.delete()
            Contact.query.delete()
            db.session.commit()
            print("Base limpa.")

        contatos = {}
        for nome, email in CONTATOS:
            contato = Contact.query.filter_by(name=nome).first()
            if contato is None:
                contato = Contact(name=nome, email=email)
                db.session.add(contato)
            contatos[nome] = contato
        db.session.commit()

        criadas = 0
        for titulo, etapa, offset, duracao, responsavel, prioridade, status in TAREFAS:
            if Task.query.filter_by(title=titulo).first():
                continue
            inicio = INICIO_PROJETO + timedelta(days=offset)
            prazo = inicio + timedelta(days=duracao - 1)   # prazo = início + duração - 1
            db.session.add(Task(
                title=titulo,
                etapa=etapa,
                data_inicio=inicio,
                duracao=duracao,
                prazo=prazo,
                prioridade=prioridade,
                status=status,
                contact=contatos[responsavel],
            ))
            criadas += 1
        db.session.commit()

        print(f"Contatos: {Contact.query.count()} | "
              f"Tarefas: {Task.query.count()} (novas: {criadas})")


if __name__ == "__main__":
    seed(reset="--reset" in sys.argv)
