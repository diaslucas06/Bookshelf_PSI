from flask import Flask, request, url_for, redirect, render_template, flash
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .db import User, Livro, Genero, db, session
from .models.usuario import Usuario

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_segredo'

db

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(int(user_id))

# ---------------------------------------------------------------------------------------


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
   
    if request.method == 'POST':
        login = request.form.get('login')
        senha = request.form.get('senha')

        hash = generate_password_hash(senha)

        user = session.query(User).filter_by(login=login).first() 

        if not user:
            usuario_novo = User(login=login, senha=hash)
            session.add(usuario_novo)
            session.commit()
            return redirect(url_for('login'))
        else:
            flash('usuário existente')
            return redirect(url_for('cadastro'))


    return render_template('cadastro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
       
    if request.method == 'POST':
        login = request.form.get('login')
        senha = request.form.get('senha')

        user = session.query(User).filter_by(login=login).first() 
        if user and check_password_hash(user.senha, senha):
            login_user(user) 
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
    
    titulo = request.form.get('titulo')
    genero = request.form.get('genero')
    descricao = request.form.get('descricao')

    id_usuario_atual = current_user.id
    
    book = session.query(Livro).filter_by(titulo=titulo, user_id=id_usuario_atual).first()

    if not book:
           
        n_livro = Livro(titulo=titulo, descricao=descricao, user_id=id_usuario_atual, genero=genero)
        session.add(n_livro)

        genero_existe = session.query(Genero).filter_by(nome=genero).first()
        if not genero_existe:
            n_genero = Genero(nome=genero)
            session.add(n_genero)

        session.commit()
        return redirect(url_for('livros_cadastrados'))
    
   
    flash('livro existente')
    return redirect(url_for('livros_cadastrados'))


@app.route('/livros-cadastrados')
@login_required
def livros_cadastrados():
    
    filtro_status = request.args.get('status', default='todos')
    filtro_genero = request.args.get('genero', default='todos')
    
    generos_db = session.query(Genero).all()

    query = session.query(Livro).filter(Livro.user_id == current_user.id, Livro.deletado != True)
    
    if filtro_genero != 'todos':
        query = query.filter(Livro.genero == filtro_genero)
   
    if filtro_status == 'lidos':
        query = query.filter(Livro.lido == True)
    elif filtro_status == 'nao_lido':
        query = query.filter(Livro.lido != True)

    livros_db = query.all()
   
    return render_template( 'livros_cadastrados.html', livros=livros_db, filtro_atual=filtro_status, generos=generos_db, genero_atual=filtro_genero)


@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    flash("Logout realizado com sucesso.", "success")
    return redirect(url_for('index'))


@app.route('/excluir-livro/<int:id_livro>' , methods=['POST'])
def excluir_livro(id_livro):
    livro = session.query(Livro).filter_by(id=id_livro, user_id=current_user.id).first()

    if livro:
        livro.deletado = True
        session.commit()

    return redirect(url_for('livros_cadastrados'))


@app.route('/editar-livro/<int:id_livro>', methods=['GET', 'POST'])
@login_required
def editar_livro(id_livro):
    
    livro = session.query(Livro).filter_by(id=id_livro, user_id=current_user.id).first()

    if request.method == 'GET':
          return render_template('editar_livro.html', livro=livro)

    if not livro:
          
        flash("Livro não encontrado.")
        return redirect(url_for('livros_cadastrados'))

    livro.titulo = request.form.get('titulo')
    livro.genero = request.form.get('genero')
    livro.descricao = request.form.get('descricao')
    livro.lido = request.form.get('lido') == 'on'
    
    session.commit()

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
   

