#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import MySQLdb

import timeit

from unicodedata import normalize

con = MySQLdb.connect(host='localhost', user='admin', passwd='admin123', db='sinformedb')
cursor = con.cursor()


def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII').upper()


def inserirBanco(cursor, nomeTabela, lista):
    cursor.execute("""INSERT INTO """ + nomeTabela + """ (NOME, NOME_COMPLETO, SIGLA_PARTIDO, FUNCAO) VALUES 
    ("%s","%s","%s","%s")""" % (lista[0], lista[1], lista[2], lista[3] ) )
    
    '''cursor.execute(
        """INSERT INTO partido_parlamentar (nome_sem_acento, nome_completo, sigla_partido) VALUES ("%s","%s","%s")""" % (
        lista[0], lista[1], lista[2]))'''
    con.commit()


def checkHeader(listHeader, defaultHeader):
    textHeader = ';'.join(listHeader)
    if textHeader == defaultHeader:
        return True
    else:
        return False


def insertCSVinDB(fileName, tableName, headerDefault, parlamentar):
    ifile = open('arquivos/' + fileName + '.csv', 'r')
    read = csv.reader(ifile, delimiter=';')
    header = []
    rownum = 0
    try:
        for row in read:
            if rownum == 0:
                header = row
                resultHeader = checkHeader(header, headerDefault)  # True or False
            elif resultHeader:
                if parlamentar == 's':
                    listRowDB = [remover_acentos(row[1]), remover_acentos(row[2]), row[8], "SENADOR"]
                elif parlamentar == 'd':
                    listRowDB = [row[14], remover_acentos(row[16]), row[1], "DEPUTADO"]
                else:
                    print("Ocorreu um erro no tipo de parlamentar escolhido.")
                    break
                inserirBanco(cursor, tableName, listRowDB)
            else:
                print('Erro no Header do arquivo selecionado')
                break
            rownum += 1
    except Exception as e:
        raise

    ifile.close()


cabecalhoTabelaSenadores = "IdentificacaoParlamentar/CodigoParlamentar;IdentificacaoParlamentar/NomeParlamentar;IdentificacaoParlamentar/NomeCompletoParlamentar;IdentificacaoParlamentar/SexoParlamentar;IdentificacaoParlamentar/FormaTratamento;IdentificacaoParlamentar/UrlFotoParlamentar;IdentificacaoParlamentar/UrlPaginaParlamentar;IdentificacaoParlamentar/EmailParlamentar;IdentificacaoParlamentar/SiglaPartidoParlamentar;IdentificacaoParlamentar/UfParlamentar;Mandato/CodigoMandato;Mandato/UfParlamentar;Mandato/PrimeiraLegislaturaDoMandato/NumeroLegislatura;Mandato/PrimeiraLegislaturaDoMandato/DataInicio;Mandato/PrimeiraLegislaturaDoMandato/DataFim;Mandato/SegundaLegislaturaDoMandato/NumeroLegislatura;Mandato/SegundaLegislaturaDoMandato/DataInicio;Mandato/SegundaLegislaturaDoMandato/DataFim;Mandato/DescricaoParticipacao;Mandato/Suplentes/Suplente/0/DescricaoParticipacao;Mandato/Suplentes/Suplente/0/CodigoParlamentar;Mandato/Suplentes/Suplente/0/NomeParlamentar;Mandato/Suplentes/Suplente/1/DescricaoParticipacao;Mandato/Suplentes/Suplente/1/CodigoParlamentar;Mandato/Suplentes/Suplente/1/NomeParlamentar;Mandato/Exercicios/Exercicio/0/CodigoExercicio;Mandato/Exercicios/Exercicio/0/DataInicio;Mandato/Exercicios/Exercicio/1/CodigoExercicio;Mandato/Exercicios/Exercicio/1/DataInicio;Mandato/Exercicios/Exercicio/1/DataFim;Mandato/Exercicios/Exercicio/1/SiglaCausaAfastamento;Mandato/Exercicios/Exercicio/1/DescricaoCausaAfastamento;UrlGlossario;Mandato/Titular/DescricaoParticipacao;Mandato/Titular/CodigoParlamentar;Mandato/Titular/NomeParlamentar;Mandato/Exercicios/Exercicio/2/CodigoExercicio;Mandato/Exercicios/Exercicio/2/DataInicio;Mandato/Exercicios/Exercicio/2/DataFim;Mandato/Exercicios/Exercicio/2/SiglaCausaAfastamento;Mandato/Exercicios/Exercicio/2/DescricaoCausaAfastamento;Mandato/Exercicios/Exercicio/0/DataLeitura;Mandato/Exercicios/Exercicio/1/DataLeitura;Mandato/Exercicios/Exercicio/3/CodigoExercicio;Mandato/Exercicios/Exercicio/3/DataInicio;Mandato/Exercicios/Exercicio/3/DataFim;Mandato/Exercicios/Exercicio/3/SiglaCausaAfastamento;Mandato/Exercicios/Exercicio/3/DescricaoCausaAfastamento;Mandato/Exercicios/Exercicio/4/CodigoExercicio;Mandato/Exercicios/Exercicio/4/DataInicio;Mandato/Exercicios/Exercicio/4/DataFim;Mandato/Exercicios/Exercicio/4/SiglaCausaAfastamento;Mandato/Exercicios/Exercicio/4/DescricaoCausaAfastamento;Mandato/Exercicios/Exercicio/2/DataLeitura"

cabecalhoTabelaDeputados = "Nome Parlamentar;Partido;UF;Titular/Suplente/Efetivado;Endereço;Anexo;Endereço (continuação);Gabinete;Endereço (complemento);Telefone;Fax;Mês Aniversário;Dia Aniversário;Correio Eletrônico;Nome sem Acento;Tratamento;Nome Civil"

if __name__ == '__main__':
    start = timeit.default_timer()
    # colocar nome do arquivo csv (sem a extensao)
    print("UC01 - Senadores e Deputados ")
    print("Importação sendo executada ... ")
    nomeArqSenadores = 'senadores'
    insertCSVinDB(nomeArqSenadores, 'PARLAMENTAR', cabecalhoTabelaSenadores, 's')
    nomeArqDeputados = 'deputado'
    insertCSVinDB(nomeArqDeputados, 'PARLAMENTAR', cabecalhoTabelaDeputados, 'd')
    
    stop = timeit.default_timer()
    print("Tempo de execucao: ", stop - start)
