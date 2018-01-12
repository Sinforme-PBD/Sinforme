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
    cursor.execute("""INSERT INTO """ + nomeTabela + """ VALUES ("%s","%s","%d","%s","%s", %f, %f)""" % (
    lista[0], lista[1], lista[2], lista[3], lista[4], lista[5], lista[6]))
    con.commit()

def consultarBanco (cursor, nomeTabela, nomeColuna1, nomeColuna2, valor):
    print("valor ===",valor)
    try:
        cursor.execute("""SELECT """ + nomeColuna1 + """ FROM """ + nomeTabela + """ WHERE """ + nomeColuna2 + """ = '%s'""" % valor )    
        result = cursor.fetchone()[0]
    except TypeError as e:
        print(e)
        result = None   
    return result

def checkHeader(listHeader, defaultHeader):
    listDefault = defaultHeader.split(";")
    if listHeader == listDefault:
        return True
    else:
        return False

def checkValue(value):
    if value.isdigit():
        return int(value)
    else:
        return -9999  # -9999 representa Valor inválido


def strToFloat(texto):
    texto = texto.replace(" ", "")
    if texto == "":
        texto = "0.0"
    elif texto.count(",") == 1:
        texto = texto.replace(",", ".")
    try:
        if texto.count(".") <= 1:
            if texto.replace(".", "").isdigit():
                return float(texto)
            else:
                return -8888.88  # "A string contem caracteres que nao sao numeros."

    except ValueError:
        return -9999.99  # "Erro"


def insertCSVinDB(fileName, tableName, headerDefault):
    ifile = open('arquivos/' + fileName + '.csv', 'r', encoding="utf-8-sig")
    read = csv.reader(ifile, delimiter=';')
    header = []
    excecaoElementosEmenda = [1, 2, 7]
    rownum = 0
    try:
        for row in read:
            if rownum == 0:
                header = row
                resultHeader = checkHeader(header, headerDefault)  # True or False
            elif resultHeader:
                #Geracao da tabela Emenda 
                row[4] = consultarBanco(cursor, 'PARLAMENTAR', 'ID_PARLAMENTAR', 'NOME', row[4] )
                print("row4 == ",row[4])
                if row[7] == 'INDIVIDUAL' and row[4] != None:
                    row[8] = strToFloat(row[8])
                    row[9] = strToFloat(row[9])
                    for x in excecaoElementosEmenda[::-1]:  # Inverte a lista antes de remover os elementos
                        row.pop(x)
                    inserirBanco(cursor, tableName, row)
            else:
                print('Erro no Header do arquivo selecionado')
                break
            rownum += 1
    except Exception as e:
        raise
    print("O numero de Emendas importadas foi:", rownum - 1)
    ifile.close()
    con.close()

cabecalhoTabelaEmenda = "ID_PROPOSTA;QUALIF_PROPONENTE;COD_PROGRAMA_EMENDA;NR_EMENDA;NOME_PARLAMENTAR;BENEFICIARIO_EMENDA;IND_IMPOSITIVO;TIPO_PARLAMENTAR;VALOR_REPASSE_PROPOSTA_EMENDA;VALOR_REPASSE_EMENDA"

if __name__ == '__main__':
    # colocar nome do arquivo csv (sem a extensao)
    start = timeit.default_timer()
    nomeArqEmenda = 'siconv_emenda3'
    insertCSVinDB(nomeArqEmenda, 'EMENDA', cabecalhoTabelaEmenda)
    stop = timeit.default_timer()
    print("Tempo de execucao: ", stop - start)
