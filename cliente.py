# -*- coding: utf-8 -*-

import socket
from modelos import Usuario
from constantes import (MSG_FAZ_LOGIN,
                        MSG_LISTA_LEILOES,
                        MSG_ADICIONA_USUARIO)

class Cliente:

    def __init__(self, ip="localhost", porta=8888, timeout=0):
        self.timeout = timeout
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, porta))
        if timeout > 0:
            self.socket.settimeout(timeout)

    def adiciona_usuario(self, usuario):
        self.envia_mensagem(MSG_ADICIONA_USUARIO,
                            usuario.nome, usuario.telefone,
                            usuario.endereco, usuario.email, usuario.senha)
        return self.recebe_resposta() == 'ok'

    def login(self, nome, senha):
        self.envia_mensagem(MSG_FAZ_LOGIN, nome, senha)
        return self.recebe_resposta() == 'ok'

    def lista_leiloes(self):
        self.envia_mensagem(MSG_LISTA_LEILOES)
        return self.recebe_resposta()

    def envia_mensagem(self, *campos):
        self.socket.sendall(','.join(campos))

    def recebe_resposta(self, tamanho=32768):
        return self.socket.recv(tamanho)

    def sair(self):
        self.envia_mensagem('Sair')
        return self.recebe_resposta()

    def fechar(self):
        self.socket.close()


def main():
    ip = "localhost"
    porta = 8888

    cliente = Cliente(ip, porta, 5)
    print 'Bem-vindo ao melhor leilão de Telecom'

    logado = False
    while not logado:
        print 'Escolha uma das opções:'
        print '\t1- Adicionar usuário'
        print '\t2- Entrar'
        print '\t3- Listar leilões'
        print '\t4- Fechar'
        opcao = raw_input('\tDigite o número da sua opção: ')
        if opcao == '1':
            u = pede_usuario()
            ok = cliente.adiciona_usuario(u)
            if ok:
                print 'Usuário criado com sucesso!'
                continue
            else:
                print 'Falha na criação do usuário!'
                continue
        elif opcao == '2':
            nome = raw_input('Entre com o nome: ')
            senha = raw_input('Entre com a senha: ')
            ok = cliente.login(nome, senha)
            if ok:
                print 'Logado com sucesso.'
                logado = True
            else:
                print 'Falha no login.'
        elif opcao == '3':
            # Ainda não foi implementado!!
            pass
        elif opcao == '4':
            print 'Até mais. Volte sempre.'
            cliente.fechar()
            return
        else:
            print 'Opção inválida. Digite o número de uma das opções acima.'


def pede_usuario():
    nome = raw_input('Entre com o nome: ')
    telefone = raw_input('Entre com o telefone: ')
    endereco = raw_input('Entre com o endereço: ')
    email = raw_input('Entre com o email: ')
    senha = raw_input('Entre com a senha: ')
    return Usuario(nome, telefone, endereco, email, senha)

if __name__ == "__main__":
    main()
