"""Testes das ROTAS (controllers + views): simulam o navegador do cliente.
Cada teste corresponde a um critério de aceitação da Etapa 1."""


def html(resposta):
    return resposta.get_data(as_text=True)


# ---------------- US03 / US04 – Catálogo ----------------

def test_catalogo_lista_cupcakes_com_foto_nome_e_preco(client):
    pagina = html(client.get("/"))
    assert "Red Velvet" in pagina
    assert "R$ 12,90" in pagina
    assert 'src="/static/img/cupcakes/red-velvet.webp"' in pagina
    assert 'alt="Cupcake Red Velvet"' in pagina  # RNF04 acessibilidade


def test_catalogo_vazio_mostra_msg10(client, sql):
    sql("UPDATE cupcake SET ativo = FALSE")
    pagina = html(client.get("/"))
    assert "Nossos cupcakes estão saindo do forno!" in pagina


def test_busca_sem_resultado_mostra_msg11(client):
    pagina = html(client.get("/?q=pizza"))
    assert "Não encontramos cupcakes com &#34;pizza&#34;" in pagina


def test_filtro_por_categoria(client):
    pagina = html(client.get("/?categoria=3"))
    assert "Cenoura Vegano" in pagina
    assert "Red Velvet" not in pagina


def test_busca_nao_executa_html_digitado(client):
    """Proteção contra XSS: o termo buscado é exibido como texto."""
    pagina = html(client.get("/?q=<script>alert(1)</script>"))
    assert "<script>alert(1)</script>" not in pagina


# ---------------- US05 – Detalhes ----------------

def test_detalhes_mostram_todas_as_informacoes(client):
    pagina = html(client.get("/cupcakes/1"))
    for esperado in ["Red Velvet", "R$ 12,90", "Tradicional", "90 g",
                     "cobertura de cream cheese", "Cacau", "Contém alergênicos", "Adicionar ao carrinho"]:
        assert esperado in pagina


def test_cupcake_sem_alergenico_listado_nao_mostra_alerta(client, sql):
    sql("DELETE FROM cupcake_ingrediente ci USING ingrediente i "
        "WHERE ci.ingrediente_id = i.id AND ci.cupcake_id = 4 AND i.alergenico")
    pagina = html(client.get("/cupcakes/4"))
    assert "Contém alergênicos" not in pagina


def test_detalhe_inexistente_mostra_msg12_com_status_404(client):
    resposta = client.get("/cupcakes/999")
    assert resposta.status_code == 404
    assert "Este cupcake não está mais disponível." in html(resposta)


def test_detalhe_de_cupcake_inativo_mostra_msg12(client, sql):
    sql("UPDATE cupcake SET ativo = FALSE WHERE id = 1")
    assert client.get("/cupcakes/1").status_code == 404


def test_pagina_inexistente_mostra_erro_amigavel(client):
    resposta = client.get("/nao-existe")
    assert resposta.status_code == 404
    assert "Ver cardápio" in html(resposta)


# ---------------- US06 – Carrinho ----------------

def adicionar(client, cupcake_id, quantidade):
    return client.post("/carrinho/adicionar", data={"cupcake_id": cupcake_id, "quantidade": quantidade},
                       follow_redirects=True)


def test_carrinho_vazio_mostra_msg14(client):
    assert "Seu carrinho está vazio" in html(client.get("/carrinho"))


def test_adicionar_ao_carrinho_mostra_msg20_e_total_correto(client):
    pagina = html(adicionar(client, 1, 2))
    assert "2× Red Velvet adicionado ao carrinho." in pagina  # MSG20
    carrinho = html(client.get("/carrinho"))
    assert "R$ 25,80" in carrinho  # subtotal
    assert "R$ 8,00" in carrinho   # entrega
    assert "R$ 33,80" in carrinho  # total (RN06)


def test_adicionar_duas_vezes_soma_quantidade(client):
    adicionar(client, 1, 2)
    adicionar(client, 1, 1)
    with client.session_transaction() as sessao:
        assert sessao["carrinho"] == {"1": 3}


def test_adicionar_mais_de_20_limita_e_mostra_msg13(client):
    pagina = html(adicionar(client, 2, 25))
    assert "O máximo é 20 unidades por sabor" in pagina
    with client.session_transaction() as sessao:
        assert sessao["carrinho"] == {"2": 20}


def test_nao_adiciona_cupcake_inativo(client, sql):  # RN04
    sql("UPDATE cupcake SET ativo = FALSE WHERE id = 1")
    pagina = html(adicionar(client, 1, 1))
    assert "Este cupcake não está mais disponível." in pagina
    with client.session_transaction() as sessao:
        assert not sessao.get("carrinho")


def test_alterar_quantidade_recalcula_total(client):
    adicionar(client, 1, 1)
    pagina = html(client.post("/carrinho/alterar", data={"cupcake_id": 1, "quantidade": 3}, follow_redirects=True))
    assert "R$ 38,70" in pagina  # 3 × 12,90
    assert "R$ 46,70" in pagina  # + 8,00


def test_remover_e_desfazer(client):
    adicionar(client, 1, 2)
    pagina = html(client.post("/carrinho/remover", data={"cupcake_id": 1}, follow_redirects=True))
    assert "Red Velvet removido do carrinho." in pagina  # MSG19
    assert "Desfazer" in pagina
    assert "Seu carrinho está vazio" in pagina
    pagina = html(client.post("/carrinho/desfazer", data={"cupcake_id": 1, "quantidade": 2}, follow_redirects=True))
    assert "R$ 33,80" in pagina


def test_cupcake_desativado_depois_sai_do_carrinho_com_msg15(client, sql):
    adicionar(client, 1, 2)
    adicionar(client, 2, 1)
    sql("UPDATE cupcake SET ativo = FALSE WHERE id = 1")
    pagina = html(client.get("/carrinho"))
    assert "O cupcake Red Velvet acabou de sair do cardápio" in pagina
    assert "R$ 22,50" in pagina  # só o Brigadeiro: 14,50 + 8,00


def test_contador_do_carrinho_na_barra_inferior(client):
    adicionar(client, 1, 2)
    adicionar(client, 2, 1)
    assert 'aria-label="3 itens"' in html(client.get("/"))


def test_erro_inesperado_mostra_msg99_sem_detalhes_tecnicos(app):  # RNF08 (incluído na Etapa 3)
    app.config["PROPAGATE_EXCEPTIONS"] = False  # comportamento de produção

    @app.get("/teste-erro")
    def quebra():
        raise RuntimeError("detalhe interno secreto")

    resposta = app.test_client().get("/teste-erro")
    pagina = html(resposta)
    assert resposta.status_code == 500
    assert "Algo deu errado do nosso lado. Tente novamente em instantes." in pagina
    assert "detalhe interno secreto" not in pagina and "Traceback" not in pagina
