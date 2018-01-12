#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from treta_db import siconv as treta
import os


if __name__ == '__main__':
	tretaDB = treta.treta_db(db="sinformedb", host="localhost", user="root", passwd="")

	#atributos = ['COD_ORGAO','DESC_ORGAO']
	#tretaDB.ReaderrCSV(os.path.abspath("")+"\\"+'siconv_proposta', 'orgao', atributos)


	""" UC04 """
	atributos = ['NR_PROCESSO', 'UG_EMITENTE', 'VL_EMPENHADO_CONV']
	tretaDB.ReaderrCSV(os.path.abspath("")+"\\"+'siconv_convenio', 'convenio', atributos)
