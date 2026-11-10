# 5. Dicionário de Dados – CupcakeApp

**SGBD:** PostgreSQL 14+  •  **Banco:** `cupcakeapp`  •  **Script:** [`database/schema.sql`](../../database/schema.sql)

**Legenda:** PK = chave primária • FK = chave estrangeira • UK = valor único • NN = obrigatório (NOT NULL)

---

## usuario
Pessoas que usam o sistema: clientes e administradores da loja.

| Campo | Tipo | Restrições | Padrão | Descrição | Domínio / exemplo |
|---|---|---|---|---|---|
| id | SERIAL | PK | auto | Identificador do usuário | 1, 2, 3… |
| nome | VARCHAR(100) | NN; mínimo de 2 caracteres | – | Nome completo | "Mariana Souza" |
| email | VARCHAR(150) | NN, UK; formato de e-mail | – | E-mail usado no login (RN08) | "mariana@email.com" |
| senha_hash | VARCHAR(255) | NN | – | Hash bcrypt da senha, nunca a senha em si (RN09) | "$2a$10$…" |
| telefone | VARCHAR(20) | – | NULL | Telefone para contato sobre a entrega | "(11) 98888-7777" |
| perfil | VARCHAR(10) | NN; CHECK | 'CLIENTE' | Tipo de acesso | CLIENTE, ADMIN |
| criado_em | TIMESTAMP | NN | agora | Data e hora do cadastro | 2026-11-09 14:00 |

## endereco
Endereços de entrega cadastrados por cada cliente.

| Campo | Tipo | Restrições | Padrão | Descrição | Domínio / exemplo |
|---|---|---|---|---|---|
| id | SERIAL | PK | auto | Identificador do endereço | 1 |
| usuario_id | INTEGER | NN, FK → usuario.id (CASCADE) | – | Dono do endereço | 2 |
| cep | CHAR(8) | NN; exatamente 8 dígitos | – | CEP sem hífen | "01001000" |
| logradouro | VARCHAR(150) | NN | – | Rua, avenida etc. | "Rua das Flores" |
| numero | VARCHAR(10) | NN | – | Número. É texto para aceitar valores como "S/N" e "120-A" | "120" |
| complemento | VARCHAR(60) | – | NULL | Apartamento, bloco, referência | "Apto 42" |
| bairro | VARCHAR(80) | NN | – | Bairro | "Centro" |
| cidade | VARCHAR(80) | NN | – | Cidade | "São Paulo" |
| uf | CHAR(2) | NN; 2 letras maiúsculas | – | Sigla do estado | "SP" |

## categoria
Agrupamento dos cupcakes usado no filtro do catálogo (US04).

| Campo | Tipo | Restrições | Padrão | Descrição | Domínio / exemplo |
|---|---|---|---|---|---|
| id | SERIAL | PK | auto | Identificador da categoria | 1 |
| nome | VARCHAR(50) | NN, UK | – | Nome exibido no filtro | Clássicos, Recheados, Veganos, Zero açúcar |

## cupcake
Produtos vendidos pela loja.

