#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import MySQLdb

import timeit

from unicodedata import normalize

con = MySQLdb.connect(host='localhost', user='admin',passwd='admin123',db='sinformedb')
cursor = con.cursor()

def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII','ignore').decode('ASCII').upper()

def inserirBanco(cursor, nomeTabela, lista):
   cursor.execute("""INSERT INTO """ + nomeTabela + """ VALUES ("%s","%s","%s","%s","%s", %f, %f)""" % (lista[0],lista[1],lista[2],lista[3],lista[4],lista[5],lista[6] ) )
   con.commit()

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
		return -9999 # -9999 representa Vlaor inválido

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
                                return -8888.88 #"A string contem caracteres que nao sao numeros."
			
	except ValueError:
		return -9999.99 #"Erro"

def insertCSVinDB(fileName, tableName, headerDefault):
	ifile  = open('arquivos/'+fileName+'.csv', 'r', encoding="utf-8-sig") 
	read = csv.reader(ifile, delimiter=';')
	header = []
	excecaoElementos = [1,2,7]
        #listHeaderDefault = []
	#listHeaderDefault = headerDefault.split(";")
	rownum = 0
	try:
		for row in read:
			if rownum == 0:
				header = row
				resultHeader = checkHeader(header, headerDefault) # True or False
			elif resultHeader:
				print("ANTES === ",row)
				row[8] = strToFloat(row[8])
				row[9] = strToFloat(row[9])			
				
				for x in excecaoElementos[::-1]: #Inverte a lista antes de remover os elementos
					row.pop(x)
				print("DEPOIS === ",row)
				inserirBanco(cursor, tableName, row)
			else:
				print('Erro no Header do arquivo selecionado')				
				break
			rownum += 1
	except Exception as e:
		raise
	print("O numero de Emendas importadas foi:",rownum-1)
	ifile.close()

cabecalhoTabelaEmenda = "ID_PROPOSTA;QUALIF_PROPONENTE;COD_PROGRAMA_EMENDA;NR_EMENDA;NOME_PARLAMENTAR;BENEFICIARIO_EMENDA;IND_IMPOSITIVO;TIPO_PARLAMENTAR;VALOR_REPASSE_PROPOSTA_EMENDA;VALOR_REPASSE_EMENDA"

if __name__ == '__main__':
	#colocar nome do arquivo csv (sem a extensao)
	start = timeit.default_timer()
	nomeArqEmenda = 'siconv_emenda3'
	insertCSVinDB(nomeArqEmenda, 'EMENDA', cabecalhoTabelaEmenda)

	stop = timeit.default_timer() 
	print("Tempo de execucao: ",stop - start)


