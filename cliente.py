# -*- coding: utf-8 -*-

import socket
from usuario import Usuario
from constantes import (MSG_FAZ_LOGIN,
                        MSG_LISTA_LEILOES,
                        MSG_ADICIONA_USUARIO,
                        MSG_LANCA_PRODUTO,
                        MSG_ENTRAR_LEILAO,
                        MSG_ENVIAR_LANCE)


class Cliente:

    def __init__(self, ip="localhost", porta=8888, timeout=0):
        self.timeout = timeout
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, porta))
        self.logado = False
        self.nome_usuario = None
        if timeout > 0:
            self.socket.settimeout(timeout)

    def adiciona_usuario(self, usuario):
        self.envia_mensagem(MSG_ADICIONA_USUARIO,
                            usuario.nome, usuario.telefone,
                            usuario.endereco, usuario.email, usuario.senha)
        return self.recebe_resposta() == 'ok'

    def faz_login(self, nome, senha):
        self.envia_mensagem(MSG_FAZ_LOGIN, nome, senha)
        if self.recebe_resposta() == 'ok':
            self.logado = True
            self.nome_usuario = nome
            return True
        else:
            return False

    def lista_leiloes(self):
        self.envia_mensagem(MSG_LISTA_LEILOES)
        resposta = self.recebe_resposta()
        if len(resposta) > len('Listagem'):
            # http://stackoverflow.com/questions/1621906/is-there-a-way-to-split-a-string-by-every-nth-separator-in-python
            return resposta[10:]
        return ''

    def lanca_produto(self, nome, descricao, lance_minimo,
                      datahora_inicio, tempo_max_sem_lances):
        self.envia_mensagem(MSG_LANCA_PRODUTO, nome, descricao,
                            lance_minimo, datahora_inicio,
                            tempo_max_sem_lances)
        return self.recebe_resposta() == 'ok'

    def entrar_leilao(self, identificador_leilao):
        self.envia_mensagem(MSG_ENTRAR_LEILAO, identificador_leilao)
        return self.recebe_resposta() == 'ok'

    def enviar_lance(self, identificador_leilao, valor):
        self.envia_mensagem(MSG_ENVIAR_LANCE, identificador_leilao, valor)
        return self.recebe_resposta() == 'ok'

    def envia_mensagem(self, *campos):
        self.socket.sendall(','.join(map(str, campos)))

    def recebe_resposta(self, tamanho=32768):
        return self.socket.recv(tamanho)

    def sair(self):
        self.envia_mensagem('Sair')
        if self.recebe_resposta == 'ok':
            self.logado = False
            self.nome_usuario = None
            return True
        else:
            return False

    def fechar(self):
        self.socket.close()


def main():
    ip = "localhost"
    porta = 8888

    cliente = Cliente(ip, porta, 5)
    print 'Bem-vindo!'

    while True:
        if not cliente.logado:
            print 'Escolha uma das opções:'
            print '\t1- Adicionar usuário'
            print '\t2- Entrar'
            print '\t3- Listar leilões'
            print '\t4- Fechar'
            opcao = raw_input('\tDigite o número da sua opção: ')
            if opcao == '1':
                nome = raw_input('Entre com o nome: ')
                telefone = raw_input('Entre com o telefone: ')
                endereco = raw_input('Entre com o endereço: ')
                email = raw_input('Entre com o email: ')
                senha = raw_input('Entre com a senha: ')
                u = Usuario(nome, telefone, endereco, email, senha)
                ok = cliente.adiciona_usuario(u)
                if ok:
                    print 'Usuário criado com sucesso!'
                else:
                    print 'Falha na criação do usuário!'
            elif opcao == '2':
                nome = raw_input('Entre com o nome: ')
                senha = raw_input('Entre com a senha: ')
                ok = cliente.faz_login(nome, senha)
                if ok:
                    print 'Logado com sucesso.'
                else:
                    print 'Falha no login.'
            elif opcao == '3':
                listagem = cliente.lista_leiloes()
                if listagem == '':
                    print 'Não existem leilões abertos'
                else:
                    print listagem
            elif opcao == '4':
                print 'Até mais! Volte sempre!'
                cliente.fechar()
                return
            else:
                print 'Opção inválida. Digite o número de uma das opções acima'
        else:
            print 'Escolha uma das opções:'
            print '\t1- Listar leilões'
            print '\t2- Lançar um produto'
            print '\t3- Entrar em um leilão'
            print '\t4- Sair de um leilão'
            print '\t5- Enviar lance'
            print '\t6- Acompanhar leilões'
            print '\t7- Apagar usuário'
            print '\t8- Sair'
            opcao = raw_input('\tDigite o número da sua opção: ')
            if opcao == '1':
                print 'Ainda não implementado'
            elif opcao == '2':
                print 'Ainda não implementado'
            elif opcao == '3':
                print 'Ainda não implementado'
            elif opcao == '4':
                print 'Ainda não implementado'
            elif opcao == '5':
                print 'Ainda não implementado'
            elif opcao == '6':
                print 'Ainda não implementado'
            elif opcao == '7':
                print 'Ainda não implementado'
            elif opcao == '8':
                print 'Ainda não implementado'
            else:
                print 'Opção inválida. Digite o número de uma das opções acima'

if __name__ == "__main__":
    main()
