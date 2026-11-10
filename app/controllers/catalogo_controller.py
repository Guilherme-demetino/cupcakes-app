"""Controller do catálogo: lista (US03), filtro/busca (US04) e detalhes (US05)."""
from flask import Blueprint, render_template, request

from ..messages import msg
from ..models import cupcake_model

bp = Blueprint("catalogo", __name__)


@bp.get("/")
def index():
    categoria_id = request.args.get("categoria", type=int)
    termo = request.args.get("q", "").strip()[:80]
    promocoes = request.args.get("promocoes") == "1"  # US12: filtro "Promoções"

    cupcakes = cupcake_model.listar_ativos(categoria_id, termo, so_promocoes=promocoes)

    aviso = None
    if not cupcakes:
        if promocoes and not termo and not categoria_id:
            aviso = "Nenhuma promoção no momento. Volte em breve!"
        else:
            aviso = msg("MSG11", termo=termo) if (termo or categoria_id or promocoes) else msg("MSG10")

    return render_template("catalogo.html", cupcakes=cupcakes,
                           categorias=cupcake_model.listar_categorias(),
                           categoria_id=categoria_id, termo=termo, aviso=aviso, promocoes=promocoes)


@bp.get("/cupcakes/<int:cupcake_id>")
def detalhe(cupcake_id):
    cupcake = cupcake_model.buscar_ativo_por_id(cupcake_id)
    if cupcake is None:
        return render_template("erro.html", titulo="Cupcake indisponível", mensagem=msg("MSG12")), 404
    return render_template("detalhe.html", cupcake=cupcake)
