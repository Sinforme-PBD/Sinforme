#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import MySQLdb as my
import csv


class treta_db(object):

	def __init__(self, db, host, user, passwd=""):
		self._db = db
		self._host = host
		self._user = user
		self._passwd = passwd

	def _getconn(self):
		"""Retorna uma coneção"""
		return my.connect(host = self._host,user = self._user,passwd = self._passwd,db = self._db)


	def _limpesa(self, L):
		"""Converte vazio strings para null."""
		def f(x):
			x = x.replace('******','')
			x = x.replace('"', '')

			if(x == ""):
				return 'null'
			elif (',' in x and x.replace(',','').isdigit()):
				return x.replace(',','.')
			elif (x.count('/')==2 and x.replace('/','').isdigit()):
				return '-'.join(row[j].split('/')[::-1])
			else:
				return x
		return [f(x) for x in L]


	def _save(self, tabela, header, insert):
		""" """
		query = ("INSERT INTO %s (%s)" % (tabela,','.join(header))) + (" VALUES (%s)" % ((len(insert)-1) * "%s, " + "%s"))
		db = self._getconn()

		try:
			cursor = db.cursor()
			cursor.execute(query, insert)
			db.commit()
		except:
			db.rollback()
		db.close()


	def ReaderrCSV(self, file, tabelaNome, excecao):
		"""converte csv para listas"""
		ifile  = open(file+'.csv', 'r', encoding ="utf-8-sig")
		read = csv.reader(ifile, delimiter=';')

		#excecaoValor = list() #index dos atributos que nao seram usados
		excluir = list() #index dos atributos que nao seram usados

		i = 0
		for row in read :
			if i == 0:
				header = row
				for x in header:
					if not x in excecao:
						excluir.append(header.index(x))
			else:
				for x in excluir[::-1]:
					row.pop(x)
				self._save(tabelaNome, excecao, self._limpesa(row))
			i+=1