# -*- coding: utf-8 -*-

"""
 Arquivo que agrupa todas as funções de manipulação dos arquivos
 necessários ao servidor.

 A implementação é thread-safe, isto é, foi feita pensando em
 suportar o uso simultâneo por diversas threads.
"""

import threading
from usuario import Usuario
from leilao import Leilao

arquivo_usuarios = 'usuarios.txt'
arquivo_leiloes = 'leiloes.txt'


class Gerenciador:

    def __init__(self):
        self.semaforo_usuarios = threading.Semaphore(1)
        self.semaforo_leiloes = threading.Semaphore(1)
        # Cria arquivos se não existirem
        # http://stackoverflow.com/questions/2967194/open-in-python-does-not-create-a-file-if-it-doesnt-exist
        open(arquivo_usuarios, 'a+').close()
        open(arquivo_leiloes, 'a+').close()

    def get_usuario_por_nome(self, nome):
        with self.semaforo_usuarios:
            with open(arquivo_usuarios, 'r') as f:
                for linha in f:
                    if linha != '\n':
                        usuario_linha = Usuario.texto_para_usuario(linha)
                        if usuario_linha.nome == nome:
                            return usuario_linha
        return None

    def salva_usuario(self, u):
        with self.semaforo_usuarios:
            with open(arquivo_usuarios, "a") as f:
                f.write(str(u) + '\n')

    def get_leilao_por_identificador(self, identificador):
        with self.semaforo_leiloes:
            with open(arquivo_leiloes, 'r') as f:
                for linha in f:
                    if linha != '\n':
                        leilao_linha = Leilao.texto_para_leilao(linha)
                        if leilao_linha.identificador == identificador:
                            return leilao_linha
        return None

    def salva_leilao(self, leilao):
        with self.semaforo_leiloes:
            novo_identificador = None
            with open(arquivo_leiloes, "r") as f:
                linhas = f.readlines()
                if len(linhas) > 0:
                    ultimo_leilao_criado = Leilao.texto_para_leilao(linhas[-1])
                    novo_identificador = ultimo_leilao_criado.identificador + 1
                else:
                    novo_identificador = 1
            leilao.set_identificador(novo_identificador)
            with open(arquivo_leiloes, "a") as f:
                f.write(str(leilao) + '\n')

    def get_listagem_leiloes(self):
        return []

    # http://stackoverflow.com/questions/4914277/how-to-empty-a-file-using-python
    def apagar_todos(self):
        with self.semaforo_usuarios:
            open(arquivo_usuarios, 'w').close()
        with self.semaforo_leiloes:
            open(arquivo_leiloes, 'w').close()
