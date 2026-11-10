"""Conexão com o PostgreSQL (psycopg 3).

Cada requisição HTTP abre UMA conexão na primeira consulta e a fecha ao final
(confirmando a transação se tudo deu certo, ou desfazendo se houve erro).
"""
from pathlib import Path

import click
import psycopg
from flask import current_app, g
from psycopg.rows import dict_row

PASTA_SQL = Path(__file__).resolve().parent.parent / "database"


def get_db():
    """Devolve a conexão da requisição atual (cria se ainda não existir)."""
    if "db" not in g:
        g.db = psycopg.connect(current_app.config["DATABASE_URL"], row_factory=dict_row)
    return g.db


def close_db(erro=None):
    conexao = g.pop("db", None)
    if conexao is not None:
        if erro is None:
            conexao.commit()
        else:
            conexao.rollback()
        conexao.close()


def consultar(sql, params=None):
    """Executa um SELECT e devolve uma lista de dicionários.
    Sempre use %s nos parâmetros: o psycopg escapa os valores e evita SQL Injection (RNF05)."""
    return get_db().execute(sql, params).fetchall()


def consultar_um(sql, params=None):
    linhas = consultar(sql, params)
    return linhas[0] if linhas else None


def criar_banco_se_nao_existir(url):
    """Cria o banco informado na URL, se ainda não existir (em UTF-8, para os acentos).
    Conecta no banco padrão 'postgres' do servidor para isso. Devolve True se criou."""
    from psycopg.conninfo import conninfo_to_dict, make_conninfo

    try:  # o banco já existe? (no Render ele é criado pela plataforma)
        psycopg.connect(url).close()
        return False
    except psycopg.OperationalError as erro:
        if "does not exist" not in str(erro) and "não existe" not in str(erro):
            raise
    nome = conninfo_to_dict(url).get("dbname")
    if not nome or not nome.replace("_", "").isalnum():
        raise click.ClickException(f"Nome de banco inválido na URL: {nome!r} (use letras, números e _).")
    with psycopg.connect(make_conninfo(url, dbname="postgres"), autocommit=True) as conexao:
        existe = conexao.execute("SELECT 1 FROM pg_database WHERE datname = %s", (nome,)).fetchone()
        if existe:
            return False
        conexao.execute(f'CREATE DATABASE "{nome}" ENCODING \'UTF8\' TEMPLATE template0')
        return True


def executar_scripts(url, *arquivos):
    """Roda arquivos .sql inteiros (usado pelo comando init-db e pelos testes)."""
    with psycopg.connect(url, autocommit=True) as conexao:
        for arquivo in arquivos:
            conexao.execute((PASTA_SQL / arquivo).read_text(encoding="utf-8"))


def tabelas_existem(url):
    with psycopg.connect(url) as conexao:
        return conexao.execute("SELECT to_regclass('public.usuario') IS NOT NULL").fetchone()[0]


@click.command("init-db")
@click.option("--se-vazio", is_flag=True,
              help="Só cria as tabelas e os dados de exemplo se o banco estiver vazio (usado no servidor).")
def init_db_command(se_vazio):
    """Cria o banco (se preciso), as tabelas e os dados de exemplo (APAGA o que existir)."""
    url = current_app.config["DATABASE_URL"]
    try:
        if criar_banco_se_nao_existir(url):
            click.echo("Banco de dados criado no PostgreSQL.")
        if se_vazio and tabelas_existem(url):
            click.echo("O banco já tem dados: nada foi alterado.")
            return
        executar_scripts(url, "schema.sql", "seed.sql")
    except psycopg.OperationalError as erro:
        raise click.ClickException(
            "Não foi possível conectar ao PostgreSQL. Confira se ele está ligado e se a senha "
            f"no arquivo .env está correta.\nDetalhe: {erro}") from None
    click.echo("Banco criado e populado com os dados de exemplo.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
