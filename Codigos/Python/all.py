# -*- coding: utf-8 -*-
import MySQLdb as my
import csv
from unicodedata import normalize
import timeit

FORMAT_NUMBER = lambda x: x.replace(",", ".").replace("\u200b", "")
FORMAT_IDENTITY = lambda x: x
FORMAT_ESCAPE_SINGLE_QUOTE = lambda x: x.replace("\\", "").replace("'", "''")
FORMAT_NON_UTF8_CHARS = lambda x: FORMAT_ESCAPE_SINGLE_QUOTE(x.replace('\U00100070', '').replace('\\', '\\\\').replace('􀀹', '').replace('􀂳', ''))
FORMAT_REMOVE_ACCENTS = lambda x: FORMAT_ESCAPE_SINGLE_QUOTE(normalize('NFKD', x).encode('ASCII', 'ignore').decode('ASCII').upper())
FORMAT_DATE = lambda x: '{}-{}-{}'.format(*x.split("/")[::-1])
DEFAULT_BATCH_SIZE = 500

SENADORES_CONFIG = {
    'csv_file_name': 'senadores',
    'csv_expected_header': 'IdentificacaoParlamentar/CodigoParlamentar;IdentificacaoParlamentar/NomeParlamentar;IdentificacaoParlamentar/NomeCompletoParlamentar;IdentificacaoParlamentar/SexoParlamentar;IdentificacaoParlamentar/FormaTratamento;IdentificacaoParlamentar/UrlFotoParlamentar;IdentificacaoParlamentar/UrlPaginaParlamentar;IdentificacaoParlamentar/EmailParlamentar;IdentificacaoParlamentar/SiglaPartidoParlamentar;IdentificacaoParlamentar/UfParlamentar;Mandato/CodigoMandato;Mandato/UfParlamentar;Mandato/PrimeiraLegislaturaDoMandato/NumeroLegislatura;Mandato/PrimeiraLegislaturaDoMandato/DataInicio;Mandato/PrimeiraLegislaturaDoMandato/DataFim;Mandato/SegundaLegislaturaDoMandato/NumeroLegislatura;Mandato/SegundaLegislaturaDoMandato/DataInicio;Mandato/SegundaLegislaturaDoMandato/DataFim;Mandato/DescricaoParticipacao;Mandato/Suplentes/Suplente/0/DescricaoParticipacao;Mandato/Suplentes/Suplente/0/CodigoParlamentar;Mandato/Suplentes/Suplente/0/NomeParlamentar;Mandato/Suplentes/Suplente/1/DescricaoParticipacao;Mandato/Suplentes/Suplente/1/CodigoParlamentar;Mandato/Suplentes/Suplente/1/NomeParlamentar;Mandato/Exercicios/Exercicio/0/CodigoExercicio;Mandato/Exercicios/Exercicio/0/DataInicio;Mandato/Exercicios/Exercicio/1/CodigoExercicio;Mandato/Exercicios/Exercicio/1/DataInicio;Mandato/Exercicios/Exercicio/1/DataFim;Mandato/Exercicios/Exercicio/1/SiglaCausaAfastamento;Mandato/Exercicios/Exercicio/1/DescricaoCausaAfastamento;UrlGlossario;Mandato/Titular/DescricaoParticipacao;Mandato/Titular/CodigoParlamentar;Mandato/Titular/NomeParlamentar;Mandato/Exercicios/Exercicio/2/CodigoExercicio;Mandato/Exercicios/Exercicio/2/DataInicio;Mandato/Exercicios/Exercicio/2/DataFim;Mandato/Exercicios/Exercicio/2/SiglaCausaAfastamento;Mandato/Exercicios/Exercicio/2/DescricaoCausaAfastamento;Mandato/Exercicios/Exercicio/0/DataLeitura;Mandato/Exercicios/Exercicio/1/DataLeitura;Mandato/Exercicios/Exercicio/3/CodigoExercicio;Mandato/Exercicios/Exercicio/3/DataInicio;Mandato/Exercicios/Exercicio/3/DataFim;Mandato/Exercicios/Exercicio/3/SiglaCausaAfastamento;Mandato/Exercicios/Exercicio/3/DescricaoCausaAfastamento;Mandato/Exercicios/Exercicio/4/CodigoExercicio;Mandato/Exercicios/Exercicio/4/DataInicio;Mandato/Exercicios/Exercicio/4/DataFim;Mandato/Exercicios/Exercicio/4/SiglaCausaAfastamento;Mandato/Exercicios/Exercicio/4/DescricaoCausaAfastamento;Mandato/Exercicios/Exercicio/2/DataLeitura',
    'csv_columns_indexes': [1, 2, 8],
    'table_name': 'parlamentar',
    'columns_to_insert': ["NOME_PARLAMENTAR", "NOME_COMPLETO", "SIGLA_PARTIDO", "TIPO_PARLAMENTAR", "FUNCAO"],
    'insert_value_format': "('{}', '{}', '{}', 'INDIVIDUAL', 'SENADOR')",
    'row_formatters': [FORMAT_REMOVE_ACCENTS] * 2 + [FORMAT_IDENTITY],
    'insert_command': "INSERT"
}

