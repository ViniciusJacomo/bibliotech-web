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

# Cria o banco de dados e as tabelas
with app.app_context():
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
    db.create_all()

# --- ROTAS ---

@app.route('/')
def index():
    livros = Livro.query.all()
    leitores = Leitor.query.order_by(Leitor.nome).all()
    emprestimos_ativos = Emprestimo.query.filter_by(data_devolucao=None).all()
    hoje = date.today()
    return render_template('index.html', livros=livros, leitores=leitores, emprestimos=emprestimos_ativos, hoje=hoje)

@app.route('/leitores')
def listar_leitores():
    leitores = Leitor.query.all()
    return render_template('leitores.html', leitores=leitores)

@app.route('/adicionar_leitor', methods=['POST'])
def adicionar_leitor():
    nome = request.form.get('nome')
    documento = request.form.get('documento')
    contato = request.form.get('contato')
    
    novo_leitor = Leitor(nome=nome, documento=documento, contato=contato)
    db.session.add(novo_leitor)
    db.session.commit()
    
    flash('Leitor cadastrado com sucesso!', 'success')
    return redirect(url_for('listar_leitores'))

@app.route('/excluir_leitor/<int:id_leitor>')
def excluir_leitor(id_leitor):
    leitor = Leitor.query.get(id_leitor)
    if leitor:
        if leitor.emprestimos:
            flash(f'Erro: O leitor "{leitor.nome}" possui históricos de empréstimo e não pode ser excluído.', 'danger')
        else:
            db.session.delete(leitor)
            db.session.commit()
            flash(f'Leitor "{leitor.nome}" excluído com sucesso.', 'success')
    return redirect(url_for('listar_leitores'))

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
    leitor_id = request.form.get('leitor_id')
    prazo_str = request.form.get('prazo_devolucao')
    
    if not leitor_id:
        flash('Erro: Selecione um leitor.', 'danger')
        return redirect(url_for('index'))
        
    leitor_id = int(leitor_id)
    leitor = Leitor.query.get(leitor_id)
    
    # Validação 1: O leitor já possui este livro específico em aberto?
    duplicado = Emprestimo.query.filter_by(leitor_id=leitor_id, livro_id=livro_id, data_devolucao=None).first()
    if duplicado:
        flash(f'Erro: {leitor.nome} já possui o livro "{duplicado.livro.nome}" emprestado!', 'danger')
        return redirect(url_for('index'))

    # Validação 2: Limite de 1 livro ativo por leitor
    emprestimo_ativo = Emprestimo.query.filter_by(leitor_id=leitor_id, data_devolucao=None).first()
    if emprestimo_ativo:
        flash(f'Erro: {leitor.nome} já possui um livro emprestado. Devolva-o antes de pegar outro.', 'danger')
        return redirect(url_for('index'))
    
    livro = Livro.query.get(livro_id)
    if livro and livro.quantidade > 0:
        prazo = datetime.strptime(prazo_str, '%Y-%m-%d').date()
        novo_emprestimo = Emprestimo(
            livro_id=livro.id, 
            leitor_id=leitor_id, 
            nome_pessoa=leitor.nome, # Satisfaz a restrição NOT NULL temporariamente
            prazo_devolucao=prazo
        )
        
        livro.quantidade -= 1 
        db.session.add(novo_emprestimo)
        db.session.commit()
        
        flash('Empréstimo realizado com sucesso!', 'success')
    else:
        flash('Erro: Livro indisponível.', 'danger')
        
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
        flash(f'O livro "{livro.nome}" foi excluído.', 'success')
    return redirect(url_for('index'))

@app.route('/estender_prazo/<int:id_emprestimo>', methods=['POST'])
def estender_prazo(id_emprestimo):
    emprestimo = Emprestimo.query.get(id_emprestimo)
    nova_data = request.form.get('nova_data')
    if emprestimo and nova_data:
        emprestimo.prazo_devolucao = datetime.strptime(nova_data, '%Y-%m-%d').date()
        db.session.commit()
        flash('Prazo estendido!', 'success')
    return redirect(url_for('index'))

@app.route('/historico_usuario/<int:leitor_id>')
def historico_usuario(leitor_id):
    leitor = Leitor.query.get_or_404(leitor_id)
    historico = Emprestimo.query.filter_by(leitor_id=leitor_id).order_by(Emprestimo.data_emprestimo.desc()).all()
    return render_template('historico.html', historico=historico, nome=leitor.nome)

if __name__ == '__main__':
    app.run(debug=True)