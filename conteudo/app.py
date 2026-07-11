from flask import Flask, request, url_for, redirect, render_template, session, flash
from flask_login import LoginManager, login_required, logout_user, login_user
from werkzeug.security import check_password_hash, generate_password_hash
from .db import conectar_banco, iniciar_banco # funções do banco estão em outro arquivo
from .models.usuario import Usuario


app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_segredo'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.encontrar_usuario(user_id)

iniciar_banco()


# ---------------------------------------------------------------------------------------


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
   
    if request.method == 'POST':
        login = request.form.get('login')
        senha = request.form.get('senha')

        conexao = conectar_banco()
        cursor = conexao.cursor()

        hash = generate_password_hash(senha)

        resultado = cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (login,))
        user = resultado.fetchone()

        if not user:
            cursor.execute("INSERT INTO usuarios(usuario, senha) VALUES (?,?)", (login, hash))
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
       
    if request.method == 'POST':
        login = request.form.get('login')
        senha = request.form.get('senha')

        conexao = conectar_banco()
        cursor = conexao.cursor()

        resultado = cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (login,))
        user = resultado.fetchone()
        conexao.close()

        if user and check_password_hash(user['senha'], senha):
            usuario = Usuario(nome=resultado['nome'], senha=user['senha'])
            login_user(usuario)
            return redirect(url_for('cadastro_livros'))
        else:
            flash('usuário ou senha incorreto(s)', 'error')
            return redirect(url_for('login'))
 
    return render_template('login.html')


@app.route('/cadastro_livros')
@login_required
def cadastro_livros():
    return render_template('cadastro_livros.html')


@app.route('/adicionar-livro', methods=['POST'])
@login_required
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
@login_required
def livros_cadastrados():
    
    filtro_status = request.args.get('status', default='todos')
    filtro_genero = request.args.get('genero', default='todos')
    
    conexao = conectar_banco()
    cursor = conexao.cursor()

    resultado_generos = cursor.execute("SELECT * FROM generos")
    generos_db = resultado_generos.fetchall()

    if filtro_genero != 'todos':
        resultado = cursor.execute("SELECT * FROM livros WHERE usuario_id = ? AND genero = ?", (session['id'], filtro_genero))
    else:
        resultado = cursor.execute("SELECT * FROM livros WHERE usuario_id = ?", (session['id'],))
        
    livros_db = resultado.fetchall()
    conexao.close()
   
    return render_template( 'livros_cadastrados.html', livros=livros_db, filtro_atual=filtro_status, generos=generos_db, genero_atual=filtro_genero)


@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    flash("Logout realizado com sucesso.", "success")
    return redirect(url_for('index'))


@app.route('/excluir-livro/<int:id_livro>' , methods=['POST'])
def excluir_livro(id_livro):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("UPDATE livros SET deletado = TRUE WHERE id = ?", (id_livro,)) # não exclui do banco, somente não irá mais aparecer para o usuário

    conexao.commit()
    conexao.close()
    return redirect(url_for('livros_cadastrados'))


@app.route('/editar-livro/<int:id_livro>', methods=['GET', 'POST'])
@login_required
def editar_livro(id_livro):
    
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

if __name__ == '__main__':
    app.run(debug=True)
   