| Campo | Tipo | Restrições | Padrão | Descrição | Domínio / exemplo |
|---|---|---|---|---|---|
| id | SERIAL | PK | auto | Identificador do cupcake | 1 |
| categoria_id | INTEGER | NN, FK → categoria.id (RESTRICT) | – | Categoria do produto | 1 |
| nome | VARCHAR(80) | NN, UK | – | Nome comercial | "Red Velvet" |
| descricao | TEXT | NN; não pode ser vazio (RN01) | – | Texto exibido na tela de detalhes | "Massa aveludada de cacau…" |
| preco | NUMERIC(8,2) | NN; > 0 (RN02) | – | Preço normal, em R$ | 12.90 |
| preco_promocional | NUMERIC(8,2) | Opcional; > 0 e **menor que `preco`** (`ck_cupcake_promocao`, RN12) | NULL | Preço em promoção. Quando preenchido, é o preço de venda *(Etapa 3, migração 001)* | 9.90 |
| tamanho | VARCHAR(12) | NN; CHECK | 'TRADICIONAL' | Porte do cupcake | MINI, TRADICIONAL, GIGANTE |
| peso_gramas | SMALLINT | NN; entre 10 e 1000 | – | Peso aproximado | 90 |
| foto_url | VARCHAR(255) | NN; não pode ser vazio (RN01) | – | Caminho da imagem em WebP, até 200 KB (RNF01) | "/static/img/cupcakes/red-velvet.webp" |
| ativo | BOOLEAN | NN | TRUE | Se aparece no catálogo (RN04) | TRUE / FALSE |
| criado_em | TIMESTAMP | NN | agora | Data do cadastro | – |
| atualizado_em | TIMESTAMP | NN | agora | Última edição, atualizada pelo gatilho `tg_cupcake_atualizado` | – |

## ingrediente
Ingredientes que podem compor os cupcakes.

| Campo | Tipo | Restrições | Padrão | Descrição | Domínio / exemplo |
|---|---|---|---|---|---|
| id | SERIAL | PK | auto | Identificador do ingrediente | 3 |
| nome | VARCHAR(60) | NN, UK | – | Nome do ingrediente | "Leite" |
| alergenico | BOOLEAN | NN | FALSE | Se é um alergênico comum (glúten, lactose, ovo, oleaginosas…). Quando é, aparece destacado na US05 | TRUE |

## cupcake_ingrediente
Tabela associativa que resolve o relacionamento N:N entre cupcake e ingrediente.

| Campo | Tipo | Restrições | Padrão | Descrição | Domínio / exemplo |
|---|---|---|---|---|---|
| cupcake_id | INTEGER | PK, FK → cupcake.id (CASCADE) | – | Cupcake | 1 |
| ingrediente_id | INTEGER | PK, FK → ingrediente.id (RESTRICT) | – | Ingrediente que compõe o cupcake | 5 |

## pedido
Compras finalizadas pelos clientes.

| Campo | Tipo | Restrições | Padrão | Descrição | Domínio / exemplo |
|---|---|---|---|---|---|
| id | SERIAL | PK | auto | Número do pedido mostrado ao cliente | 1052 |
| usuario_id | INTEGER | NN, FK → usuario.id (RESTRICT) | – | Cliente que fez o pedido | 2 |
| endereco_id | INTEGER | NN, FK → endereco.id (RESTRICT) | – | Endereço de entrega (RN10) | 1 |
| status | VARCHAR(20) | NN; CHECK; transições controladas por gatilho (RN07) | 'RECEBIDO' | Situação atual do pedido | RECEBIDO, EM_PREPARO, SAIU_PARA_ENTREGA, ENTREGUE, CANCELADO |
| forma_pagamento | VARCHAR(10) | NN; CHECK | – | Como o cliente pagará na entrega | PIX, CARTAO, DINHEIRO |
| taxa_entrega | NUMERIC(8,2) | NN; ≥ 0 | 8.00 | Taxa fixa de entrega (RN06) | 8.00 |
| valor_total | NUMERIC(10,2) | NN; > 0 | – | Soma dos itens + taxa de entrega (RN06) | 33.80 |
| observacao | VARCHAR(255) | – | NULL | Recado do cliente | "Troco para R$ 50,00" |
| criado_em | TIMESTAMP | NN | agora | Data e hora do pedido | – |

## item_pedido
Cupcakes que compõem cada pedido.

| Campo | Tipo | Restrições | Padrão | Descrição | Domínio / exemplo |
|---|---|---|---|---|---|
| pedido_id | INTEGER | PK, FK → pedido.id (CASCADE) | – | Pedido | 1 |
| cupcake_id | INTEGER | PK, FK → cupcake.id (RESTRICT, RN11) | – | Cupcake comprado | 1 |
| quantidade | SMALLINT | NN; entre 1 e 20 (RN03) | – | Unidades compradas | 2 |
| preco_unitario | NUMERIC(8,2) | NN; > 0 | – | Preço congelado no momento da compra (RN05) | 12.90 |

