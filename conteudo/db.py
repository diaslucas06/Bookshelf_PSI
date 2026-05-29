import sqlite3

def conectar_banco():
    conexao = sqlite3.connect('banco.db')
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
            lido BOOLEAN DEFAULT FALSE,
            deletado BOOLEAN DEFAULT FALSE,
            usuario_id INTEGER,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)          
        );                          
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,        
            nome VARCHAR NOT NULL,   
            FOREIGN KEY (nome) REFERENCES livros(genero)      
        );                          
    """)

    conexao.commit()
    conexao.close()