DEPUTADOS_CONFIG = {
    'csv_file_name': 'deputado',
    'csv_expected_header': 'Nome Parlamentar;Partido;UF;Titular/Suplente/Efetivado;Endereço;Anexo;Endereço (continuação);Gabinete;Endereço (complemento);Telefone;Fax;Mês Aniversário;Dia Aniversário;Correio Eletrônico;Nome sem Acento;Tratamento;Nome Civil',
    'csv_columns_indexes': [0, 16, 1],
    'table_name': 'parlamentar',
    'columns_to_insert': ["NOME_PARLAMENTAR", "NOME_COMPLETO", "SIGLA_PARTIDO", "TIPO_PARLAMENTAR", "FUNCAO"],
    'insert_value_format': "('{}', '{}', '{}', 'INDIVIDUAL', 'DEPUTADO')",
    'row_formatters': [FORMAT_REMOVE_ACCENTS] * 2 + [FORMAT_IDENTITY],
    'insert_command': "INSERT"
}

ORGAO_SUP_CONFIG = {
    'csv_file_name': 'siconv_proposta',
    'csv_expected_header': 'ID_PROPOSTA;UF_PROPONENTE;MUNIC_PROPONENTE;COD_MUNIC_IBGE;COD_ORGAO_SUP;DESC_ORGAO_SUP;NATUREZA_JURIDICA;NR_PROPOSTA;DIA_PROP;MES_PROP;ANO_PROP;DIA_PROPOSTA;COD_ORGAO;DESC_ORGAO;MODALIDADE;IDENTIF_PROPONENTE;NM_PROPONENTE;CEP_PROPONENTE;ENDERECO_PROPONENTE;BAIRRO_PROPONENTE;NM_BANCO;SITUACAO_CONTA;SITUACAO_PROJETO_BASICO;SIT_PROPOSTA;DIA_INIC_VIGENCIA_PROPOSTA;DIA_FIM_VIGENCIA_PROPOSTA;OBJETO_PROPOSTA;VL_GLOBAL_PROP;VL_REPASSE_PROP;VL_CONTRAPARTIDA_PROP',
    'csv_columns_indexes': [4, 5],
    'table_name': 'orgao',
    'columns_to_insert': ["COD_ORGAO", "DESC_ORGAO"],
    'insert_value_format': "({}, '{}')",
    'row_formatters': [FORMAT_NUMBER, FORMAT_IDENTITY],
    'insert_command': "REPLACE"
}

ORGAO_CONFIG = {
    'csv_file_name': 'siconv_proposta',
    'csv_expected_header': 'ID_PROPOSTA;UF_PROPONENTE;MUNIC_PROPONENTE;COD_MUNIC_IBGE;COD_ORGAO_SUP;DESC_ORGAO_SUP;NATUREZA_JURIDICA;NR_PROPOSTA;DIA_PROP;MES_PROP;ANO_PROP;DIA_PROPOSTA;COD_ORGAO;DESC_ORGAO;MODALIDADE;IDENTIF_PROPONENTE;NM_PROPONENTE;CEP_PROPONENTE;ENDERECO_PROPONENTE;BAIRRO_PROPONENTE;NM_BANCO;SITUACAO_CONTA;SITUACAO_PROJETO_BASICO;SIT_PROPOSTA;DIA_INIC_VIGENCIA_PROPOSTA;DIA_FIM_VIGENCIA_PROPOSTA;OBJETO_PROPOSTA;VL_GLOBAL_PROP;VL_REPASSE_PROP;VL_CONTRAPARTIDA_PROP',
    'csv_columns_indexes': [12, 13],
    'table_name': 'orgao',
    'columns_to_insert': ["COD_ORGAO", "DESC_ORGAO"],
    'insert_value_format': "({}, '{}')",
    'row_formatters': [FORMAT_NUMBER, FORMAT_IDENTITY],
    'insert_command': "REPLACE"
}

