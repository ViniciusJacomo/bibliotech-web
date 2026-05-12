import os
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "chave_secreta_super_segura"

# Configuração do banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'bibliotech.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS ---

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(50), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    
    emprestimos = db.relationship('Emprestimo', backref='livro', lazy=True, cascade="all, delete-orphan")

class Emprestimo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'), nullable=False)
    nome_pessoa = db.Column(db.String(200), nullable=False)
    data_emprestimo = db.Column(db.Date, nullable=False, default=date.today)
    prazo_devolucao = db.Column(db.Date, nullable=False)
    data_devolucao = db.Column(db.Date, nullable=True)

# Cria o banco de dados e as tabelas
with app.app_context():
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
    db.create_all()

# --- ROTAS ---

@app.route('/')
def index():
    livros = Livro.query.all()
    # Empréstimos ativos (onde data_devolucao é nula)
    emprestimos_ativos = Emprestimo.query.filter_by(data_devolucao=None).all()
    hoje = date.today()
    return render_template('index.html', livros=livros, emprestimos=emprestimos_ativos, hoje=hoje)

@app.route('/adicionar_livro', methods=['POST'])
def adicionar_livro():
    nome = request.form.get('nome')
    autor = request.form.get('autor')
    categoria = request.form.get('categoria')
    isbn = request.form.get('isbn')
    quantidade = int(request.form.get('quantidade'))
    
    novo_livro = Livro(nome=nome, autor=autor, categoria=categoria, isbn=isbn, quantidade=quantidade)
    db.session.add(novo_livro)
    db.session.commit()
    
    flash('Livro cadastrado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/emprestar', methods=['POST'])
def emprestar():
    livro_id = int(request.form.get('livro_id'))
    nome_pessoa = request.form.get('nome_pessoa')
    prazo_str = request.form.get('prazo_devolucao')
    
    livro = Livro.query.get(livro_id)
    
    if livro and livro.quantidade > 0:
        prazo = datetime.strptime(prazo_str, '%Y-%m-%d').date()
        novo_emprestimo = Emprestimo(livro_id=livro.id, nome_pessoa=nome_pessoa, prazo_devolucao=prazo)
        
        livro.quantidade -= 1 
        db.session.add(novo_emprestimo)
        db.session.commit()
        
        flash('Empréstimo realizado com sucesso!', 'success')
    else:
        flash('Erro: Livro indisponível ou em falta no estoque.', 'danger')
        
    return redirect(url_for('index'))

@app.route('/devolver/<int:id_emprestimo>')
def devolver(id_emprestimo):
    emprestimo = Emprestimo.query.get(id_emprestimo)
    
    if emprestimo and not emprestimo.data_devolucao:
        emprestimo.data_devolucao = date.today()
        emprestimo.livro.quantidade += 1
        db.session.commit()
        flash('Livro devolvido com sucesso!', 'success')
        
    return redirect(url_for('index'))

@app.route('/excluir_livro/<int:id_livro>')
def excluir_livro(id_livro):
    livro = Livro.query.get(id_livro)
    
    if livro:
        db.session.delete(livro)
        db.session.commit()
        flash(f'O livro "{livro.nome}" foi excluído do sistema.', 'success')
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
