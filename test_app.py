"""Teste rápido do sistema (roda sem navegador).

Uso: python test_app.py
"""

import os
import sys
import tempfile
from datetime import date, timedelta

# Banco temporário, para não mexer no todo.db real.
TEST_DB = os.path.join(tempfile.mkdtemp(prefix="atv007_"), "test.db")
os.environ["DATABASE_URL"] = "sqlite:///" + TEST_DB.replace("\\", "/")

from app import app, db, Contact, Task  # noqa: E402


def check(condicao, mensagem):
    if not condicao:
        print(f"  ✗ FALHOU: {mensagem}")
        sys.exit(1)
    print(f"  ✓ {mensagem}")


def main():
    app.config.update(TESTING=True)
    with app.app_context():
        db.drop_all()
        db.create_all()

    client = app.test_client()

    print("1) Página inicial")
    check(client.get("/").status_code == 200, "GET / responde 200")

    print("2) Contatos")
    resp = client.post(
        "/contacts/add",
        data={"name": "Gustavo Guarlott", "email": "gustavo@exemplo.com"},
        follow_redirects=True,
    )
    check(resp.status_code == 200, "POST /contacts/add responde 200")
    with app.app_context():
        contato = Contact.query.first()
        check(contato is not None, "contato foi criado")
        check(contato.email == "gustavo@exemplo.com", "e-mail salvo")
        contato_id = contato.id

    print("3) Tarefas")
    inicio = date.today() - timedelta(days=5)
    resp = client.post(
        "/add",
        data={
            "title": "Montar o cabeçalho do calendário",
            "contact_id": str(contato_id),
            "data_inicio": inicio.isoformat(),
            "duracao": "3",
            "prioridade": "alta",
            "status": "fazendo",
        },
        follow_redirects=True,
    )
    check(resp.status_code == 200, "POST /add responde 200")
    with app.app_context():
        tarefa = Task.query.first()
        check(tarefa is not None, "tarefa foi criada")
        check(tarefa.contact_id == contato_id, "tarefa atribuída ao contato")
        check(
            tarefa.prazo == inicio + timedelta(days=2),
            "prazo = data inicial + duração - 1 (regra do vídeo)",
        )
        check(tarefa.duracao_dias == 3, "duração em dias correta")
        check(
            tarefa.status_atual == "atrasada",
            "status 'atrasada' calculado automaticamente",
        )
        tarefa_id = tarefa.id

    print("4) Visualizações")
    for url in ("/tarefas", "/contatos"):
        check(client.get(url).status_code == 200, f"GET {url} responde 200")

    print("5) Alterar status")
    resp = client.post(
        f"/status/{tarefa_id}", data={"status": "concluida"}, follow_redirects=True
    )
    check(resp.status_code == 200, "POST /status responde 200")
    with app.app_context():
        check(
            db.session.get(Task, tarefa_id).status_atual == "concluida",
            "status salvo como concluída",
        )

    print("6) Editar tarefa")
    resp = client.post(
        f"/editar/{tarefa_id}",
        data={
            "title": "Cabeçalho do calendário (revisado)",
            "contact_id": str(contato_id),
            "data_inicio": inicio.isoformat(),
            "duracao": "2",
            "prioridade": "media",
            "status": "a_fazer",
        },
        follow_redirects=True,
    )
    check(resp.status_code == 200, "POST /editar responde 200")
    with app.app_context():
        tarefa = db.session.get(Task, tarefa_id)
        check("revisado" in tarefa.title, "descrição atualizada")
        check(tarefa.duracao_dias == 2, "duração atualizada")

    print("7) Apagar tarefa")
    resp = client.post(f"/delete/{tarefa_id}", follow_redirects=True)
    check(resp.status_code == 200, "POST /delete responde 200")
    with app.app_context():
        check(Task.query.count() == 0, "tarefa apagada do banco")

    print("\nTodos os testes passaram. ✅")


if __name__ == "__main__":
    main()
