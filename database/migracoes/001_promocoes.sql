-- Migração 001 – Promoções (Etapa 3, sugestão C01 do avaliador 1)
-- Acrescenta o preço promocional em um banco que JÁ EXISTE (ex.: o do Render),
-- sem apagar nenhum dado. Pode ser executada mais de uma vez sem efeito colateral.

ALTER TABLE cupcake ADD COLUMN IF NOT EXISTS preco_promocional NUMERIC(8,2);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_cupcake_promocao') THEN
        ALTER TABLE cupcake ADD CONSTRAINT ck_cupcake_promocao CHECK (
            preco_promocional IS NULL OR (preco_promocional > 0 AND preco_promocional < preco));
    END IF;
END $$;

-- Promoções iniciais, iguais às do seed.sql (só se o cupcake existir e ainda não tiver promoção)
UPDATE cupcake SET preco_promocional = 9.90
 WHERE nome = 'Limão Siciliano' AND preco_promocional IS NULL AND preco > 9.90;
UPDATE cupcake SET preco_promocional = 11.50
 WHERE nome = 'Cenoura Vegano' AND preco_promocional IS NULL AND preco > 11.50;