MUNICIPIO_CONFIG = {
    'csv_file_name': 'siconv_proposta',
    'csv_expected_header': 'ID_PROPOSTA;UF_PROPONENTE;MUNIC_PROPONENTE;COD_MUNIC_IBGE;COD_ORGAO_SUP;DESC_ORGAO_SUP;NATUREZA_JURIDICA;NR_PROPOSTA;DIA_PROP;MES_PROP;ANO_PROP;DIA_PROPOSTA;COD_ORGAO;DESC_ORGAO;MODALIDADE;IDENTIF_PROPONENTE;NM_PROPONENTE;CEP_PROPONENTE;ENDERECO_PROPONENTE;BAIRRO_PROPONENTE;NM_BANCO;SITUACAO_CONTA;SITUACAO_PROJETO_BASICO;SIT_PROPOSTA;DIA_INIC_VIGENCIA_PROPOSTA;DIA_FIM_VIGENCIA_PROPOSTA;OBJETO_PROPOSTA;VL_GLOBAL_PROP;VL_REPASSE_PROP;VL_CONTRAPARTIDA_PROP',
    'csv_columns_indexes': [2, 3],
    'table_name': 'municipio',
    'columns_to_insert': ["MUNIC_PROPONENTE", "COD_MUNIC_IBGE"],
    'insert_value_format': "('{}', {})",
    'row_formatters': [FORMAT_ESCAPE_SINGLE_QUOTE, FORMAT_NUMBER],
    'insert_command': "INSERT IGNORE" # Ignore porque tem algumas propostas sem COD_MUNIC_IBGE
}

PROPONENTE_CONFIG = {
    'csv_file_name': 'siconv_proposta',
    'csv_expected_header': 'ID_PROPOSTA;UF_PROPONENTE;MUNIC_PROPONENTE;COD_MUNIC_IBGE;COD_ORGAO_SUP;DESC_ORGAO_SUP;NATUREZA_JURIDICA;NR_PROPOSTA;DIA_PROP;MES_PROP;ANO_PROP;DIA_PROPOSTA;COD_ORGAO;DESC_ORGAO;MODALIDADE;IDENTIF_PROPONENTE;NM_PROPONENTE;CEP_PROPONENTE;ENDERECO_PROPONENTE;BAIRRO_PROPONENTE;NM_BANCO;SITUACAO_CONTA;SITUACAO_PROJETO_BASICO;SIT_PROPOSTA;DIA_INIC_VIGENCIA_PROPOSTA;DIA_FIM_VIGENCIA_PROPOSTA;OBJETO_PROPOSTA;VL_GLOBAL_PROP;VL_REPASSE_PROP;VL_CONTRAPARTIDA_PROP',
    'csv_columns_indexes': [1, 2, 3, 6, 15, 16, 17, 18, 19],
    'table_name': 'proponente',
    'columns_to_insert': ['UF_PROPONENTE', 'MUNIC_PROPONENTE', 'COD_MUNIC_IBGE', 'NATUREZA_JURIDICA', 'IDENTIF_PROPONENTE', 'NM_PROPONENTE',
    'CEP_PROPONENTE', 'ENDERECO_PROPONENTE', 'BAIRRO_PROPONENTE'],
    'insert_value_format': "('{}', '{}', {}, '{}', {}, '{}', '{}', '{}', '{}')",
    'row_formatters': [FORMAT_ESCAPE_SINGLE_QUOTE] * 2 + [FORMAT_NUMBER] + [FORMAT_ESCAPE_SINGLE_QUOTE] \
    + [FORMAT_NUMBER] + [FORMAT_ESCAPE_SINGLE_QUOTE] * 4,
    'insert_command': "REPLACE"
}

