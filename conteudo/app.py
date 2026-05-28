from flask import Flask, request, url_for, redirect, render_template, session, flash
from .db import conectar_banco, iniciar_banco # funções do banco estão em outro arquivo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_segredo'

iniciar_banco()

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
    titulo = request.form.get('titulo')
    genero = request.form.get('genero')
    descricao = request.form.get('descricao')

    conexao = conectar_banco()
    cursor = conexao.cursor()

    resultado = cursor.execute("SELECT * FROM livros WHERE titulo = ?", (titulo,))
    book = resultado.fetchone()

    user = session['id']

    if not book:
           
        cursor.execute("INSERT INTO livros(titulo, genero, descricao, usuario_id) VALUES (?,?,?,?)", (titulo, genero, descricao, user))
        resultado = cursor.execute("SELECT * FROM generos WHERE nome = ?", (genero,))
        genero_existe = resultado.fetchone()
        if not genero_existe:
            cursor.execute("INSERT INTO generos(nome) VALUES (?)", (genero,))
        conexao.commit()
        conexao.close()

        return redirect(url_for('livros_cadastrados'))
    
    conexao.close()
    flash('livro existente')
    return redirect(url_for('livros_cadastrados'))


@app.route('/livros-cadastrados')
def livros_cadastrados():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conexao = conectar_banco()
    cursor = conexao.cursor()

    resultado = cursor.execute("SELECT * FROM livros WHERE usuario_id = ?", (session['id'],))
    livros_db = resultado.fetchall()
   
    return render_template('livros_cadastrados.html', livros = livros_db)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    session.pop('id', None)
    return redirect(url_for('index'))


@app.route('/excluir-livro/<int:id_livro>' , methods=['POST'])
def excluir_livro(id_livro):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("DELETE FROM livros WHERE id = ?", (id_livro,))

    conexao.commit()
    conexao.close()
    return redirect(url_for('livros_cadastrados'))


@app.route('/editar-livro/<int:id_livro>', methods=['GET', 'POST'])
def editar_livro(id_livro):

    if 'user' not in session:
        return redirect(url_for('login'))
    
    conexao = conectar_banco()
    cursor = conexao.cursor()

    if request.method == 'GET':
        resultado = cursor.execute("SELECT * FROM livros WHERE id = ?", (id_livro,))
        livro = resultado.fetchone()

        conexao.commit()
        conexao.close()

        if livro:
            return render_template('editar_livro.html', livro=livro)
        
        flash("Livro não encontrado.")
        return redirect(url_for('livros_cadastrados'))

    titulo = request.form.get('titulo')
    genero = request.form.get('genero')
    descricao = request.form.get('descricao')
    lido = request.form.get('lido') == 'on'
    
    conexao.execute("UPDATE livros SET titulo = ?, genero = ?, descricao = ?, lido = ? WHERE id = ?", (titulo, genero, descricao, lido, id_livro))
    
    conexao.commit()
    conexao.close()

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
   

