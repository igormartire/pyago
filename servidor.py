# -*- coding: utf-8 -*-

import socket
import threading
from usuario import Usuario
from leilao import Leilao
import arquivo
from constantes import (MSG_FAZ_LOGIN,
                        MSG_LISTA_LEILOES,
                        MSG_ADICIONA_USUARIO,
                        MSG_LISTAGEM,
                        MSG_LANCA_PRODUTO,
                        MSG_ENTRAR_LEILAO,
                        MSG_ENVIAR_LANCE)


semaforo_lance = threading.Semaphore(1)


class Servidor:

    def __init__(self, host='localhost', porta=8888, verbose=False):
        self.verbose = verbose
        self.log('Iniciando...')
        self.host = host
        self.porta = porta
        self.socket_escuta = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_escuta.setsockopt(socket.SOL_SOCKET,
                                      socket.SO_REUSEADDR, 1)
        self.socket_escuta.bind((host, porta))
        self.socket_escuta.listen(5)
        self.arquivo = arquivo.Gerenciador()
        self.rodando = True
        self.thread_escuta = threading.Thread(target=self.escuta)
        self.thread_escuta.start()
        self.log('Esperando por novas conexões na porta %s ...' % porta)

    def escuta(self):
        while self.rodando:
            conexao, endereco = self.socket_escuta.accept()
            if self.rodando:
                Conexao(conexao, endereco, self.arquivo, self.verbose)

    def parar(self):
        self.log("Encerrando...")
        self.rodando = False
        cliente_falso = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_falso.connect((self.host, self.porta))
        cliente_falso.close()
        self.thread_escuta.join()
        self.socket_escuta.close()
        self.log("Encerrado.")

    def log(self, msg):
        if self.verbose:
            print "Servidor: %s" % msg


class Conexao:

    count = 0

    def __init__(self, conexao, endereco, arquivo, verbose=False):
        Conexao.count += 1
        self.id = Conexao.count
        self.conexao = conexao
        self.endereco = endereco
        self.arquivo = arquivo
        self.verbose = verbose
        self.logado = False
        self.usuario = None
        self.leiloes = set([])
        self.log("Iniciando conexão com %s" % str(endereco))
        t = threading.Thread(target=self.lidar_com_cliente)
        t.start()

    def parar(self):
        self.log("Encerrando conexão com %s" % str(self.endereco))
        self.conexao.close()

    def lidar_com_cliente(self):
        try:
            mensagem = self.conexao.recv(4096)
            while mensagem != '':
                self.log(mensagem)
                campos = mensagem.split(',')

                if campos[0] == MSG_ADICIONA_USUARIO:
                    self.adiciona_usuario(*campos[1:])
                elif campos[0] == MSG_FAZ_LOGIN:
                    self.faz_login(*campos[1:])
                elif campos[0] == MSG_LISTA_LEILOES:
                    self.lista_leiloes()
                elif campos[0] == MSG_LANCA_PRODUTO:
                    self.lanca_produto(*campos[1:])
                elif campos[0] == MSG_ENTRAR_LEILAO:
                    self.entrar_leilao(*campos[1:])
                elif campos[0] == MSG_ENVIAR_LANCE:
                    self.enviar_lance(*campos[1:])

                mensagem = self.conexao.recv(4096)
        finally:
            self.parar()

    def adiciona_usuario(self, nome, telefone, endereco, email, senha):
        try:
            u = self.arquivo.get_usuario_por_nome(nome)
            if u is not None:
                self.responde_erro()
            else:
                new_u = Usuario(nome, telefone, endereco, email, senha)
                self.arquivo.salva_usuario(new_u)
                self.responde_sucesso()
        except ValueError:
            self.responde_erro()

    def faz_login(self, nome, senha):
        if self.logado:
            self.responde_erro()
            return

        u = self.arquivo.get_usuario_por_nome(nome)
        if u is not None and u.senha == senha:
            self.logado = True
            self.usuario = u
            self.responde_sucesso()
        else:
            self.responde_erro()

    def lista_leiloes(self):
        leiloes = self.arquivo.get_listagem_leiloes()
        leiloes_nao_finalizados = filter(lambda l: not l.finalizado(), leiloes)
        if leiloes_nao_finalizados:
            listagem = ','.join(map(str, leiloes_nao_finalizados))
            self.conexao.sendall(MSG_LISTAGEM + ',' + listagem)
        else:
            self.conexao.sendall(MSG_LISTAGEM)

    def lanca_produto(self, nome, descricao, lance_minimo,
                      datahora_inicio, tempo_max_sem_lances):
        if not self.logado:
            self.responde_erro()
            return
        try:
            self.arquivo.cria_leilao(
                nome, descricao, lance_minimo, datahora_inicio,
                tempo_max_sem_lances, self.usuario.nome
            )
            self.responde_sucesso()
        except ValueError:
            self.responde_erro()

    def entrar_leilao(self, identificador_leilao):
        if not self.logado:
            self.responde_erro()
            return

        id_leilao = int(identificador_leilao)
        l = self.arquivo.get_leilao_por_identificador(id_leilao)
        if l is None or not l.entrada_permitida():
            self.responde_erro()
        else:
            self.leiloes.add(identificador_leilao)
            self.responde_sucesso()

    def enviar_lance(self, identificador_leilao, valor):
        if not self.logado:
            self.responde_erro()
            return

        with semaforo_lance:
            id_leilao = int(identificador_leilao)
            if id_leilao not in self.leiloes:
                self.return_erro()
            else:
                ok = self.arquivo.lance(
                    id_leilao, float(valor), self.usuario.nome
                )
                if ok:
                    self.responde_sucesso()
                else:
                    self.responde_erro()

    def responde_erro(self):
        self.conexao.sendall('not_ok')

    def responde_sucesso(self):
        self.conexao.sendall('ok')

    def log(self, msg):
        if self.verbose:
            print 'Cliente %d: %s' % (self.id, msg)


if __name__ == '__main__':
    servidor = Servidor(verbose=True)
    try:
        raw_input('Pressione Enter para encerrar o servidor.\n')
    except KeyboardInterrupt:
        pass
    servidor.parar()
