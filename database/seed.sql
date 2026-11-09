-- =====================================================================
-- CupcakeApp – Dados iniciais (carga de exemplo)
-- Execute depois do schema.sql:  psql -d cupcakeapp -f database/seed.sql
--
-- Usuários de teste:
--   admin@cupcakeapp.com.br  /  Admin@2026   (perfil ADMIN)
--   mariana@email.com        /  Cupcake@123  (perfil CLIENTE)
-- As senhas são gravadas com hash bcrypt (extensão pgcrypto), nunca em texto puro (RN09).
-- =====================================================================

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

INSERT INTO usuario (nome, email, senha_hash, telefone, perfil) VALUES
 ('Administrador da Loja', 'admin@cupcakeapp.com.br', crypt('Admin@2026',  gen_salt('bf', 10)), '(11) 3000-0000', 'ADMIN'),
 ('Mariana Souza',         'mariana@email.com',       crypt('Cupcake@123', gen_salt('bf', 10)), '(11) 98888-7777', 'CLIENTE');

INSERT INTO endereco (usuario_id, cep, logradouro, numero, complemento, bairro, cidade, uf) VALUES
 (2, '01001000', 'Rua das Flores', '120', 'Apto 42', 'Centro', 'São Paulo', 'SP');

INSERT INTO categoria (nome) VALUES
 ('Clássicos'), ('Recheados'), ('Veganos'), ('Zero açúcar');

INSERT INTO ingrediente (nome, alergenico) VALUES
 ('Farinha de trigo', TRUE),    -- 1  glúten
 ('Ovos', TRUE),                -- 2
 ('Leite', TRUE),               -- 3  lactose
 ('Manteiga', TRUE),            -- 4  lactose
 ('Cream cheese', TRUE),        -- 5  lactose
 ('Leite condensado', TRUE),    -- 6  lactose
 ('Creme de leite', TRUE),      -- 7  lactose
 ('Leite em pó', TRUE),         -- 8  lactose
 ('Farinha de amêndoas', TRUE), -- 9  oleaginosa
 ('Cacau', FALSE),              -- 10
 ('Açúcar', FALSE),             -- 11
 ('Chocolate belga', FALSE),    -- 12
 ('Limão siciliano', FALSE),    -- 13
 ('Cenoura', FALSE),            -- 14
 ('Óleo de coco', FALSE),       -- 15
 ('Chocolate 70%', FALSE),      -- 16
 ('Morango', FALSE),            -- 17
 ('Xilitol', FALSE);            -- 18

INSERT INTO cupcake (categoria_id, nome, descricao, preco, tamanho, peso_gramas, foto_url) VALUES
 (1, 'Red Velvet',        'Massa aveludada de cacau com toque de baunilha e cobertura de cream cheese.',           12.90, 'TRADICIONAL',  90, '/static/img/cupcakes/red-velvet.webp'),
 (2, 'Brigadeiro Belga',  'Massa de chocolate recheada com brigadeiro de chocolate belga 54%.',                    14.50, 'TRADICIONAL', 100, '/static/img/cupcakes/brigadeiro-belga.webp'),
 (1, 'Limão Siciliano',   'Massa leve com raspas de limão siciliano e merengue maçaricado.',                       11.90, 'TRADICIONAL',  85, '/static/img/cupcakes/limao-siciliano.webp'),
 (3, 'Cenoura Vegano',    'Massa de cenoura sem ingredientes de origem animal, com cobertura de chocolate 70%.',  13.50, 'TRADICIONAL',  90, '/static/img/cupcakes/cenoura-vegano.webp'),
 (2, 'Ninho com Morango', 'Massa branca recheada com creme de leite Ninho e pedaços de morango fresco.',           15.90, 'GIGANTE',     140, '/static/img/cupcakes/ninho-morango.webp'),
 (4, 'Cacau Zero',        'Mini cupcake de cacau adoçado com xilitol, sem adição de açúcar.',                      13.90, 'MINI',         50, '/static/img/cupcakes/cacau-zero.webp');

INSERT INTO cupcake_ingrediente (cupcake_id, ingrediente_id) VALUES
 (1,1),(1,10),(1,2),(1,3),(1,5),(1,11),
 (2,1),(2,12),(2,6),(2,4),(2,2),
 (3,1),(3,13),(3,2),(3,11),(3,4),
 (4,1),(4,14),(4,15),(4,16),
 (5,1),(5,8),(5,17),(5,7),(5,2),
 (6,9),(6,10),(6,18),(6,2);

-- Pedido 1: 2x Red Velvet = 25,80 + 8,00 de entrega = 33,80 -> será entregue
INSERT INTO pedido (usuario_id, endereco_id, forma_pagamento, taxa_entrega, valor_total)
VALUES (2, 1, 'PIX', 8.00, 33.80);
INSERT INTO item_pedido (pedido_id, cupcake_id, quantidade, preco_unitario) VALUES (1, 1, 2, 12.90);
UPDATE pedido SET status = 'EM_PREPARO'        WHERE id = 1;
UPDATE pedido SET status = 'SAIU_PARA_ENTREGA' WHERE id = 1;
UPDATE pedido SET status = 'ENTREGUE'          WHERE id = 1;

-- Pedido 2: 1x Brigadeiro Belga + 1x Ninho com Morango = 30,40 + 8,00 = 38,40 -> recém-recebido
INSERT INTO pedido (usuario_id, endereco_id, forma_pagamento, taxa_entrega, valor_total, observacao)
VALUES (2, 1, 'DINHEIRO', 8.00, 38.40, 'Troco para R$ 50,00');
INSERT INTO item_pedido (pedido_id, cupcake_id, quantidade, preco_unitario) VALUES
 (2, 2, 1, 14.50),
 (2, 5, 1, 15.90);

COMMIT;
