# -*- coding: utf-8 -*-

import socket
import time
import threading
import os
from usuario import Usuario
from leilao import Leilao, FORMATO_DATAHORA
from constantes import (MSG_FAZ_LOGIN,
                        MSG_LISTA_LEILOES,
                        MSG_ADICIONA_USUARIO,
                        MSG_LANCA_PRODUTO,
                        MSG_ENTRAR_LEILAO,
                        MSG_ENVIAR_LANCE,
                        MSG_SAIR,
                        MSG_INFORMACAO_LEILOES,
                        MSG_FIM_LEILAO,
                        MSG_CONTATO_VENDEDOR,
                        MSG_CONTATO_CLIENTE,
                        MSG_LANCE,
                        MSG_APAGA_USUARIO,
                        MSG_SAIR_LEILAO,
                        MSG_OK,
                        MSG_NOT_OK)


class Cliente:

    def __init__(self, ip="localhost", porta=8888, timeout=0):
        self.timeout = timeout
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, porta))
        self.logado = False
        self.nome_usuario = None
        if timeout > 0:
            self.socket.settimeout(timeout)
        self.acompanhando = False
        self.rodando = True

        def loop():
            while self.rodando:
                if self.acompanhando:
                    limpar_tela()
                    self.imprime_informacao_leiloes()
                    time.sleep(1)
        # Jusitificativa do uso de thread: sem esta thread seria muito mais
        # complexo permitir ao usuário parar o loop apertando a tecla ENTER.
        # Isto porque precisaríamos de uma captura de pressionamento de tecla
        # pelo usuário que seja assíncrona, isto é, que não bloqueie a execução
        # da thread principal. Poderíamos usar select.select() no stdin, mas
        # infelizmente isso não funcionaria no Windows. Assim sendo, soluções
        # assíncronas multi-plataformas são descritas em:
        # http://stackoverflow.com/questions/13207678/whats-the-simplest-way-of-detecting-keyboard-input-in-python-from-the-terminal
        # Contudo, por serem muito complexas, resolvemos optar por essa
        # abordagem mais simples que faz o uso de Threads, como sugerido em:
        # http://stackoverflow.com/questions/292095/polling-the-keyboard-detect-a-keypress-in-python
        # Assim, essa nova thread é responsável por imprimir na tela as
        # informações mais recentes de cada leilão a cada segundo, enquanto
        # a thread principal utiliza um simples comando raw_input aguardando
        # o pressionamento da tecla ENTER para então setar self.acompanhando
        # para False e assim fazer com que a Thread pare de imprimir na tela.
        threading.Thread(target=loop).start()

    def adiciona_usuario(self, usuario):
        # Envia a mensagem "Adiciona_usuario"
        self.envia_mensagem(MSG_ADICIONA_USUARIO,
                            usuario.nome, usuario.telefone,
                            usuario.endereco, usuario.email, usuario.senha)
        return self.recebe_resposta() == MSG_OK

    def apaga_usuario(self, senha):
        if not self.logado:
            return False
        # Envia a mensagem "Apaga_usuario"
        self.envia_mensagem(MSG_APAGA_USUARIO, self.nome_usuario, senha)
        return self.recebe_resposta() == MSG_OK

    def faz_login(self, nome, senha):
        # Envia a mensagem "Faz_login"
        self.envia_mensagem(MSG_FAZ_LOGIN, nome, senha)
        if self.recebe_resposta() == MSG_OK:
            self.logado = True
            self.nome_usuario = nome
            return True
        else:
            return False

    def lista_leiloes(self):
        # Envia a mensagem "Lista_leiloes"
        self.envia_mensagem(MSG_LISTA_LEILOES)
        resposta = self.recebe_resposta()
        # ';' separam leiloes. Os campos dos leiloes são separados por ','
        # A separação feita dessa forma facilita o processamento em comparação
        # com o caso onde ',' seriam usadas tanto para separar os campos de um
        # leilão como também para separar os leilões entre si.
        campos = resposta.split(';')
        listagem = []
        # A resposta sempre contém 1 campo: o cabeçalho Listagem. Se tiver
        # mais de 1, significa que veio informações de pelo menos 1 leilão.
        if len(campos) > 1:
            leiloes_texto = campos[1:]
            num_leiloes = len(leiloes_texto)
            for i in range(num_leiloes):
                leilao = Leilao.texto_para_leilao(leiloes_texto[i])
                listagem.append(leilao)
        return listagem

    def lanca_produto(self, nome, descricao, lance_minimo,
                      datahora_inicio, tempo_max_sem_lances):
        # Envia a mensagem "Lanca_produto"
        self.envia_mensagem(MSG_LANCA_PRODUTO, nome, descricao,
                            lance_minimo, datahora_inicio,
                            tempo_max_sem_lances)
        return self.recebe_resposta() == MSG_OK

    def entrar_leilao(self, identificador_leilao):
        # Envia a mensagem "Entrar_leilao"
        self.envia_mensagem(MSG_ENTRAR_LEILAO, identificador_leilao)
        return self.recebe_resposta() == MSG_OK

    def sair_leilao(self, identificador_leilao):
        # Envia a mensagem "Sair_leilao"
        self.envia_mensagem(MSG_SAIR_LEILAO, identificador_leilao)
        return self.recebe_resposta() == MSG_OK

    def enviar_lance(self, identificador_leilao, valor):
        # Envia a mensagem "Enviar_lance"
        self.envia_mensagem(MSG_ENVIAR_LANCE, identificador_leilao, valor)
        return self.recebe_resposta() == MSG_OK

    def imprime_informacao_leiloes(self):
        # Envia a mensagem "Informacao_leiloes"
        # Esta mensagem foi adicionada por nós para facilitar a implementação.
        # Seria muito complexo receber informações do servidor a cada 1 segundo
        # e imprimir imediatamente na tela sem que isso atrapalhasse o uso
        # da interface pelo usuário quando ele quisesse, por exemplo, fazer um
        # lance. No momento em que o usuário estivesse digitando as informações
        # para seu lance, o cliente receberia informações do servidor e as
        # imprimiria imediatamente, interferindo com a interface do usuário.
        # Assim, optamos por fazer com que o cliente peça as informações ao
        # servidor. Assim, ele pode fazer num momento em que esteja preparado
        # para tal. A resposta a essa mensagem são todas as informações mais
        # recentes sobre os leilões nos quais esse usuário participa. Essas
        # informações são impressas em tela, o que não atrapalha o usuário de
        # interagir com sua interface, pois esta está desabilitada até que o
        # usuário tecle ENTER, o que significa que o usuário deseja interagir
        # e portanto tais informações devem parar de serem impressas para que
        # o usuário possa utilizar a interface sem problemas.
        self.envia_mensagem(MSG_INFORMACAO_LEILOES)
        print '----------- Acompanhemento -----------\n'
        resposta = self.recebe_resposta()
        if resposta == MSG_NOT_OK:
            print 'Você não está participando de nenhum leilão.\n'
            self.acompanhando = False
        else:
            # Assim como na mensagem de Lista_leiloes, onde recebíamos uma
            # lista de leilões, aqui recebemos uma lista de mensagens e
            # novamente usamos o separador ';' para facilitar a separação das
            # diferentes mensangens. Novamente cada mensagem tem seus campos
            # separados por vírgulas.
            mensagens = resposta.split(';')
            for mensagem in mensagens:
                campos = mensagem.split(',')

                # Recebe a mensagem "Fim_leilao"
                if campos[0] == MSG_FIM_LEILAO:
                    if campos[3] == 'Aguardando o envio':
                        print (
                            'Fim do leilão: %s. Valor de venda: %s. '
                            'Comprador: N/A.' % (campos[1], campos[2])
                        )
                    else:
                        print (
                            'Fim do leilão: %s. Valor de venda: %s. '
                            'Comprador: %s.'
                            % (campos[1], campos[2], campos[3])
                        )
                # Recebe a mensagem "Contato_vendedor"
                elif campos[0] == MSG_CONTATO_VENDEDOR:
                    print (
                        'Leilão: %s. Valor de venda: %s.\n'
                        'Contato do vendedor:\n'
                        '\tNome: %s\n'
                        '\tEndereço: %s\n'
                        '\tTelefone: %s\n'
                        '\tEmail: %s'
                        % (campos[1], campos[2], campos[3],
                           campos[4], campos[5], campos[6])
                    )
                # Recebe a mensagem "Contato_cliente"
                elif campos[0] == MSG_CONTATO_CLIENTE:
                    print (
                        'Leilão: %s. Valor de venda: %s.\n'
                        'Contato do cliente:\n'
                        '\tNome: %s\n'
                        '\tEndereço: %s\n'
                        '\tTelefone: %s\n'
                        '\tEmail: %s'
                        % (campos[1], campos[2], campos[3],
                           campos[4], campos[5], campos[6])
                    )
                # Recebe a mensagem "Lance"
                # Adicionamos um novo campo na mensagem Lance que julgamos
                # interessante. Trata-se do tempo restante em segundos até
                # que o leilão seja finalizado caso não hajam mais lances.
                # Com essa informação o usuário sabe em tempo real o quanto
                # de tempo tem para decidir em dar uma lance ou não.
                elif campos[0] == MSG_LANCE:
                    print (
                        'Leilão: %s. Nome do autor do lance: %s. '
                        'Lance atual: %s. Número de usuários: %s '
                        'Número de lances: %s. Tempo restante: %s'
                        % (campos[1], campos[2], campos[3],
                           campos[4], campos[5], campos[6])
                    )
                print ''
        print '--------------------------------------'
        print '\nPressione [ENTER] para parar de acompanhar.\n'

    def envia_mensagem(self, *campos):
        self.socket.sendall(','.join(map(str, campos)))

    # O tamanho de 32768 é arbitrário e foi utilizado somente para garantir
    # que nenhuma parte de nenhuma mensagem será perdida. Julgamos que não
    # haverão mensagens tão grandes como as de tamanho 32768.
    def recebe_resposta(self, tamanho=32768):
        return self.socket.recv(tamanho)

    def sair(self):
        self.envia_mensagem(MSG_SAIR)
        if self.recebe_resposta() == MSG_OK:
            self.logado = False
            self.nome_usuario = None
            return True
        else:
            return False

    def fechar(self):
        self.socket.close()
        self.rodando = False


