"""Model de Cupcake: consultas do catálogo (US03, US04, US05)."""
from ..db import consultar, consultar_um

_CAMPOS = """
    c.id, c.nome, c.descricao, c.preco, c.tamanho, c.peso_gramas, c.foto_url,
    c.categoria_id, cat.nome AS categoria
"""

TAMANHOS = {"MINI": "Mini", "TRADICIONAL": "Tradicional", "GIGANTE": "Gigante"}


def _escapar_like(termo):
    """Faz % e _ digitados pelo usuário serem tratados como texto comum na busca."""
    return termo.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def listar_categorias():
    return consultar("SELECT id, nome FROM categoria ORDER BY id")


def listar_ativos(categoria_id=None, termo=None):
    """Cupcakes ativos (RN04), com filtro opcional por categoria e busca por nome (US04).
    A busca não diferencia maiúsculas de minúsculas."""
    sql = f"""SELECT {_CAMPOS}
              FROM cupcake c JOIN categoria cat ON cat.id = c.categoria_id
              WHERE c.ativo"""
    params = []
    if categoria_id:
        sql += " AND c.categoria_id = %s"
        params.append(categoria_id)
    if termo:
        sql += " AND lower(c.nome) LIKE lower(%s) ESCAPE '\\'"
        params.append(f"%{_escapar_like(termo)}%")
    sql += " ORDER BY c.nome"
    return consultar(sql, params)


def buscar_ativo_por_id(cupcake_id):
    """Detalhes completos de um cupcake ativo, com ingredientes e alergênicos (US05).
    Devolve None se não existir ou estiver inativo."""
    cupcake = consultar_um(
        f"""SELECT {_CAMPOS}
            FROM cupcake c JOIN categoria cat ON cat.id = c.categoria_id
            WHERE c.id = %s AND c.ativo""",
        (cupcake_id,),
    )
    if cupcake is None:
        return None
    cupcake["ingredientes"] = consultar(
        """SELECT i.nome, i.alergenico
           FROM ingrediente i JOIN cupcake_ingrediente ci ON ci.ingrediente_id = i.id
           WHERE ci.cupcake_id = %s
           ORDER BY i.alergenico DESC, i.nome""",
        (cupcake_id,),
    )
    cupcake["alergenicos"] = [i["nome"] for i in cupcake["ingredientes"] if i["alergenico"]]
    cupcake["tamanho_rotulo"] = TAMANHOS.get(cupcake["tamanho"], cupcake["tamanho"])
    return cupcake


def buscar_ativos_por_ids(ids):
    """Devolve {id: cupcake} só com os cupcakes ativos da lista (usado pelo carrinho)."""
    ids = [int(i) for i in ids]
    if not ids:
        return {}
    marcadores = ", ".join(["%s"] * len(ids))
    linhas = consultar(
        f"""SELECT {_CAMPOS}
            FROM cupcake c JOIN categoria cat ON cat.id = c.categoria_id
            WHERE c.ativo AND c.id IN ({marcadores})""",
        ids,
    )
    return {linha["id"]: linha for linha in linhas}


def buscar_nome(cupcake_id):
    """Nome de um cupcake mesmo que esteja inativo (para avisar o cliente, MSG15)."""
    linha = consultar_um("SELECT nome FROM cupcake WHERE id = %s", (cupcake_id,))
    return linha["nome"] if linha else "selecionado"
