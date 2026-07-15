from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base


db = create_engine("sqlite:///banco.db")

Session = sessionmaker(bind=db)
session = Session() 
Base = declarative_base() # Cria todas as tabelas do banco de dados dentro do db

# Tabelas
class User(Base):

    __tablename__ = "users" 

    # Criando as colunas da tabela
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    login = Column('login', String)
    senha = Column('senha', String)

    # Não é necessário id, pois é autoincrement
    def __init__(self, login, senha):
        self.login = login
        self.senha = senha

class Livro(Base):

    # Define o nome da tabela, é bom utilizar para garantir o nome correto
    __tablename__ = 'livros'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    titulo = Column('titulo', String)
    descricao = Column('descricao', String)
    lido = Column('lido', Boolean)
    deletado = Column('deletado', Boolean)
    genero = Column('genero', String)
    user_id = Column('user_id', ForeignKey('users.id'))

    # Não é necessário id, pois é autoincrement
    def __init__(self, titulo, descricao, user_id, genero, lido=False, deletado=False):
        self.titulo = titulo
        self.descricao = descricao
        self.lido = lido
        self.deletado = deletado
        self.genero = genero
        self.user_id = user_id

class Genero(Base):

    # Define o nome da tabela, é bom utilizar para garantir o nome correto
    __tablename__ = 'generos'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    nome = Column('nome', ForeignKey('livros.genero'))

    # Não é necessário id, pois é autoincrement
    def __init__(self, nome):
        self.nome = nome

Base.metadata.create_all(bind=db)