from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "chave_secreta_super_segura"


lista_livros = []
lista_emprestimos = []


contador_livros = 1
contador_emprestimos = 1

class Livro:
    def __init__(self, id, nome, autor, categoria, isbn, quantidade):
        self.id = id
        self.nome = nome
        self.autor = autor
        self.categoria = categoria
        self.isbn = isbn
        self.quantidade = quantidade

class Emprestimo:
    def __init__(self, id, livro, nome_pessoa, prazo_devolucao):
        self.id = id
        self.livro = livro  # Guarda o objeto Livro inteiro
        self.nome_pessoa = nome_pessoa
        self.data_emprestimo = date.today()
        self.prazo_devolucao = prazo_devolucao
        self.data_devolucao = None

# --- ROTAS ---

@app.route('/')
def index():
    
    emprestimos_ativos = [e for e in lista_emprestimos if e.data_devolucao is None]
    hoje = date.today()
    return render_template('index.html', livros=lista_livros, emprestimos=emprestimos_ativos, hoje=hoje)

@app.route('/adicionar_livro', methods=['POST'])
def adicionar_livro():
    global contador_livros
    
    nome = request.form.get('nome')
    autor = request.form.get('autor')
    categoria = request.form.get('categoria')
    isbn = request.form.get('isbn')
    quantidade = int(request.form.get('quantidade'))
    
    # Cria o livro (arrumar)
    novo_livro = Livro(contador_livros, nome, autor, categoria, isbn, quantidade)
    lista_livros.append(novo_livro)
    contador_livros += 1
    
    flash('Livro cadastrado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/emprestar', methods=['POST'])
def emprestar():
    global contador_emprestimos
    
    livro_id = int(request.form.get('livro_id'))
    nome_pessoa = request.form.get('nome_pessoa')
    prazo_str = request.form.get('prazo_devolucao')
    
   
    livro = next((l for l in lista_livros if l.id == livro_id), None)
    
    if livro and livro.quantidade > 0:
        prazo = datetime.strptime(prazo_str, '%Y-%m-%d').date()
        novo_emprestimo = Emprestimo(contador_emprestimos, livro, nome_pessoa, prazo)
        
        livro.quantidade -= 1 
        lista_emprestimos.append(novo_emprestimo)
        contador_emprestimos += 1
        
        flash('Empréstimo realizado com sucesso!', 'success')
    else:
        flash('Erro: Livro indisponível ou em falta no estoque.', 'danger')
        
    return redirect(url_for('index'))

@app.route('/devolver/<int:id_emprestimo>')
def devolver(id_emprestimo):
    # Busca o empréstimo na lista
    emprestimo = next((e for e in lista_emprestimos if e.id == id_emprestimo), None)
    
    if emprestimo and not emprestimo.data_devolucao:
        emprestimo.data_devolucao = date.today()
        emprestimo.livro.quantidade += 1
        flash('Livro devolvido com sucesso!', 'success')
        
    return redirect(url_for('index'))

@app.route('/excluir_livro/<int:id_livro>')
def excluir_livro(id_livro):
    global lista_livros, lista_emprestimos
    
    # Busca o livro
    livro = next((l for l in lista_livros if l.id == id_livro), None)
    
    if livro:
        # Remove todos os empréstimos ligados a esse livro para não quebrar a tela
        lista_emprestimos = [e for e in lista_emprestimos if e.livro.id != livro.id]
        
        # Remove o livro do estoque
        lista_livros.remove(livro)
        flash(f'O livro "{livro.nome}" foi excluído do sistema.', 'success')
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)