PROPOSTA_CONFIG = {
    'csv_file_name': 'siconv_proposta',
    'csv_expected_header': 'ID_PROPOSTA;UF_PROPONENTE;MUNIC_PROPONENTE;COD_MUNIC_IBGE;COD_ORGAO_SUP;DESC_ORGAO_SUP;NATUREZA_JURIDICA;NR_PROPOSTA;DIA_PROP;MES_PROP;ANO_PROP;DIA_PROPOSTA;COD_ORGAO;DESC_ORGAO;MODALIDADE;IDENTIF_PROPONENTE;NM_PROPONENTE;CEP_PROPONENTE;ENDERECO_PROPONENTE;BAIRRO_PROPONENTE;NM_BANCO;SITUACAO_CONTA;SITUACAO_PROJETO_BASICO;SIT_PROPOSTA;DIA_INIC_VIGENCIA_PROPOSTA;DIA_FIM_VIGENCIA_PROPOSTA;OBJETO_PROPOSTA;VL_GLOBAL_PROP;VL_REPASSE_PROP;VL_CONTRAPARTIDA_PROP',
    'csv_columns_indexes': [0, 4, 7, 11, 12, 14, 15, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
    'table_name': 'proposta',
    'columns_to_insert': ["ID_PROPOSTA", "COD_ORGAO_SUP", "NR_PROPOSTA", "DIA_PROPOSTA",
    "COD_ORGAO", "MODALIDADE", "IDENTIF_PROPONENTE", "NM_BANCO", "SITUACAO_CONTA", "SITUACAO_PROJETO_BASICO",
    "SIT_PROPOSTA", "DIA_INIC_VIGENCIA_PROPOSTA", "DIA_FIM_VIGENCIA_PROPOSTA", "OBJETO_PROPOSTA", "VL_GLOBAL_PROP",
    "VL_REPASSE_PROP", "VL_CONTRAPARTIDA_PROP"],
    'insert_value_format': "({}, {}, '{}', '{}', {}, '{}', {}, '{}', '{}', '{}', '{}', '{}', '{}', '{}', {}, {}, {})",
    'row_formatters': [FORMAT_NUMBER] * 2 + [FORMAT_ESCAPE_SINGLE_QUOTE] + [FORMAT_DATE] + [FORMAT_NUMBER] + [FORMAT_ESCAPE_SINGLE_QUOTE] + [FORMAT_NUMBER] \
    + [FORMAT_ESCAPE_SINGLE_QUOTE] * 4 + [FORMAT_DATE] * 2 + [FORMAT_NON_UTF8_CHARS] + [FORMAT_NUMBER] * 3,
    'insert_command': "INSERT"
}

CONVENIO_CONFIG = {
    'csv_file_name': 'siconv_convenio',
    'csv_expected_header': 'NR_CONVENIO;ID_PROPOSTA;DIA;MES;ANO;DIA_ASSIN_CONV;SIT_CONVENIO;SUBSITUACAO_CONV;SITUACAO_PUBLICACAO;INSTRUMENTO_ATIVO;IND_OPERA_OBTV;NR_PROCESSO;UG_EMITENTE;DIA_PUBL_CONV;DIA_INIC_VIGENC_CONV;DIA_FIM_VIGENC_CONV;DIAS_PREST_CONTAS;DIA_LIMITE_PREST_CONTAS;SITUACAO_CONTRATACAO;QTDE_CONVENIOS;QTD_TA;QTD_PRORROGA;VL_GLOBAL_CONV;VL_REPASSE_CONV;VL_CONTRAPARTIDA_CONV;VL_EMPENHADO_CONV;VL_DESEMBOLSADO_CONV;VL_SALDO_REMAN_TESOURO;VL_SALDO_REMAN_CONVENENTE;VL_RENDIMENTO_APLICACAO;VL_INGRESSO_CONTRAPARTIDA',
    'csv_columns_indexes': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
    'table_name': 'convenio',
    'columns_to_insert': ["NR_CONVENIO", "ID_PROPOSTA", "DIA", "MES", "ANO",
    "DIA_ASSIN_CONV", "SIT_CONVENIO", "SUBSITUACAO_CONV", "SITUACAO_PUBLICACAO", "INSTRUMENTO_ATIVO",
    "IND_OPERA_OBTV", "DIA_PUBL_CONV", "DATA_INICIO_VIGENC_CONV", "DATA_FIM_VIGENC_CONV", "DIAS_PREST_CONTAS",
    "DATA_LIMITE_PREST_CONTAS", "SITUACAO_CONTRATACAO", "QTDE_CONVENIOS", "QTD_TA", "QTD_PRORROGA",
    "VL_GLOBAL_CONV", "VL_REPASSE_CONV", "VL_CONTRAPARTIDA_CONV", "VL_EMPENHADO_CONV", "VL_DESEMBOLSADO_CONV",
    "VL_SALDO_REMAN_TESOURO", "VL_SALDO_REMAN_CONVENENTE", "VL_RENDIMENTO_APLICACAO", "VL_INGRESSO_CONTRAPARTIDA"],
    'insert_value_format': '({}, {}'+ (", '{}'" * 16) + (", {}" * 11) + ')',
    'row_formatters': [FORMAT_NUMBER] * 2 + [FORMAT_ESCAPE_SINGLE_QUOTE] * 3 + [FORMAT_DATE] \
    + [FORMAT_ESCAPE_SINGLE_QUOTE] * 12 + [FORMAT_NUMBER] * 11,
    'insert_command': "INSERT"
}

DESEMBOLSO_CONFIG = {
    'csv_file_name': 'siconv_desembolso',
    'csv_expected_header': 'NR_CONVENIO;DT_ULT_DESEMBOLSO;QTD_DIAS_SEM_DESEMBOLSO;DATA_DESEMBOLSO;ANO_DESEMBOLSO;MES_DESEMBOLSO;NR_SIAFI;VL_DESEMBOLSADO',
    'csv_columns_indexes': [0, 1, 2, 3, 6, 7],
    'table_name': 'desembolso',
    'columns_to_insert': ["NR_CONVENIO", "DT_ULT_DESEMBOLSO", "QTD_DIAS_SEM_DESEMBOLSO", "DATA_DESEMBOLSO", "NR_SIAFI", "VL_DESEMBOLSADO"],
    'insert_value_format': "({}, '{}', {}, '{}', '{}', {})",
    'row_formatters': [FORMAT_NUMBER, FORMAT_DATE, FORMAT_NUMBER, FORMAT_DATE, FORMAT_ESCAPE_SINGLE_QUOTE, FORMAT_NUMBER],
    'insert_command': "INSERT"
}

META_CONFIG = {
    'csv_file_name': 'siconv_meta_crono_fisico',
    'csv_expected_header': 'ID_META;NR_CONVENIO;COD_PROGRAMA;NOME_PROGRAMA;NR_META;TIPO_META;DESC_META;DATA_INICIO_META;DATA_FIM_META;UF_META;MUNICIPIO_META;ENDERECO_META;CEP_META;QTD_META;UND_FORNECIMENTO_META;VL_META',
    'csv_columns_indexes': [0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    'table_name': 'meta',
    'columns_to_insert': ["ID_META", "NR_CONVENIO", "NR_META", "TIPO_META", "DESC_META", "DATA_INICIO_META", "DATA_FIM_META", "UF_META", "MUNIC_META", "ENDERECO_META", "CEP_META", "QTD_META", "UND_FORNECIMENTO_META", "VL_META"],
    'insert_value_format': "({}, {}, {}, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {})",
    'row_formatters': [FORMAT_NUMBER] * 3 + [FORMAT_ESCAPE_SINGLE_QUOTE] * 2 + [FORMAT_DATE] * 2 + [FORMAT_ESCAPE_SINGLE_QUOTE] * 4 + [FORMAT_NUMBER] + [FORMAT_ESCAPE_SINGLE_QUOTE] + [FORMAT_NUMBER],
    'insert_command': "INSERT"
}

TERMO_ADITIVO_CONFIG = {
    'csv_file_name': 'siconv_termo_aditivo',
    'csv_expected_header': 'NR_CONVENIO;NUMERO_TA;TIPO_TA;VL_GLOBAL_TA;VL_REPASSE_TA;VL_CONTRAPARTIDA_TA;DT_ASSINATURA_TA;DT_INICIO_TA;DT_FIM_TA;JUSTIFICATIVA_TA',
    'csv_columns_indexes': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    'table_name': 'termo_aditivo',
    'columns_to_insert': ["NR_CONVENIO", "NUMERO_TA", "TIPO_TA", "VL_GLOBAL_TA", "VL_REPASSE_TA", "VL_CONTRAPARTIDA_TA", "DT_ASSINATURA_TA", "DT_INICIO_TA", "DT_FIM_TA", "JUSTIFICATIVA_TA"],
    'insert_value_format': "({}, '{}', '{}', {}, {}, {}, '{}', '{}', '{}', '{}')",
    'row_formatters': [FORMAT_NUMBER] + [FORMAT_IDENTITY] * 2 + [FORMAT_NUMBER] * 3 + [FORMAT_DATE] * 3 + [FORMAT_NON_UTF8_CHARS],
    'insert_command': "INSERT"
}

EMPENHO_CONFIG = {
    'csv_file_name': 'siconv_empenho',
    'csv_expected_header': 'NR_CONVENIO;NR_EMPENHO;TIPO_NOTA;DESC_TIPO_NOTA;DATA_EMISSAO;COD_SITUACAO_EMPENHO;DESC_SITUACAO_EMPENHO;VALOR_EMPENHO',
    'csv_columns_indexes': [0, 1, 2, 3, 4, 5, 6, 7],
    'table_name': 'empenho',
    'columns_to_insert': ["NR_CONVENIO", "NR_EMPENHO", "TIPO_NOTA", "DESC_TIPO_NOTA", "DATA_EMISSAO", "COD_SITUACAO_EMPENHO", "DESC_SITUACAO_EMPENHO", "VALOR_EMPENHO"],
    'insert_value_format': "({}, '{}', '{}', '{}', '{}', {}, '{}', {})",
    'row_formatters': [FORMAT_NUMBER] + [FORMAT_IDENTITY] * 2 + [FORMAT_ESCAPE_SINGLE_QUOTE] + [FORMAT_DATE] + [FORMAT_NUMBER] + [FORMAT_ESCAPE_SINGLE_QUOTE] + [FORMAT_NUMBER],
    'insert_command': "INSERT"
}

HISTORICO_SITUACAO_CONFIG = {
    'csv_file_name': 'siconv_historico_situacao',
    'csv_expected_header': 'ID_PROPOSTA;NR_CONVENIO;DIA_HISTORICO_SIT;HISTORICO_SIT;DIAS_HISTORICO_SIT;COD_HISTORICO_SIT',
    'csv_columns_indexes': [0, 1, 2, 3, 4, 5],
    'table_name': 'historico_situacao',
    'columns_to_insert': ["ID_PROPOSTA", "NR_CONVENIO", "DIA_HISTORICO_SIT", "HISTORICO_SIT", "DIAS_HISTORICO_SIT", "COD_HISTORICO_SIT"],
    'insert_value_format': "({}, {}, '{}', '{}', {}, {})",
    'row_formatters': [FORMAT_NUMBER] * 2 + [FORMAT_DATE] + [FORMAT_ESCAPE_SINGLE_QUOTE] + [FORMAT_NUMBER] * 2,
    'insert_command': "INSERT"
}

EMENDA_CONFIG = {
    'csv_file_name': 'siconv_emenda',
    'csv_expected_header': 'ID_PROPOSTA;QUALIF_PROPONENTE;COD_PROGRAMA_EMENDA;NR_EMENDA;NOME_PARLAMENTAR;BENEFICIARIO_EMENDA;IND_IMPOSITIVO;TIPO_PARLAMENTAR;VALOR_REPASSE_PROPOSTA_EMENDA;VALOR_REPASSE_EMENDA',
    'csv_columns_indexes': [0, 3, 5, 6, 8, 9],
    'table_name': 'emenda',
    'columns_to_insert': ["ID_PROPOSTA", "NR_EMENDA", "BENEFICIARIO_EMENDA", "IND_IMPOSITIVO", "VL_REPASSE_PROPOSTA_EMENDA", "VL_REPASSE_EMENDA"],
    'insert_value_format': "({}, {}, {}, '{}', {}, {})",
    'row_formatters': [FORMAT_NUMBER] * 3 + [FORMAT_IDENTITY] + [FORMAT_NUMBER] * 2,
    'insert_command': "INSERT"
}

PAGAMENTO_CONFIG = {
    'csv_file_name': 'siconv_pagamento',
    'csv_expected_header': 'NR_MOV_FIN;NR_CONVENIO;IDENTIF_FORNECEDOR;NOME_FORNECEDOR;TP_MOV_FINANCEIRA;DATA_PAG;NR_DL;DESC_DL;VL_PAGO',
    'csv_columns_indexes': [0, 1, 2, 4, 5, 6, 8],
    'table_name': 'pagamento',
    'columns_to_insert': ["NR_MOV_FIN", "NR_CONVENIO", "IDENTIF_FORNECEDOR", "TP_MOV_FINANCEIRA", "DATA_PAG", "NR_DL", "VL_PAGO"],
    'insert_value_format': "({}, {}, {}, '{}', {}, {})",
    'row_formatters': [FORMAT_NUMBER] * 3 + [FORMAT_IDENTITY] + [FORMAT_DATE] + [FORMAT_NUMBER] * 2,
    'insert_command': "INSERT"
}

DOCUMENTO_DE_LIQUIDACAO_CONFIG = {
    'csv_file_name': 'siconv_pagamento',
    'csv_expected_header': 'NR_MOV_FIN;NR_CONVENIO;IDENTIF_FORNECEDOR;NOME_FORNECEDOR;TP_MOV_FINANCEIRA;DATA_PAG;NR_DL;DESC_DL;VL_PAGO',
    'csv_columns_indexes': [6, 7],
    'table_name': 'documento_de_liquidacao',
    'columns_to_insert': ["NR_DL", "DESC_DL"],
    'insert_value_format': "({}, '{}')",
    'row_formatters': [FORMAT_NUMBER] + [FORMAT_IDENTITY],
    'insert_command': "INSERT"
}

FORNECEDOR_CONFIG = {
    'csv_file_name': 'siconv_pagamento',
    'csv_expected_header': 'NR_MOV_FIN;NR_CONVENIO;IDENTIF_FORNECEDOR;NOME_FORNECEDOR;TP_MOV_FINANCEIRA;DATA_PAG;NR_DL;DESC_DL;VL_PAGO',
    'csv_columns_indexes': [2, 3],
    'table_name': 'fornecedor',
    'columns_to_insert': ["IDENTIF_FORNECEDOR", "NOME_FORNECEDOR"],
    'insert_value_format': "({}, '{}')",
    'row_formatters': [FORMAT_NUMBER] + [FORMAT_IDENTITY],
    'insert_command': "INSERT"
}

OBTV_CONVENENTE_CONFIG = {
    'csv_file_name': 'siconv_obtv_convenente',
    'csv_expected_header': 'NR_MOV_FIN;IDENTIF_FAVORECIDO_OBTV_CONV;NM_FAVORECIDO_OBTV_CONV;TP_AQUISICAO;VL_PAGO_OBTV_CONV',
    'csv_columns_indexes': [0, 1, 3, 4],
    'table_name': 'obtv_convenente',
    'columns_to_insert': ["NR_MOV_FIN", "IDENTIF_FAVORECIDO_OBTV_CONV", "TP_AQUISICAO", "VL_PAGO_OBTV_CONV"],
    'insert_value_format': "({}, '{}', '{}', {})",
    'row_formatters': [FORMAT_NUMBER] + [FORMAT_IDENTITY] * 2 + [FORMAT_NUMBER],
    'insert_command': "INSERT"
}

FAVORECIDO_OBTV_CONFIG = {
    'csv_file_name': 'siconv_obtv_convenente',
    'csv_expected_header': 'NR_MOV_FIN;IDENTIF_FAVORECIDO_OBTV_CONV;NM_FAVORECIDO_OBTV_CONV;TP_AQUISICAO;VL_PAGO_OBTV_CONV',
    'csv_columns_indexes': [1, 2],
    'table_name': 'favorecido_obtv',
    'columns_to_insert': ["IDENTIF_FAVORECIDO_OBTV_CONV", "NM_FAVORECIDO_OBTV_CONV"],
    'insert_value_format': "('{}', '{}')",
    'row_formatters': [FORMAT_IDENTITY] * 2,
    'insert_command': "INSERT"
}

def insert_values_on_database(db_cursor, table_name, insert_command, columns_to_insert, insert_values):
    start = timeit.default_timer()
    insert_columns_name_statement = '(' + ','.join([('`' + column_name + '`') for column_name in columns_to_insert]) + ')'

    inserted_rows = 0
    total_rows = len(insert_values)
    while len(insert_values) > 0:
        batch_start = timeit.default_timer()
        next_batch_size = min(DEFAULT_BATCH_SIZE, len(insert_values))
        insert_values_batch = list()
        for i in range(next_batch_size):
            insert_values_batch.append(insert_values.pop(0))

        insert_sql_command = insert_command + ' INTO ' + table_name + ' ' + insert_columns_name_statement \
        + ' VALUES ' + ', '.join(insert_values_batch)
        #print(insert_sql_command)
        db_cursor.execute(insert_sql_command)
        inserted_rows += next_batch_size
        db.commit()
        batch_stop = timeit.default_timer()
        batch_time = batch_stop - batch_start
        print("Linhas inseridas/atualizadas em " + table_name + ": " + str(inserted_rows) + "/" + str(total_rows) + ' (' + str(batch_time) + 's)')
    stop = timeit.default_timer()
    time_spent = stop - start
    print('Tempo inserindo na tabela ' + table_name + ': ' + str(time_spent) + 's')

def format_csv_column(row, row_formatter):
    if row == '':
        return 'NULL'
    else:
        return row_formatter(row)

def build_insert_value(csv_row, row_formatters, insert_value_format):
    j = 0
    while j < len(csv_row):
        csv_row[j] = format_csv_column(csv_row[j],row_formatters[j])
        j += 1

    return insert_value_format.format(*csv_row).replace("'NULL'", 'NULL')

# Remove colunas que nao serao utilizadas
def filter_csv_row(csv_row, csv_columns_indexes):
    filtered_csv_row = list()
    for x in csv_columns_indexes:
        filtered_csv_row.append(csv_row[x])

    return filtered_csv_row

# converte csv para strings contendo um VALUE do sql
def convert_csv_to_sql_insert_values(config):
    file_name = config['csv_file_name']
    row_formatters = config['row_formatters']
    insert_value_format = config['insert_value_format']
    csv_columns_indexes = config['csv_columns_indexes']
    allow_null_columns = config.get('allow_null_columns', True)

    ifile = open('arquivos/' + file_name + '.csv', 'r', encoding="utf-8")
    reader = csv.reader(ifile, delimiter=';')

    insert_values = list()
    i = 0
    for csv_row in reader:
        # Coleta e valida o header
        if i == 0:
            header = ';'.join(csv_row)
            header = header.replace(u'\ufeff', '')
            if (header != config['csv_expected_header']):
                raise(Exception('Erro - ' + 'O header do csv ' + config['csv_file_name'] + ' está diferente do esperado: ' + header + ' x ' + config['csv_expected_header'] + ' (esperado)'))
        else:
            if not allow_null_columns and '' in csv_row:
                continue
            csv_row = filter_csv_row(csv_row, csv_columns_indexes)
            insert_values.append(build_insert_value(csv_row, row_formatters, insert_value_format))

        i += 1

    return insert_values

def process(db_cursor, config):
    start_build_insert = timeit.default_timer()
    insert_values_sql_part = convert_csv_to_sql_insert_values(config)
    stop_build_insert = timeit.default_timer()
    print('Entrada processada para tabela ' + config['table_name'] + ' em: ' + str(stop_build_insert - start_build_insert) + 's')

    insert_values_on_database(db_cursor, config['table_name'], config['insert_command'], config['columns_to_insert'], insert_values_sql_part)

if __name__ == '__main__':
    db = my.connect(
        host="127.0.0.1",
        user="root",
        passwd="",
        db="sinformedb", # Nome da Base de dados gerado pelo diagrama logico
        use_unicode = True,
        charset = "utf8"
    )
    db_cursor = db.cursor()

    #process(db_cursor, SENADORES_CONFIG)
    #process(db_cursor, DEPUTADOS_CONFIG)
    #process(db_cursor, ORGAO_SUP_CONFIG)
    #process(db_cursor, ORGAO_CONFIG)
    #process(db_cursor, MUNICIPIO_CONFIG)
    #process(db_cursor, PROPONENTE_CONFIG)
    #process(db_cursor, PROPOSTA_CONFIG)
    #process(db_cursor, CONVENIO_CONFIG)
    #process(db_cursor, DESEMBOLSO_CONFIG)
    #process(db_cursor, META_CONFIG)
    #process(db_cursor, TERMO_ADITIVO_CONFIG)
    #process(db_cursor, EMPENHO_CONFIG)
    # Terminar!
    #process(db_cursor, HISTORICO_SITUACAO_CONFIG)
    process(db_cursor, EMENDA_CONFIG)
