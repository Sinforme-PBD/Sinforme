#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pip install mysqlclient
import MySQLdb as my
import csv


# esta funcao pode ser usada em todos so casos de uso ;-)
def gravarDados(tabela, header, insert):
    db = my.connect(
        host="127.0.0.1",
        user="root",
        passwd="",
        db="siconvdb"  # Nome da Base de dados gerado pelo diagrama logico
    )

    sql = 'INSERT INTO ' + tabela + ' VALUES (' + ('%s,' * len(header))[0:-1] + ')'

    cursor = db.cursor()
    number_of_rows = cursor.executemany(sql, insert)
    db.commit()
    db.close()


# converte csv para listas
def convertCSVToSQLScript(file):
    ifile = open(file + '.csv', 'r', encoding="utf-8-sig")  # , encoding="utf8" ,latin1,  'ascii', 'iso-8859-1'
    read = csv.reader(ifile, delimiter=';')  # , quotechar='|'

    excecao = ['NR_PROCESSO', 'UG_EMITENTE', 'VL_EMPENHADO_CONV']  # atributos que nao seram usados
    excecaoValor = [11, 12, 25]  # index dos atributos que nao seram usados

    insert = list()
    i = 0

    for row in read:
        if i == 0:
            header = row
        else:
            j = 0
            while j < len(row):

                row[j] = row[j].replace('******', '')

                if row[j] == '':
                    row[j] = 'null'
                elif row[j].replace(',', '').isdigit() and ',' in row[j]:
                    row[j] = row[j].replace(',', '.')
                elif row[j].count('/') == 2 and row[j].replace('/', '').isdigit():
                    row[j] = '-'.join(row[j].split('/')[::-1])
                else:
                    row[j] = row[j]
                j += 1

            for x in excecaoValor[::-1]:
                row.pop(x)

            insert.append(tuple(row))

        i += 1

    for x in excecao:
        header.remove(x);

    return header, insert


if __name__ == '__main__':
    banco = convertCSVToSQLScript('siconv_convenio')
    gravarDados('convenio', banco[0], banco[1])
