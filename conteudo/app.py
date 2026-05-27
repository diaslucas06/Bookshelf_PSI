from flask import Flask, request, url_for, redirect, render_template, session, flash
import sqlite3
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_segredo'


livros = []


dir = os.path.dirname(os.path.abspath(__file__))
db = os.path.join (dir, "banco.db")


def conectar_banco():
    conexao = sqlite3.connect(db)
    conexao.row_factory = sqlite3.Row
    return conexao


def iniciar_banco():
    conexao = conectar_banco()
    cursor = conexao.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario VARCHAR NOT NULL,
        senha VARCHAR NOT NULL          
    );              
                                 
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS livros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,        
        titulo VARCHAR NOT NULL,
        genero VARCHAR,
        descricao VARCHAR,
        lido INTEGER,
        usuario_id INTEGER          
    );                          
    """)
    conexao.commit()
    conexao.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    if 'user' in session:
        return redirect(url_for('cadastro_livros'))
   
    if request.method == 'POST':
        login = request.form.get('login')
        senha = request.form.get('senha')


        conexao = conectar_banco()
        cursor = conexao.cursor()


        resultado = cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (login,))
        user = resultado.fetchone()


        if not user:
           
            cursor.execute("INSERT INTO usuarios(usuario, senha) VALUES (?,?)", (login, senha))
            conexao.commit()
            conexao.close()


            return redirect(url_for('login'))
       
        else:
            conexao.close()
            flash('usuário existente')
            return redirect(url_for('cadastro'))


    return render_template('cadastro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():


    if 'user' in session:
        return redirect(url_for('cadastro_livros'))
       
   
    if request.method == 'POST':
        login = request.form.get('login')
        senha = request.form.get('senha')


        conexao = conectar_banco()
        cursor = conexao.cursor()


        resultado = cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (login,))
        user = resultado.fetchone()
        conexao.close()


        if user and user['usuario'] == login and user['senha'] == senha:
            session['user'] = login
            session['id'] = user['id']
            return redirect(url_for('cadastro_livros'))
        else:
            flash('usuário ou senha incorreto(s)', 'error')
            return redirect(url_for('login'))
 
    return render_template('login.html')


@app.route('/cadastro_livros')
def cadastro_livros():
    if 'user' not in session:
        return redirect(url_for('login'))
   
    return render_template('cadastro_livros.html')


@app.route('/adicionar-livro', methods=['POST'])
def adicionar_livro():
    global livros
    livro = {
        "titulo": request.form.get('titulo'),
        "genero": request.form.get('genero'),
        "descricao": request.form.get('descricao'),
        "lido": False
    }
    livros.append(livro)
    return redirect(url_for('livros_cadastrados'))


@app.route('/livros-cadastrados')
def livros_cadastrados():
    if 'user' not in session:
        return redirect(url_for('login'))
   
    return render_template('livros_cadastrados.html', livros = livros)


@app.route('/logout', methods=['POST'])
def logout():
    global livros
    session.pop('user', None)
    session.pop('id', None)
    livros = [] # ?
    return redirect(url_for('index'))


@app.route('/excluir-livro/<int:indice>' , methods=['POST'])
def excluir_livro(indice):
    global livros
    if 0 <= indice < len(livros):
        livros.pop(indice)
    return redirect(url_for('livros_cadastrados'))


@app.route('/editar-livro/<int:indice>', methods=['GET', 'POST'])
def editar_livro(indice):
    global livros
    if 'user' not in session:
        return redirect(url_for('login'))
   
    if request.method == 'GET':
        if 0 <= indice < len(livros):
            livro = livros[indice]
            return render_template('editar_livro.html', livro=livro, indice=indice)
        return redirect(url_for('livros_cadastrados'))


    if 0 <= indice < len(livros):
        livros[indice] = {
            "titulo": request.form.get('titulo'),
            "genero": request.form.get('genero'),
            "descricao": request.form.get('descricao'),
            "lido": request.form.get('lido') == 'on'
        }
    return redirect(url_for('livros_cadastrados'))


@app.errorhandler(400)
def error400(error):
    return render_template('errors/error400.html'), 400


@app.errorhandler(401)
def error401(error):
    return render_template('errors/error401.html'), 401


@app.errorhandler(403)
def error403(error):
    return render_template('errors/error403.html'), 403


@app.errorhandler(404)
def error404(error):
    return render_template('errors/error404.html'), 404


iniciar_banco()
if __name__ == '__main__':
    app.run(debug=True)
   

