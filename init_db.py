"""
init_db.py — Criação/atualização do banco de dados do sistema
Gestão de Condomínios (Streamlit + PostgreSQL)

Uso:
    python init_db.py

O script é idempotente: pode ser executado quantas vezes for necessário,
pois todas as tabelas usam IF NOT EXISTS e os dados semeados checam existência.
"""

import os
import hashlib

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "condominios"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )

# ============================================================
# 1) CRIAÇÃO DAS TABELAS
# ============================================================

TABELAS = [
    """
    CREATE TABLE IF NOT EXISTS condominios (
        id          SERIAL PRIMARY KEY,
        nome        TEXT NOT NULL,
        cnpj        TEXT,
        endereco    TEXT,
        cidade      TEXT,
        uf          TEXT,
        email       TEXT,
        senha_email TEXT,
        criado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id            SERIAL PRIMARY KEY,
        usuario       TEXT UNIQUE NOT NULL,
        senha         TEXT NOT NULL,
        nome          TEXT NOT NULL,
        perfil        TEXT DEFAULT 'operador',
        condominio_id INTEGER REFERENCES condominios(id) ON DELETE SET NULL,
        ativo         BOOLEAN DEFAULT TRUE,
        criado_em     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS apartamentos (
        id            SERIAL PRIMARY KEY,
        condominio_id INTEGER NOT NULL REFERENCES condominios(id) ON DELETE CASCADE,
        numero        TEXT NOT NULL,
        bloco         TEXT,
        proprietario  TEXT,
        telefone      TEXT,
        email         TEXT,
        criado_em     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS moradores (
        id             SERIAL PRIMARY KEY,
        apartamento_id INTEGER NOT NULL REFERENCES apartamentos(id) ON DELETE CASCADE,
        nome           TEXT NOT NULL,
        parentesco     TEXT,
        telefone       TEXT,
        email          TEXT,
        is_principal   BOOLEAN DEFAULT FALSE,
        criado_em      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS veiculos (
        id             SERIAL PRIMARY KEY,
        apartamento_id INTEGER NOT NULL REFERENCES apartamentos(id) ON DELETE CASCADE,
        tipo           TEXT,
        marca          TEXT,
        modelo         TEXT,
        placa          TEXT,
        cor            TEXT,
        ano            INTEGER,
        criado_em      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS pets (
        id             SERIAL PRIMARY KEY,
        apartamento_id INTEGER NOT NULL REFERENCES apartamentos(id) ON DELETE CASCADE,
        tipo           TEXT,
        raca           TEXT,
        porte          TEXT,
        observacao     TEXT,
        criado_em      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS empregadas (
        id             SERIAL PRIMARY KEY,
        condominio_id  INTEGER NOT NULL REFERENCES condominios(id) ON DELETE CASCADE,
        apartamento_id INTEGER REFERENCES apartamentos(id) ON DELETE SET NULL,
        nome           TEXT NOT NULL,
        cpf            TEXT UNIQUE,
        telefone       TEXT,
        endereco       TEXT,
        criado_em      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS categorias (
        id            SERIAL PRIMARY KEY,
        condominio_id INTEGER NOT NULL REFERENCES condominios(id) ON DELETE CASCADE,
        tipo          TEXT NOT NULL,
        nome          TEXT NOT NULL,
        UNIQUE (condominio_id, tipo, nome)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS lancamentos (
        id              SERIAL PRIMARY KEY,
        condominio_id   INTEGER NOT NULL REFERENCES condominios(id) ON DELETE CASCADE,
        apartamento_id  INTEGER REFERENCES apartamentos(id) ON DELETE SET NULL,
        tipo            TEXT NOT NULL,
        categoria       TEXT NOT NULL,
        descricao       TEXT,
        valor           NUMERIC(12,2) NOT NULL,
        data_lancamento DATE NOT NULL,
        criado_em       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS saldos_iniciais (
        id            SERIAL PRIMARY KEY,
        condominio_id INTEGER NOT NULL REFERENCES condominios(id) ON DELETE CASCADE,
        mes           INTEGER NOT NULL,
        ano           INTEGER NOT NULL,
        valor         NUMERIC(12,2) NOT NULL DEFAULT 0,
        atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (condominio_id, mes, ano)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS contas_bancarias (
        id            SERIAL PRIMARY KEY,
        condominio_id INTEGER NOT NULL REFERENCES condominios(id) ON DELETE CASCADE,
        tipo          TEXT NOT NULL,
        banco         TEXT NOT NULL,
        agencia       TEXT,
        numero_conta  TEXT,
        saldo         NUMERIC(12,2) DEFAULT 0,
        atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS distribuicao_contas (
        id            SERIAL PRIMARY KEY,
        condominio_id INTEGER NOT NULL REFERENCES condominios(id) ON DELETE CASCADE,
        mes           INTEGER NOT NULL,
        ano           INTEGER NOT NULL,
        conta_id      INTEGER NOT NULL REFERENCES contas_bancarias(id) ON DELETE CASCADE,
        valor         NUMERIC(12,2) NOT NULL DEFAULT 0,
        UNIQUE (condominio_id, mes, ano, conta_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS auditoria (
        id            SERIAL PRIMARY KEY,
        usuario_id    INTEGER,
        usuario_nome  TEXT,
        tabela        TEXT NOT NULL,
        registro_id   INTEGER,
        acao          TEXT NOT NULL,
        detalhes      TEXT,
        data_hora     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
]

# ============================================================
# 2) FUNÇÕES AUXILIARES
# ============================================================

def criar_tabelas(cur):
    """Cria todas as tabelas (idempotente)."""
    for ddl in TABELAS:
        cur.execute(ddl)
    print(f"✅ {len(TABELAS)} tabelas verificadas/criadas.")

def conceder_privilegios(cur):
    """Concede privilégios ao usuário atualmente conectado no banco."""
    cur.execute("SELECT current_user")
    usuario = cur.fetchone()[0]
    cur.execute(sql.SQL("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {}")
                .format(sql.Identifier(usuario)))
    cur.execute(sql.SQL("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {}")
                .format(sql.Identifier(usuario)))
    print(f"✅ Privilégios (tabelas + sequências) concedidos ao usuário '{usuario}'.")

def criar_master(cur):
    """Cria o usuário master inicial, se ainda não existir (senha em SHA-256)."""
    cur.execute("SELECT COUNT(*) FROM usuarios WHERE perfil = 'master'")
    if cur.fetchone()[0] == 0:
        senha_master = os.getenv("MASTER_SENHA", "admin123")
        if len(senha_master) < 6:
            print("❌ A senha do master deve ter pelo menos 6 caracteres.")
            print("   Defina MASTER_SENHA no arquivo .env com uma senha válida e rode novamente.")
            return
        senha_hash = hashlib.sha256(senha_master.encode()).hexdigest()
        cur.execute(
            "INSERT INTO usuarios (usuario, senha, nome, perfil, ativo) "
            "VALUES (%s, %s, %s, 'master', TRUE)",
            ("admin", senha_hash, "Administrador Master"),
        )
        if senha_master == "admin123":
            print("✅ Usuário master criado:  usuário 'admin' / senha 'admin123'")
            print("   ⚠️  TROQUE A SENHA IMEDIATAMENTE no módulo Usuários após o 1º login!")
        else:
            print("✅ Usuário master criado:  usuário 'admin' com senha definida via MASTER_SENHA.")
    else:
        print("ℹ️  Já existe usuário master — nada a fazer.")

def semear_categorias(cur):
    """Garante as categorias padrão de receita para cada condomínio existente."""
    cur.execute("SELECT id FROM condominios ORDER BY id")
    condominios = [r[0] for r in cur.fetchall()]
    if not condominios:
        print("ℹ️  Nenhum condomínio cadastrado — categorias padrão serão criadas "
              "quando o primeiro condomínio for adicionado pelo app.")
        return
    criadas = 0
    for cid in condominios:
        for nome in ("Taxa de condomínio", "Taxa de garagem"):
            cur.execute(
                "SELECT COUNT(*) FROM categorias "
                "WHERE condominio_id = %s AND tipo = 'receita' AND nome = %s",
                (cid, nome),
            )
            if cur.fetchone()[0] == 0:
                cur.execute(
                    "INSERT INTO categorias (condominio_id, tipo, nome) "
                    "VALUES (%s, 'receita', %s)",
                    (cid, nome),
                )
                criadas += 1
    print(f"✅ Categorias padrão verificadas em {len(condominios)} condomínio(s) "
          f"({criadas} criada(s)).")

# ============================================================
# 3) EXECUÇÃO PRINCIPAL
# ============================================================

def main():
    conn = get_connection()
    cur = conn.cursor()
    try:
        criar_tabelas(cur)
        conceder_privilegios(cur)
        criar_master(cur)
        semear_categorias(cur)
        conn.commit()
        print("\n🎉 Banco de dados inicializado/atualizado com sucesso!")
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erro durante a inicialização: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()