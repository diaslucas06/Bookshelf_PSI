from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

class Usuario(UserMixin):
    def __init__(self, nome, senha, hash = False, id = None):
        self.id = id
        self.nome = nome

        if hash:
            self.senha = senha
        else:
            self.senha = generate_password_hash(senha)

    def pegar_id(self):
        return str(self.id)
    
    @classmethod
    def encontrar_usuario(clas, user_id):
        # Precisa abrir a conexão com o banco e pegar os dados do usuário via id
        pass