def main():
    # Aqui a interface do cliente pergunta ao usuário qual o IP e porta
    # do servidor.
    ip = raw_input('Entre com o IP do servidor: ')
    porta = int(raw_input('Entre com a porta do servidor: '))

    # Aqui usamos um timeout de 5 segundos só para garantir de que se houver
    # algum problema de conexão, o processo não fique parado para sempre
    # esperando uma resposta do servidor. Com esse timeout, o cliente espera
    # por uma resposta no máximo por 5 segundos.
    cliente = Cliente(ip, porta, timeout=5)
    print '\nSeja Bem-vindo!'

    try:
        while True:
            if not cliente.logado:
                print '\nEscolha uma das opções:'
                print '\t1- Adicionar usuário'
                print '\t2- Entrar'
                print '\t3- Listar leilões'
                print '\t4- Fechar'
                opcao = raw_input('\tDigite o número da sua opção: ')
                if opcao == '1':
                    nome = raw_input('\nEntre com o nome: ')
                    telefone = raw_input('Entre com o telefone: ')
                    endereco = raw_input('Entre com o endereço: ')
                    email = raw_input('Entre com o email: ')
                    senha = raw_input('Entre com a senha: ')
                    if nome == '':
                        print '\nO nome não pode ser vazio!'
                    else:
                        u = Usuario(nome, telefone, endereco, email, senha)
                        ok = cliente.adiciona_usuario(u)
                        if ok:
                            print '\nUsuário criado com sucesso!'
                        else:
                            print '\nFalha na criação do usuário!'
                elif opcao == '2':
                    nome = raw_input('\nEntre com o nome: ')
                    senha = raw_input('Entre com a senha: ')
                    ok = cliente.faz_login(nome, senha)
                    if ok:
                        print '\nLogado com sucesso.'
                    else:
                        print '\nFalha no login.'
                elif opcao == '3':
                    lista_leiloes(cliente)
                elif opcao == '4':
                    print '\nAté mais! Volte sempre!'
                    cliente.fechar()
                    return
                else:
                    print (
                        '\nOpção inválida. '
                        'Digite o número de uma das opções acima')
            else:
                print '\nEscolha uma das opções:'
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
                    lista_leiloes(cliente)
                elif opcao == '2':
                    nome = raw_input('\nEntre com o nome: ')
                    descricao = raw_input('Entre com a descrição: ')
                    lance_minimo = raw_input('Entre com o lance minimo: ')
                    datahora_inicio = raw_input(
                        'Entre com a data e hora de inicio '
                        '(formato: dd/mm/aaaa hh:mm:ss): ')
                    tempo_max_sem_lances = raw_input(
                        'Entre com o tempo máximo sem lances: ')
                    ok = cliente.lanca_produto(nome, descricao, lance_minimo,
                                               datahora_inicio,
                                               tempo_max_sem_lances)
                    if ok:
                        print '\nProduto lançado com sucesso'
                    else:
                        print '\nFalha no lançamento do produto'
                elif opcao == '3':
                    identificador_leilao = raw_input(
                        '\nEntre com o código identificador do leilão: ')
                    ok = cliente.entrar_leilao(identificador_leilao)
                    if ok:
                        print '\nEntrada efetuada com sucesso!'
                    else:
                        print '\nFalha na tentativa de entrar no leilão!'
                elif opcao == '4':
                    identificador_leilao = raw_input(
                        '\nEntre com o código identificador do leilão: ')
                    ok = cliente.sair_leilao(identificador_leilao)
                    if ok:
                        print '\nSaída efetuada com sucesso!'
                    else:
                        print '\nFalha na tentativa de sair do leilão!'
                elif opcao == '5':
                    identificador_leilao = raw_input(
                        '\nEntre com o código identificador do leilão: ')
                    valor = raw_input('Entre com o valor do lance: ')
                    ok = cliente.enviar_lance(identificador_leilao, valor)
                    if ok:
                        print '\nLance aceito com sucesso!'
                    else:
                        print '\nFalha no aceite do lance!'
                elif opcao == '6':
                    cliente.acompanhando = True
                    raw_input(
                        '\nPressione [ENTER] para parar de acompanhar.\n\n')
                    cliente.acompanhando = False
                elif opcao == '7':
                    senha = raw_input('\nEntre com sua senha: ')
                    ok = cliente.apaga_usuario(senha)
                    if ok:
                        print '\nUsuário deletado com sucesso!'
                        cliente.logado = False
                        cliente.nome_usuario = None
                    else:
                        print '\nFalha ao tentar deletar o usuário!'
                elif opcao == '8':
                    ok = cliente.sair()
                    if ok:
                        print '\nDeslogado com sucesso!'
                    else:
                        print '\nFalha ao tentar deslogar!'
                else:
                    print (
                        '\nOpção inválida. '
                        'Digite o número de uma das opções acima')
    finally:
        cliente.fechar()


def lista_leiloes(cliente):
    listagem = cliente.lista_leiloes()
    if listagem == []:
        print '\nNão existem leilões abertos'
    else:
        print '\n----------- Leilões: -----------\n'
        for leilao in listagem:
            print (
                'ID: %d '
                '| Nome: %s '
                '| Descrição: %s '
                '| Lance mínimo: R$ %.2f '
                '| Início: %s '
                '| Tempo máximo sem lances: %d '
                '| Dono: %s\n' %
                (leilao.identificador, leilao.nome,
                 leilao.descricao, leilao.lance_minimo,
                 leilao.datahora_inicio.strftime(
                    FORMATO_DATAHORA
                 ), leilao.tempo_max_sem_lances,
                 leilao.nome_dono)
            )
        print '--------------------------------\n'


# http://stackoverflow.com/a/23516888
# http://stackoverflow.com/questions/1325581/how-do-i-check-if-im-running-on-windows-in-python
def limpar_tela():
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix' or os.name == 'mac':
        os.system('clear')

if __name__ == "__main__":
    main()
