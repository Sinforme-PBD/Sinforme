import MySQLdb as my
import csv
from unicodedata import normalize
import timeit



if __name__ == '__main__':
    
    db = my.connect(
        host="127.0.0.1",
        user="root",
        passwd="admin",
        db="sinformedb",  # Nome da Base de dados gerado pelo diagrama logico
        use_unicode = True,
        charset = "utf8"
    )
    db_cursor = db.cursor()
    
    while opcao != 'x':
        print("************** SINFORMEDB **************")
        print("1 - Consulta por Parlamentar")
        print("2 - Consulta por Orgao")
        print("3 - Consulta por Beneficiario")
        print("4 - Listar os Parlamentares Outliers")
        print("x - Consulta por Parlamentar")
        opcao = input("Digite umas das opcoes acima:")
        
        if opcao == '1':
            #cod
            parlamentar = input("Digite parte do nome do Parlamentar:")
            
            
        elif opcao == '2':
            pass       
        elif opcao == '3':
            pass 
        elif opcao == '4':
            pass
        elif opcao == 'x':
            break 
        else:
            print("Opcao Invalida.")        
        
    
    
