# Gerenciador de Atividades — Equipe 3 (Atividade 007)

INTEGRANTES DA EQUIPE 3
Disciplina: Fundamentos de Sistemas de Informação.

-----------------------
Gustavo Guarlott
Bruno Bras Barros
Claudio Von Ehnert
========================================================

Aplicação web simples (**Flask + SQLite**) para gerenciar **contatos** (os
responsáveis), **tarefas** (com prazo, prioridade e status) e o **cronograma do
projeto** em um **Diagrama de Gantt**.

Disciplina: Fundamentos de Sistemas de Informação.

---

## ▶ Como rodar (jeito fácil, Windows)

1. **Clique duas vezes em `run.cmd`.**
2. Espere aparecer a mensagem: `Servidor em http://127.0.0.1:5000`.
3. O navegador abre sozinho. Se não abrir, acesse <http://127.0.0.1:5000>.
4. Para parar, volte à janela preta e aperte **Ctrl + C**.

Na primeira vez o script cria o ambiente virtual, instala as dependências e
coloca os dados de exemplo no banco. Depois disso, o próximo clique em
`run.cmd` é quase instantâneo.

### Atalhos do `run.cmd`

| Comando           | O que faz                                              |
|-------------------|--------------------------------------------------------|
| `run.cmd`         | Sobe o sistema normalmente                             |
| `run.cmd -Reset`  | Apaga tudo e recria os dados de exemplo do zero        |
| `run.cmd -Test`   | Roda os testes e sai (não abre o servidor)             |
| `run.cmd -NoSeed` | Sobe sem mexer no banco (usa o que já existe)          |

### Rodando sem o script (qualquer sistema)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
python seed.py                  # dados de exemplo (opcional)
python app.py
```

---

## 🗂 O que é cada arquivo

| Arquivo / pasta        | Para que serve                                                     |
|------------------------|--------------------------------------------------------------------|
| `INICIAR_AQUI.txt`     | Instruções rápidas (é o primeiro arquivo a ser lido).              |
| `app.py`               | O programa: banco, regras do projeto e as páginas. **Leia este.**  |
| `run.cmd` / `run.ps1`  | Ligam tudo automaticamente (ambiente + dependências + servidor).   |
| `seed.py`              | Cria os contatos e as tarefas de exemplo.                          |
| `test_app.py`          | Testes automáticos (funciona sem abrir o navegador).               |
| `requirements.txt`     | As bibliotecas necessárias (Flask e Flask-SQLAlchemy).             |
| `templates/`           | As páginas em HTML (`.html`).                                       |
| `static/style.css`     | O visual do site (cores, layout, aparência do Gantt).              |
| `instance/todo.db`     | Banco de dados SQLite. **É criado sozinho**, não precisa mexer.     |

---

## 🧭 As páginas do sistema

| Rota              | Página                                                        |
|-------------------|---------------------------------------------------------------|
| `/`               | Painel: resumo, cadastro de tarefa e de contato, lista de tarefas |
| `/tarefas`        | Tarefas agrupadas por responsável, com filtros                |
| `/cronograma`     | Diagrama de Gantt do projeto                                  |
| `/contatos`       | Lista de contatos e quantas tarefas cada um tem               |

---

## 📊 Como o cronograma (Gantt) funciona

O gráfico foi feito seguindo o vídeo
[Como Criar Gráfico de Gantt no Planilhas Google](https://www.youtube.com/watch?v=CWn-eieoRpQ).
A lógica é exatamente a mesma de uma planilha:

1. **Estrutura de dados:** cada tarefa tem *Data inicial*, *Duração* e
   *Data final*, onde **Data final = Data inicial + Duração − 1**
   (o dia do início já conta).
2. **Cabeçalho de datas:** mostra só o número do dia (`d`), mas guarda a data
   completa para fazer as contas.
3. **A regra:** um dia é marcado quando está dentro do período da tarefa —
   é o mesmo que `=SE(E(dia >= início; dia <= fim); "OK"; "")`.
4. **A cor:** cada célula marcada recebe a cor do **status** da tarefa, o que
   forma as barras do Gantt.

### Cores por status

| Status    | Cor          |
|-----------|--------------|
| A fazer   | 🔵 azul      |
| Fazendo   | 🟡 amarelo   |
| Concluída | 🟢 verde     |
| Atrasada  | 🔴 vermelho  |

O status **Atrasada** é calculado automaticamente quando o prazo já passou e a
tarefa não foi marcada como concluída.

---

## ✅ O sistema está funcionando?

Rode:

```bash
python test_app.py
```

Ele testa as rotas e as regras principais (prazo = início + duração − 1, status
“atrasada” automático, Gantt, troca de status, edição e remoção) usando um banco
descartável — ou seja, **não estraga os seus dados**.

---

## 🛠 Problemas comuns

| Problema | Solução |
|----------|---------|
| “Python não encontrado” | Instale o Python em <https://python.org> e marque **“Add python.exe to PATH”** na instalação. |
| O site abre em branco ou com dados estranhos | Rode `run.cmd -Reset` para recriar os dados de exemplo. |
| A porta 5000 está em uso | Feche o outro programa que está usando a porta ou reinicie o computador. |
| Quero começar do zero | Apague a pasta `instance/` e rode `run.cmd -Reset`. |
