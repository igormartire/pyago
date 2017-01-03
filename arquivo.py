# -*- coding: utf-8 -*-

"""
 Arquivo que agrupa todas as funções de manipulação dos arquivos
 necessárias ao servidor.

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
        self.cria_arquivos_caso_nao_existam()
        # Jusitificativa do uso de semáforos: estes dois semáforos são
        # responsáveis por proteger os arquivos que guardam os usuários e os
        # leilões. Como são arquivos compartilhados por diversas threads (as
        # threads que lidam com os diversos clientes), há necessidade do uso
        # de semáforos para garantir que duas threads não estejam acessando
        # o mesmo arquivo ao mesmo tempo. Assim, sempre antes de usar os
        # arquivos para leitura e/ou escrita nós usamos o semáforo para
        # para adquirirmos o lock sobre o arquivo e assim garantir que só
        # uma thread por vez tem acesso ao arquivo.
        self.semaforo_usuarios = threading.Semaphore(1)
        self.semaforo_leiloes = threading.Semaphore(1)

    # http://stackoverflow.com/questions/2967194/open-in-python-does-not-create-a-file-if-it-doesnt-exist
    def cria_arquivos_caso_nao_existam(self):
        open(arquivo_usuarios, 'a+').close()
        open(arquivo_leiloes, 'a+').close()

    # http://stackoverflow.com/questions/4914277/how-to-empty-a-file-using-python
    def apagar_todos(self):
        with self.semaforo_usuarios:
            open(arquivo_usuarios, 'w').close()
        with self.semaforo_leiloes:
            open(arquivo_leiloes, 'w').close()

    #########################################
    #  Funções relacionadas a usuários
    #########################################

    def get_usuario_por_nome(self, nome):
        with self.semaforo_usuarios:
            with open(arquivo_usuarios, 'r') as f:
                for linha in f:
                    if linha != '\n':
                        usuario_linha = Usuario.texto_para_usuario(linha)
                        if usuario_linha.nome == nome:
                            return usuario_linha
        return None

    def get_ids_leiloes_dos_quais_o_usuario_participa(self, nome_usuario):
        with self.semaforo_usuarios:
            with open(arquivo_usuarios, 'r') as f:
                for linha in f:
                    if linha != '\n':
                        usuario_linha = Usuario.texto_para_usuario(linha)
                        if usuario_linha.nome == nome_usuario:
                            return usuario_linha.ids_leiloes_participando
        return None

    def salva_usuario(self, u):
        with self.semaforo_usuarios:
            with open(arquivo_usuarios, "a") as f:
                f.write(str(u) + '\n')

    def apaga_usuario(self, nome, senha):
        with self.semaforo_usuarios:
            achou = False
            usuarios = []
            with open(arquivo_usuarios, 'r') as f:
                for linha in f:
                    if linha != '\n':
                        usuario_linha = Usuario.texto_para_usuario(linha)
                        if usuario_linha.nome == nome:
                            achou = True
                            if senha != usuario_linha.senha:
                                return False
                        else:
                            usuarios.append(usuario_linha)
            if not achou:
                return False
            with open(arquivo_usuarios, 'w') as f:
                for usuario in usuarios:
                    f.write(str(usuario) + '\n')
            return True

    #########################################
    #  Funções relacionadas a leilões
    #########################################

    def get_leilao_por_identificador(self, identificador):
        with self.semaforo_leiloes:
            with open(arquivo_leiloes, 'r') as f:
                for linha in f:
                    if linha != '\n':
                        leilao_linha = Leilao.texto_para_leilao(linha)
                        if leilao_linha.identificador == identificador:
                            return leilao_linha
        return None

    def get_listagem_leiloes(self):
        listagem = []
        with self.semaforo_leiloes:
            with open(arquivo_leiloes, 'r') as f:
                for linha in f:
                    if linha != '\n':
                        leilao_linha = Leilao.texto_para_leilao(linha)
                        listagem.append(leilao_linha)
        return listagem

    # Salva o leilão no arquivo e associa ao mesmo um identificador único
    def cria_leilao(self, nome, descricao, lance_minimo,
                    datahora_inicio, tempo_max_sem_lances, nome_dono):
        leilao = Leilao(
            nome, descricao, float(lance_minimo),
            datahora_inicio, int(tempo_max_sem_lances), nome_dono
        )
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

    def lance_leilao(self, identificador_leilao, valor, nome_autor):
        with self.semaforo_leiloes:
            leiloes = []
            with open(arquivo_leiloes, 'r') as f:
                for linha in f:
                    if linha != '\n':
                        leilao_linha = Leilao.texto_para_leilao(linha)
                        if leilao_linha.identificador == identificador_leilao:
                            lance_ok = leilao_linha.lance(valor, nome_autor)
                            if not lance_ok:
                                return False
                        leiloes.append(leilao_linha)
            with open(arquivo_leiloes, 'w') as f:
                for leilao in leiloes:
                    f.write(str(leilao) + '\n')
            return True

    #########################################
    #  Funções relacionadas a usuários e leilões simultaneamente
    #########################################

    # Ingressa o usuario no leilão, incrementando o contador de usuários
    # participantes do leilão e adicionando o leilão na lista de leilões
    # que o usuário participa
    def entrar_leilao(self, nome_usuario, identificador_leilao):
        with self.semaforo_usuarios, self.semaforo_leiloes:
            usuarios = []
            with open(arquivo_usuarios, 'r') as f:
                for linha in f:
                    if linha != '\n':
                        usuario_linha = Usuario.texto_para_usuario(linha)
                        if usuario_linha.nome == nome_usuario:
                            if identificador_leilao in \
                               usuario_linha.ids_leiloes_participando:
                                return True
                            usuario_linha.ids_leiloes_participando\
                                         .add(identificador_leilao)
                        usuarios.append(usuario_linha)
            achou = False
            leiloes = []
            with open(arquivo_leiloes, 'r') as f:
                for linha in f:
                    if linha != '\n':
                        leilao_linha = Leilao.texto_para_leilao(linha)
                        if leilao_linha.identificador == identificador_leilao:
                            achou = True
                            if not leilao_linha.entrada_permitida():
                                return False
                            else:
                                leilao_linha.numero_usuarios += 1
                        leiloes.append(leilao_linha)
            if not achou:
                return False
            with open(arquivo_usuarios, 'w') as f:
                for usuario in usuarios:
                    f.write(str(usuario) + '\n')
            with open(arquivo_leiloes, 'w') as f:
                for leilao in leiloes:
                    f.write(str(leilao) + '\n')
            return True

    # Retira o usuario do leilão, decrementando o contador de usuários
    # participantes do leilão e removendo o leilão da lista de leilões
    # que o usuário participa
    def sair_leilao(self, nome_usuario, identificador_leilao):
        with self.semaforo_usuarios, self.semaforo_leiloes:
            usuarios = []
            with open(arquivo_usuarios, 'r') as f:
                for linha in f:
                    if linha != '\n':
                        usuario_linha = Usuario.texto_para_usuario(linha)
                        if usuario_linha.nome == nome_usuario:
                            if identificador_leilao not in \
                               usuario_linha.ids_leiloes_participando:
                                return False
                            else:
                                usuario_linha.ids_leiloes_participando \
                                             .remove(identificador_leilao)
                        usuarios.append(usuario_linha)
            achou = False
            leiloes = []
            with open(arquivo_leiloes, 'r') as f:
                for linha in f:
                    if linha != '\n':
                        leilao_linha = Leilao.texto_para_leilao(linha)
                        if leilao_linha.identificador == identificador_leilao:
                            achou = True
                            leilao_linha.numero_usuarios -= 1
                        leiloes.append(leilao_linha)
            if not achou:
                return False
            with open(arquivo_usuarios, 'w') as f:
                for usuario in usuarios:
                    f.write(str(usuario) + '\n')
            with open(arquivo_leiloes, 'w') as f:
                for leilao in leiloes:
                    f.write(str(leilao) + '\n')
            return True
