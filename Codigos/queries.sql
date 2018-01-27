-- Consulta por orgao
SELECT c.NR_CONVENIO, c.ID_PROPOSTA, c.DIA_ASSIN_CONV, c.VL_GLOBAL_CONV, c.total, p.COD_ORGAO, p.COD_ORGAO_SUP
FROM convenio_pagamentos AS c, proposta AS p
WHERE c.ID_PROPOSTA = p.ID_PROPOSTA AND p.COD_ORGAO = %i

-- Busca por Parlamentar
SELECT *
FROM convenio_pagamentos AS c, parlamentares AS p
WHERE c.ID_PROPOSTA = p.ID_PROPOSTA;

-- view dos parlamentares
CREATE VIEW parlamentares AS
SELECT p.ID_PARLAMENTAR, p.NM_PARLAMENTAR, e.ID_PROPOSTA
FROM parlamentar AS p, emenda AS e
WHERE p.ID_PARLAMENTAR = e.ID_PARLAMENTAR;

-- view valor total de  cada convenio
CREATE VIEW total_pagamento AS
SELECT NR_CONVENIO, SUM(VL_PAGO) as total
FROM pagamento
GROUP BY NR_CONVENIO;

-- view dados de todos os convenios que receberam pagamentos
CREATE VIEW convenio_pagamentos AS
SELECT c.NR_CONVENIO, c.ID_PROPOSTA, c.DIA_ASSIN_CONV, c.VL_GLOBAL_CONV, s.total
FROM convenio AS c, soma_pagamentos AS s
WHERE c.NR_CONVENIO = s.NR_CONVENIO;