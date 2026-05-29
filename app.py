import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "chave_secreta_super_segura"

# Configuração do banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'bibliotech.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DECORADOR PARA PROTEÇÃO DE ROTAS ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'livraria_nome' not in session:
            flash('Por favor, faça login para acessar.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- MODELOS ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_livraria = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(50), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    emprestimos = db.relationship('Emprestimo', backref='livro', lazy=True, cascade="all, delete-orphan")

class Leitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    documento = db.Column(db.String(50), nullable=True)
    contato = db.Column(db.String(100), nullable=True)
    emprestimos = db.relationship('Emprestimo', backref='leitor', lazy=True)

class Emprestimo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'), nullable=False)
    leitor_id = db.Column(db.Integer, db.ForeignKey('leitor.id'), nullable=True)
    nome_pessoa = db.Column(db.String(200), nullable=True)
    data_emprestimo = db.Column(db.Date, nullable=False, default=date.today)
    prazo_devolucao = db.Column(db.Date, nullable=False)
    data_devolucao = db.Column(db.Date, nullable=True)

with app.app_context():
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
    db.create_all()

# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            session['livraria_nome'] = usuario.nome_livraria
            return redirect(url_for('index'))
        flash('Email ou senha inválidos!', 'danger')
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome_livraria')
        email = request.form.get('email')
        senha = generate_password_hash(request.form.get('senha'))
        novo_usuario = Usuario(nome_livraria=nome, email=email, senha=senha)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/logout')
def logout():
    session.pop('livraria_nome', None)
    return redirect(url_for('login'))

# --- ROTAS PRINCIPAIS ---
@app.route('/')
@login_required
def index():
    livros = Livro.query.all()
    leitores = Leitor.query.order_by(Leitor.nome).all()
    emprestimos = Emprestimo.query.filter_by(data_devolucao=None).all()
    return render_template('index.html', livros=livros, leitores=leitores, emprestimos=emprestimos, hoje=date.today())

@app.route('/leitores')
@login_required
def listar_leitores():
    return render_template('leitores.html', leitores=Leitor.query.all())

@app.route('/adicionar_leitor', methods=['POST'])
@login_required
def adicionar_leitor():
    db.session.add(Leitor(nome=request.form.get('nome'), documento=request.form.get('documento'), contato=request.form.get('contato')))
    db.session.commit()
    return redirect(url_for('listar_leitores'))

@app.route('/excluir_leitor/<int:id_leitor>')
@login_required
def excluir_leitor(id_leitor):
    leitor = Leitor.query.get(id_leitor)
    if leitor:
        db.session.delete(leitor)
        db.session.commit()
    return redirect(url_for('listar_leitores'))

@app.route('/adicionar_livro', methods=['POST'])
@login_required
def adicionar_livro():
    db.session.add(Livro(nome=request.form.get('nome'), autor=request.form.get('autor'), categoria=request.form.get('categoria'), isbn=request.form.get('isbn'), quantidade=int(request.form.get('quantidade'))))
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/excluir_livro/<int:id_livro>')
@login_required
def excluir_livro(id_livro):
    livro = Livro.query.get(id_livro)
    if livro:
        db.session.delete(livro)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/emprestar', methods=['POST'])
@login_required
def emprestar():
    livro = Livro.query.get(int(request.form.get('livro_id')))
    leitor = Leitor.query.get(int(request.form.get('leitor_id')))
    if livro and livro.quantidade > 0:
        db.session.add(Emprestimo(livro_id=livro.id, leitor_id=leitor.id, nome_pessoa=leitor.nome, prazo_devolucao=datetime.strptime(request.form.get('prazo_devolucao'), '%Y-%m-%d').date()))
        livro.quantidade -= 1
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/devolver/<int:id_emprestimo>')
@login_required
def devolver(id_emprestimo):
    emp = Emprestimo.query.get(id_emprestimo)
    if emp:
        emp.data_devolucao = date.today()
        emp.livro.quantidade += 1
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/estender_prazo/<int:id_emprestimo>', methods=['POST'])
@login_required
def estender_prazo(id_emprestimo):
    emp = Emprestimo.query.get_or_404(id_emprestimo)
    emp.prazo_devolucao = datetime.strptime(request.form.get('nova_data'), '%Y-%m-%d').date()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/historico_usuario/<int:leitor_id>')
@login_required
def historico_usuario(leitor_id):
    leitor = Leitor.query.get_or_404(leitor_id)
    return render_template('historico.html', historico=leitor.emprestimos, nome=leitor.nome)

if __name__ == '__main__':
    app.run(debug=True)