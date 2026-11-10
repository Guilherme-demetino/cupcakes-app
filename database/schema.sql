-- =====================================================================
-- CupcakeApp – Projeto físico do banco de dados
-- SGBD: PostgreSQL 14+
-- Autor: Guilherme França Demetino (RGM 33160236) – PI II, Situação 1
--
-- Como executar:
--   createdb cupcakeapp
--   psql -d cupcakeapp -f database/schema.sql
--   psql -d cupcakeapp -f database/seed.sql
-- =====================================================================

BEGIN;

DROP TABLE IF EXISTS historico_status, item_pedido, pedido, cupcake_ingrediente,
                     ingrediente, cupcake, categoria, endereco, usuario, migracao CASCADE;

-- ---------------------------------------------------------------------
-- USUARIO: clientes e administradores (RN08, RN09)
-- ---------------------------------------------------------------------
CREATE TABLE usuario (
    id           SERIAL        PRIMARY KEY,
    nome         VARCHAR(100)  NOT NULL CHECK (length(trim(nome)) >= 2),
    email        VARCHAR(150)  NOT NULL,
    senha_hash   VARCHAR(255)  NOT NULL,
    telefone     VARCHAR(20),
    perfil       VARCHAR(10)   NOT NULL DEFAULT 'CLIENTE'
                               CHECK (perfil IN ('CLIENTE', 'ADMIN')),
    criado_em    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_usuario_email UNIQUE (email),
    CONSTRAINT ck_usuario_email CHECK (email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$')
);

-- ---------------------------------------------------------------------
-- ENDERECO: endereços de entrega do cliente
-- ---------------------------------------------------------------------
CREATE TABLE endereco (
    id           SERIAL        PRIMARY KEY,
    usuario_id   INTEGER       NOT NULL,
    cep          CHAR(8)       NOT NULL CHECK (cep ~ '^[0-9]{8}$'),
    logradouro   VARCHAR(150)  NOT NULL,
    numero       VARCHAR(10)   NOT NULL,
    complemento  VARCHAR(60),
    bairro       VARCHAR(80)   NOT NULL,
    cidade       VARCHAR(80)   NOT NULL,
    uf           CHAR(2)       NOT NULL CHECK (uf ~ '^[A-Z]{2}$'),
    CONSTRAINT fk_endereco_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuario (id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- CATEGORIA
-- ---------------------------------------------------------------------
CREATE TABLE categoria (
    id    SERIAL       PRIMARY KEY,
    nome  VARCHAR(50)  NOT NULL,
    CONSTRAINT uk_categoria_nome UNIQUE (nome)
);

-- ---------------------------------------------------------------------
-- CUPCAKE: produtos do catálogo (RN01, RN02, RN04, RN11)
-- ---------------------------------------------------------------------
CREATE TABLE cupcake (
    id             SERIAL        PRIMARY KEY,
    categoria_id   INTEGER       NOT NULL,
    nome           VARCHAR(80)   NOT NULL,
    descricao      TEXT          NOT NULL CHECK (length(trim(descricao)) > 0),   -- RN01
    preco          NUMERIC(8,2)  NOT NULL CHECK (preco > 0),                     -- RN02
    preco_promocional NUMERIC(8,2),                                              -- RN12 (Etapa 3, C01)
    tamanho        VARCHAR(12)   NOT NULL DEFAULT 'TRADICIONAL'
                                 CHECK (tamanho IN ('MINI', 'TRADICIONAL', 'GIGANTE')),
    peso_gramas    SMALLINT      NOT NULL CHECK (peso_gramas BETWEEN 10 AND 1000),
    foto_url       VARCHAR(255)  NOT NULL CHECK (length(trim(foto_url)) > 0),    -- RN01
    ativo          BOOLEAN       NOT NULL DEFAULT TRUE,                          -- RN04
    criado_em      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_cupcake_nome UNIQUE (nome),
    CONSTRAINT ck_cupcake_promocao CHECK (preco_promocional IS NULL
        OR (preco_promocional > 0 AND preco_promocional < preco)),               -- RN12
    CONSTRAINT fk_cupcake_categoria FOREIGN KEY (categoria_id)
        REFERENCES categoria (id) ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------
-- INGREDIENTE e associação N:N com CUPCAKE
-- ---------------------------------------------------------------------
CREATE TABLE ingrediente (
    id          SERIAL       PRIMARY KEY,
    nome        VARCHAR(60)  NOT NULL,
    alergenico  BOOLEAN      NOT NULL DEFAULT FALSE,
    CONSTRAINT uk_ingrediente_nome UNIQUE (nome)
);

CREATE TABLE cupcake_ingrediente (
    cupcake_id      INTEGER  NOT NULL,
    ingrediente_id  INTEGER  NOT NULL,
    CONSTRAINT pk_cupcake_ingrediente PRIMARY KEY (cupcake_id, ingrediente_id),
    CONSTRAINT fk_ci_cupcake FOREIGN KEY (cupcake_id)
        REFERENCES cupcake (id) ON DELETE CASCADE,
    CONSTRAINT fk_ci_ingrediente FOREIGN KEY (ingrediente_id)
        REFERENCES ingrediente (id) ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------
-- PEDIDO (RN06, RN07, RN10)
-- ---------------------------------------------------------------------
CREATE TABLE pedido (
    id               SERIAL         PRIMARY KEY,
    usuario_id       INTEGER        NOT NULL,
    endereco_id      INTEGER        NOT NULL,
    status           VARCHAR(20)    NOT NULL DEFAULT 'RECEBIDO'
                     CHECK (status IN ('RECEBIDO', 'EM_PREPARO', 'SAIU_PARA_ENTREGA',
                                       'ENTREGUE', 'CANCELADO')),
    forma_pagamento  VARCHAR(10)    NOT NULL
                     CHECK (forma_pagamento IN ('PIX', 'CARTAO', 'DINHEIRO')),
    taxa_entrega     NUMERIC(8,2)   NOT NULL DEFAULT 8.00 CHECK (taxa_entrega >= 0),
    valor_total      NUMERIC(10,2)  NOT NULL CHECK (valor_total > 0),
    observacao       VARCHAR(255),
    criado_em        TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pedido_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuario (id) ON DELETE RESTRICT,
    CONSTRAINT fk_pedido_endereco FOREIGN KEY (endereco_id)
        REFERENCES endereco (id) ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------
-- ITEM_PEDIDO (RN03, RN05, RN11)
-- ---------------------------------------------------------------------
CREATE TABLE item_pedido (
    pedido_id       INTEGER       NOT NULL,
    cupcake_id      INTEGER       NOT NULL,
    quantidade      SMALLINT      NOT NULL CHECK (quantidade BETWEEN 1 AND 20),  -- RN03
    preco_unitario  NUMERIC(8,2)  NOT NULL CHECK (preco_unitario > 0),           -- RN05
    CONSTRAINT pk_item_pedido PRIMARY KEY (pedido_id, cupcake_id),
    CONSTRAINT fk_item_pedido FOREIGN KEY (pedido_id)
        REFERENCES pedido (id) ON DELETE CASCADE,
    CONSTRAINT fk_item_cupcake FOREIGN KEY (cupcake_id)
        REFERENCES cupcake (id) ON DELETE RESTRICT                               -- RN11
);

-- ---------------------------------------------------------------------
-- HISTORICO_STATUS: linha do tempo do pedido (US08)
-- ---------------------------------------------------------------------
CREATE TABLE historico_status (
    id           SERIAL       PRIMARY KEY,
    pedido_id    INTEGER      NOT NULL,
    status       VARCHAR(20)  NOT NULL
                 CHECK (status IN ('RECEBIDO', 'EM_PREPARO', 'SAIU_PARA_ENTREGA',
                                   'ENTREGUE', 'CANCELADO')),
    alterado_em  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_historico_pedido FOREIGN KEY (pedido_id)
        REFERENCES pedido (id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- ÍNDICES (consultas frequentes)
-- ---------------------------------------------------------------------
CREATE INDEX ix_cupcake_categoria_ativo ON cupcake (categoria_id, ativo);
CREATE INDEX ix_cupcake_nome_lower      ON cupcake (lower(nome));          -- busca US04
CREATE INDEX ix_endereco_usuario        ON endereco (usuario_id);
CREATE INDEX ix_pedido_usuario_data     ON pedido (usuario_id, criado_em DESC); -- US08
CREATE INDEX ix_pedido_status           ON pedido (status);                 -- US11
CREATE INDEX ix_item_pedido_cupcake     ON item_pedido (cupcake_id);
CREATE INDEX ix_historico_pedido        ON historico_status (pedido_id, alterado_em);

-- ---------------------------------------------------------------------
-- GATILHOS
-- ---------------------------------------------------------------------
-- 1) Mantém cupcake.atualizado_em sempre atualizado
CREATE OR REPLACE FUNCTION fn_atualiza_timestamp() RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_cupcake_atualizado
    BEFORE UPDATE ON cupcake
    FOR EACH ROW EXECUTE FUNCTION fn_atualiza_timestamp();

-- 2) RN07: impede transições de status inválidas e grava o histórico
CREATE OR REPLACE FUNCTION fn_valida_status_pedido() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.status <> OLD.status THEN
        IF NOT (
               (OLD.status = 'RECEBIDO'          AND NEW.status IN ('EM_PREPARO', 'CANCELADO'))
            OR (OLD.status = 'EM_PREPARO'        AND NEW.status IN ('SAIU_PARA_ENTREGA', 'CANCELADO'))
            OR (OLD.status = 'SAIU_PARA_ENTREGA' AND NEW.status = 'ENTREGUE')
        ) THEN
            RAISE EXCEPTION 'Transição de status inválida: % -> %', OLD.status, NEW.status
                USING ERRCODE = 'check_violation';
        END IF;
    END IF;

    IF TG_OP = 'INSERT' OR NEW.status <> OLD.status THEN
        INSERT INTO historico_status (pedido_id, status) VALUES (NEW.id, NEW.status);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_pedido_status
    AFTER INSERT OR UPDATE OF status ON pedido
    FOR EACH ROW EXECUTE FUNCTION fn_valida_status_pedido();

-- ---------------------------------------------------------------------
-- VISÃO: catálogo público com indicação de alergênicos (US03/US05)
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_catalogo AS
SELECT c.id,
       c.nome,
       cat.nome                               AS categoria,
       c.descricao,
       c.preco,
       c.tamanho,
       c.peso_gramas,
       c.foto_url,
       COALESCE(bool_or(i.alergenico), FALSE) AS contem_alergenicos,
       string_agg(i.nome, ', ' ORDER BY i.nome) FILTER (WHERE i.alergenico) AS alergenicos
FROM cupcake c
JOIN categoria cat               ON cat.id = c.categoria_id
LEFT JOIN cupcake_ingrediente ci ON ci.cupcake_id = c.id
LEFT JOIN ingrediente i          ON i.id = ci.ingrediente_id
WHERE c.ativo
GROUP BY c.id, cat.nome;

COMMIT;
