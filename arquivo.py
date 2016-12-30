# -*- coding: utf-8 -*-

"""
 Arquivo que agrupa todas as funções de manipulação dos arquivos
 necessários ao servidor.

 A implementação é thread-safe, isto é, foi feita pensando em
 suportar o uso simultâneo por diversas threads.
"""

import threading
from modelos import Usuario

arquivo_usuarios = 'usuarios.txt'


class Gerenciador:

    def __init__(self):
        self.semaforo_usuarios = threading.Semaphore(1)
        self.semaforo_lances = threading.Semaphore(1)

    def get_usuario_por_nome(self, nome):
        with self.semaforo_usuarios:
            with open(arquivo_usuarios, 'r') as f:
                for linha in f:
                    usuario_linha = Usuario.texto_para_usuario(linha)
                    if usuario_linha.nome == nome:
                        return usuario_linha
        return None

    def escreve_usuario(self, u):
        with self.semaforo_usuarios:
            with open(arquivo_usuarios, "a") as f:
                f.write(str(u) + '\n')

    def get_listagem_leiloes(self):
        return []

    # http://stackoverflow.com/questions/4914277/how-to-empty-a-file-using-python
    def apagar_todos(self):
        with self.semaforo_usuarios:
            open(arquivo_usuarios, 'w').close()
