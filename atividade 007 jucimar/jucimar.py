from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# ==============================================================================
# 1. INICIALIZAÇÃO DA APLICAÇÃO E CONFIGURAÇÕES
# ==============================================================================
# Instanciamos a aplicação Flask. A variável 'app' é o núcleo do servidor Web.
app = Flask(__name__)

# Define a URI de conexão. Aqui usamos o SQLite, um banco de dados relacional baseado em arquivo (.db).
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projeto.db'
# Desativa a notificação de modificações do SQLAlchemy para economizar recursos de memória.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Instancia o SQLAlchemy associando-o à nossa aplicação Flask (ORM - Object-Relational Mapping).
db = SQLAlchemy(app)


# ==============================================================================
# 2. CONCEITOS DE ORIENTAÇÃO A OBJETOS (POO) E MODELAGEM DE DADOS (ORM)
# ==============================================================================
# Em vez de escrever consultas SQL manuais (Ex: "CREATE TABLE..."), usamos POO.
# Cada classe que herda de 'db.Model' representa uma TABELA no Banco de Dados.
# Cada instância dessa classe (objeto) representará uma LINHA dessa tabela.

class Contato(db.Model):
    # Definimos os Atributos da Classe, que o ORM mapeia como Colunas no Banco de Dados.
    id = db.Column(db.Integer, primary_key=True)  # Chave primária autoincrementada
    nome = db.Column(db.String(100), nullable=False)  # Não permite valores nulos
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)  # Campo opcional

    # RELACIONAMENTO (POO + SQL):
    # O 'db.relationship' não cria uma coluna física no banco de dados.
    # Ele cria uma propriedade conceitual no Python para acessar objetos vinculados.
    # - 'backref="contato"': Adiciona uma propriedade inversa no objeto Tarefa (tarefa.contato).
    # - 'lazy=True': Carrega os dados do relacionamento apenas quando forem acessados.
    # - 'cascade="all, delete-orphan"': Se um Contato for deletado, suas Tarefas vinculadas também serão apagadas automaticamente (Integridade Referencial).
    tarefas = db.relationship('Tarefa', backref='contato', lazy=True, cascade='all, delete-orphan')


class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    prazo = db.Column(db.String(20), nullable=False)
    prioridade = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='a_fazer')

    # CHAVE ESTRANGEIRA (Foreign Key):
    # Conecta esta tabela à tabela 'contato'. O parâmetro usa o nome da TABELA no BD ('contato.id'),
    # que por padrão é o nome da classe em minúsculo.
    contato_id = db.Column(db.Integer, db.ForeignKey('contato.id'), nullable=False)


class Cronograma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fase = db.Column(db.String(100), nullable=False)
    data_inicio = db.Column(db.String(20), nullable=False)
    data_fim = db.Column(db.String(20), nullable=False)
    # Chave estrangeira opcional (nullable=True), indicando que nem todo cronograma precisa ter uma tarefa atrelada.
    tarefa_id = db.Column(db.Integer, db.ForeignKey('tarefa.id'), nullable=True)
    responsavel = db.Column(db.String(100), nullable=True)


# Cria fisicamente no banco de dados todas as tabelas mapeadas pelas classes herdadas de db.Model.
with app.app_context():
    db.create_all()


# ==============================================================================
# 3. ROTAS DE APLICAÇÃO E CONTROLADORES (HTTP & FLASK)
# ==============================================================================
# Rotas definem o comportamento da aplicação quando um usuário acessa uma determinada URL.
# Utilizamos o decorador '@app.route()' sobre funções do Python para associar
# o endereço da URL à lógica de processamento.

@app.route('/')
def index():
    """
    Rota Raiz ('/').
    Por padrão, escuta apenas requisições do tipo GET.
    Seu papel aqui é fazer um redirecionamento para a rota principal do sistema.
    """
    return redirect(url_for('listar_tarefas'))


@app.route('/tarefas')
def listar_tarefas():
    """
    Rota de Leitura/Consulta (GET).
    Acessa o Banco de Dados através das classes (Tarefas.query / Contato.query),
    recupera as listas de objetos e injeta esses objetos no HTML via Jinja2 (render_template).
    """
    # POO na prática: Tarefa.query.all() retorna uma lista de Objetos da classe Tarefa.
    tarefas = Tarefa.query.all()
    contatos = Contato.query.all()

    # Injeta os objetos Python dentro do template 'tarefas.html'
    return render_template('tarefas.html', tarefas=tarefas, contatos=contatos)


@app.route('/tarefas/criar', methods=['POST'])
def criar_tarefa():
    """
    Rota de Escrita/Criação (POST).
    Recebe os dados submetidos por um formulário HTML através do 'request.form'.
    Instancia um novo Objeto Python (POO) e persiste no banco via SQLAlchemy (db.session).
    """
    # 1. Captura os dados enviados via formulário HTTP
    descricao = request.form['descricao']
    prazo = request.form['prazo']
    prioridade = request.form['prioridade']
    status = request.form['status']
    contato_id = request.form['contato_id']

    # 2. Instanciação de Objeto (POO):
    # Cria uma nova instância da classe 'Tarefa' com os atributos recebidos.
    nova = Tarefa(
        descricao=descricao,
        prazo=prazo,
        prioridade=prioridade,
        status=status,
        contato_id=contato_id
    )

    # 3. Persistência no Banco de Dados:
    # 'add' prepara o objeto para o banco; 'commit' efetiva a transação.
    db.session.add(nova)
    db.session.commit()

    # Redireciona o usuário de volta para a listagem para atualizar a visualização.
    return redirect(url_for('listar_tarefas'))