## historico_status
Linha do tempo de cada pedido (US08). É preenchida **automaticamente** pelo gatilho `tg_pedido_status`.

| Campo | Tipo | Restrições | Padrão | Descrição | Domínio / exemplo |
|---|---|---|---|---|---|
| id | SERIAL | PK | auto | Identificador do registro | 1 |
| pedido_id | INTEGER | NN, FK → pedido.id (CASCADE) | – | Pedido | 1 |
| status | VARCHAR(20) | NN; CHECK | – | Status assumido | mesmos valores de pedido.status |
| alterado_em | TIMESTAMP | NN | agora | Quando a mudança ocorreu | – |

---

## migracao
Controle das **migrações** aplicadas em bancos que já existiam (ex.: o publicado no Render). Criada automaticamente na Etapa 3.

| Campo | Tipo | Restrições | Padrão | Descrição | Domínio / exemplo |
|---|---|---|---|---|---|
| nome | VARCHAR(100) | PK | – | Nome do arquivo em `database/migracoes/` | "001_promocoes.sql" |
| aplicada_em | TIMESTAMP | NN | agora | Quando a migração foi aplicada | – |

## Objetos complementares

| Objeto | Tipo | Descrição |
|---|---|---|
| `vw_catalogo` | Visão | Cupcakes **ativos** com o nome da categoria, a indicação `contem_alergenicos` e a lista de alergênicos. É usada pelas telas de catálogo e detalhes. |
| `fn_valida_status_pedido` / `tg_pedido_status` | Função + gatilho | Valida as transições de status (RN07) e grava o histórico. |
| `fn_atualiza_timestamp` / `tg_cupcake_atualizado` | Função + gatilho | Atualiza `cupcake.atualizado_em`. |
| `ix_cupcake_categoria_ativo` | Índice | Filtro do catálogo por categoria (US03/US04). |
| `ix_cupcake_nome_lower` | Índice | Busca por nome sem diferenciar maiúsculas de minúsculas (US04). |
| `ix_pedido_usuario_data` | Índice | "Meus pedidos", do mais recente para o mais antigo (US08). |
| `ix_pedido_status` | Índice | Filtro de pedidos por status na área admin (US11). |
| `ix_endereco_usuario`, `ix_item_pedido_cupcake`, `ix_historico_pedido` | Índices | Aceleram as junções pelas chaves estrangeiras. |

## Rastreabilidade: regra de negócio → banco

| Regra | Onde é garantida no banco |
|---|---|
| RN01 foto e descrição obrigatórias | `cupcake.descricao` e `cupcake.foto_url`: NOT NULL + CHECK de texto não vazio |
| RN02 preço > 0 | CHECK em `cupcake.preco` |
| RN03 quantidade de 1 a 20 | CHECK em `item_pedido.quantidade` |
| RN04 inativos fora do catálogo | Campo `cupcake.ativo` + filtro na `vw_catalogo` |
| RN05 preço congelado | `item_pedido.preco_unitario` |
| RN06 cálculo do total | `pedido.taxa_entrega` e `pedido.valor_total`; o cálculo fica na aplicação, com teste unitário |
| RN07 fluxo de status | Gatilho `tg_pedido_status` |
| RN08 e-mail único | UNIQUE `uk_usuario_email` |
| RN09 senha com hash | `usuario.senha_hash` com bcrypt (pgcrypto no seed; biblioteca bcrypt na aplicação) |
| RN10 endereço obrigatório | `pedido.endereco_id` NOT NULL + FK |
| RN11 não excluir cupcake vendido | FK `fk_item_cupcake` com ON DELETE RESTRICT |
| RN12 promoção menor que o preço | CHECK `ck_cupcake_promocao` |
