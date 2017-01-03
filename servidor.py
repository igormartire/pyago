# -*- coding: utf-8 -*-

import socket
import threading
from usuario import Usuario
import arquivo
from constantes import (MSG_FAZ_LOGIN,
                        MSG_LISTA_LEILOES,
                        MSG_ADICIONA_USUARIO,
                        MSG_LISTAGEM,
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


class Servidor:

    def __init__(self, host='localhost', porta=8888, verbose=False):
        # Verbose=True fará com que o servidor imprima na tela mensagens
        # que explicam o que está acontecendo agora, como status do servidor,
        # mensagens recebidas dos clientes, erros.
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
        # Jusitificativa do uso de thread: de forma similar à thread usada
        # na classe Cliente, esta thread foi aqui utilizada para permitir
        # a captura da tecla ENTER pelo usuário para finalizar o servidor.
        # Ao capturar a intenção de finalizar o servidor, podemos finalizar
        # todas as conexões e threads corretamente, ao invés de causar
        # mal uso da memória e precisar matar o processo através de linha
        # de comando, pois o processo estaria com várias threads em execução
        # que estariam impedindo o processo de ser concluído. Assim, colocamos
        # a tarefa de escutar "infinitamente" por novas conexões nessa nova
        # thread. "infinitamente" entre aspas porque se analisarmos o código
        # do método escuta(), podemos perceber que o while é condicionado no
        # valor de self.rodando, que só será False quanto o processo estiver
        # sendo finalizado devido a uma ação do usuário (pressionamento da
        # tecla ENTER por exemplo).
        self.thread_escuta = threading.Thread(target=self.escuta)
        self.thread_escuta.start()
        self.log('Esperando por novas conexões na porta %s ...' % porta)

    def escuta(self):
        while self.rodando:
            conexao, endereco = self.socket_escuta.accept()
            if self.rodando:
                # Note que é sempre o mesmo self.arquivo que é passado
                # para todas as conexões. Isso faz com que todas as conexões
                # compartilhem os mesmos semáforos do self.arquivo, evitando
                # assim que umas interfiram nas outras.
                Conexao(conexao, endereco, self.arquivo, self.verbose)

    def parar(self):
        self.log("Encerrando...")
        self.rodando = False
        # Esse cliente_falso é necessário, pois a thread de escuta de novas
        # conexões está bloqueada no método accept(), que só será desbloqueada
        # depois que uma conexão for aceita. Assim, criamos essa simples
        # conexão somente para desbloquear a thread de escuta, para que ela
        # possar então prosseguir com o seu encerramento, uma vez que
        # self.rodando agora é False.
        cliente_falso = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_falso.connect((self.host, self.porta))
        cliente_falso.close()
        # Esperamos a thread de escuta chegar ao seu fim
        self.thread_escuta.join()
        # Para então fecharmos seu socket
        self.socket_escuta.close()
        self.log("Encerrado.")

    def log(self, msg):
        if self.verbose:
            print "Servidor: %s" % msg


class Conexao:

    count = 0

    def __init__(self, conexao, endereco, arquivo, verbose=False):
        Conexao.count += 1
        # Este ID é utilizado apena para fins de log, para diferenciar um
        # cliente do outro de forma mais simples do que a combinação de
        # IP e porta.
        self.id = Conexao.count
        self.conexao = conexao
        self.endereco = endereco
        self.arquivo = arquivo
        self.verbose = verbose
        self.logado = False
        self.nome_usuario = None
        self.log("Iniciando conexão com %s" % str(endereco))
        # Jusitificativa do uso de thread: antes de criarmos essa nova thread
        # este código está sendo executado na mesma thread que é responsável
        # por escutar por novas conexões. Para que a thread possa então voltar
        # à sua incansável tarefa de aceitar novas conexões, precisamos
        # liberá-la do restante desta tarefa de lidar com o cliente. Assim,
        # passamos esta tarefa para uma nova thread. Dessa forma, temos uma
        # thread dedicada para cada cliente e uma única thread responsável
        # por escutar e aceitar novas conexões.
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

                # Aqui nós direcionamos cada mensagem para o método de
                # tratamento adequado.
                try:
                    if campos[0] == MSG_ADICIONA_USUARIO:
                        self.adiciona_usuario(*campos[1:])
                    elif campos[0] == MSG_APAGA_USUARIO:
                        self.apaga_usuario(*campos[1:])
                    elif campos[0] == MSG_FAZ_LOGIN:
                        self.faz_login(*campos[1:])
                    elif campos[0] == MSG_LISTA_LEILOES:
                        self.lista_leiloes()
                    elif campos[0] == MSG_LANCA_PRODUTO:
                        self.lanca_produto(*campos[1:])
                    elif campos[0] == MSG_ENTRAR_LEILAO:
                        self.entrar_leilao(*campos[1:])
                    elif campos[0] == MSG_SAIR_LEILAO:
                        self.sair_leilao(*campos[1:])
                    elif campos[0] == MSG_ENVIAR_LANCE:
                        self.enviar_lance(*campos[1:])
                    elif campos[0] == MSG_INFORMACAO_LEILOES:
                        self.informacao_leiloes()
                    elif campos[0] == MSG_SAIR:
                        self.sair()
                except Exception as e:
                    self.log('Error: ' + str(e))

                mensagem = self.conexao.recv(4096)
        finally:
            self.parar()

    def adiciona_usuario(self, nome, telefone, endereco, email, senha):
        try:
            u = self.arquivo.get_usuario_por_nome(nome)
            if u is not None:
                # Se achou um usuário com o mesmo nome, responde com 'not_ok'
                self.responde_erro()
            else:
                new_u = Usuario(nome, telefone, endereco, email, senha)
                self.arquivo.salva_usuario(new_u)
                self.responde_sucesso()
        except ValueError:
            # O construtor de Usuario retorna ValueError caso o nome
            # do usuário seja vazio. Nesse caso responde com 'not_ok',
            # pois não se pode criar um usuário inválido (nome vazio).
            self.responde_erro()

    def apaga_usuario(self, nome, senha):
        # Se não estiver logado, responde com 'not_ok', pois precisa estar
        # logado para realizar esta ação.
        if not self.logado:
            self.responde_erro()
            return

        # Somente permite deletar o próprio usuário
        if nome != self.nome_usuario:
            self.responde_erro()
            return

        ok = self.arquivo.apaga_usuario(nome, senha)
        if ok:
            # Após deletar seu usuário, o cliente é automaticamente deslogado
            self.sair()
        else:
            self.responde_erro()

    def faz_login(self, nome, senha):
        if self.logado:
            self.responde_erro()
            return

        u = self.arquivo.get_usuario_por_nome(nome)
        if u is not None and u.senha == senha:
            self.logado = True
            self.nome_usuario = u.nome
            self.responde_sucesso()
        else:
            self.responde_erro()

    def lista_leiloes(self):
        leiloes = self.arquivo.get_listagem_leiloes()
        leiloes_nao_finalizados = filter(lambda l: not l.finalizado(), leiloes)
        if leiloes_nao_finalizados:
            listagem = ';'.join(map(str, leiloes_nao_finalizados))
            self.conexao.sendall(MSG_LISTAGEM + ';' + listagem)
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
                tempo_max_sem_lances, self.nome_usuario
            )
            self.responde_sucesso()
        except ValueError as e:
            self.log('Error: ' + str(e))
            self.responde_erro()

    def entrar_leilao(self, identificador_leilao):
        if not self.logado:
            self.responde_erro()
            return

        id_leilao = int(identificador_leilao)
        ok = self.arquivo.entrar_leilao(self.nome_usuario, id_leilao)
        if ok:
            self.responde_sucesso()
        else:
            self.responde_erro()

    def sair_leilao(self, identificador_leilao):
        if not self.logado:
            self.responde_erro()
            return

        id_leilao = int(identificador_leilao)
        ok = self.arquivo.sair_leilao(self.nome_usuario, id_leilao)
        if ok:
            self.responde_sucesso()
        else:
            self.responde_erro()

    def enviar_lance(self, identificador_leilao, valor):
        if not self.logado:
            self.responde_erro()
            return

        id_leilao = int(identificador_leilao)
        ids_leiloes_usuario = self.arquivo\
            .get_ids_leiloes_dos_quais_o_usuario_participa(self.nome_usuario)
        # Se o usuário está tentando dar um lance num leilão do qual ele não
        # participa, responde com 'not_ok'
        if id_leilao not in ids_leiloes_usuario:
            self.responde_erro()
        else:
            ok = self.arquivo.lance_leilao(
                id_leilao, float(valor), self.nome_usuario
            )
            if ok:
                self.responde_sucesso()
            else:
                self.responde_erro()

    # Retorna a informação mais recente para cada um dos leilões dos quais
    # o usuário participa. A informação pode ser de Lance ou de Fim_leilao. Se
    # for de Fim_leilao, ainda pode contar as informações Contato_cliente ou
    # Contato_vendedor.
    def informacao_leiloes(self):
        if not self.logado:
            self.responde_erro()
            return

        leiloes = self.arquivo.get_listagem_leiloes()
        ids_leiloes_usuario = self.arquivo\
            .get_ids_leiloes_dos_quais_o_usuario_participa(self.nome_usuario)
        leiloes_usuario = filter(
            lambda l: l.identificador in ids_leiloes_usuario, leiloes)

        if len(leiloes_usuario) == 0:
            self.responde_erro()

        mensagens = []
        for leilao in leiloes_usuario:
            if leilao.finalizado():
                mensagens.append(','.join([
                    MSG_FIM_LEILAO, str(leilao.identificador),
                    str(leilao.lance_atual), leilao.nome_autor_do_lance
                ]))
                if self.nome_usuario == leilao.nome_dono:
                    comprador = self.arquivo.get_usuario_por_nome(
                        leilao.nome_autor_do_lance)
                    if comprador is not None:
                        mensagens.append(','.join([
                            MSG_CONTATO_CLIENTE, str(leilao.identificador),
                            str(leilao.lance_atual), comprador.nome,
                            comprador.endereco, comprador.telefone,
                            comprador.email
                        ]))
                    else:
                        mensagens.append(','.join([
                            MSG_CONTATO_CLIENTE, str(leilao.identificador),
                            str(leilao.lance_atual), 'Usuário apagado',
                            'Usuário apagado', 'Usuário apagado',
                            'Usuário apagado'
                        ]))
                if self.nome_usuario == leilao.nome_autor_do_lance:
                    vendedor = self.arquivo.get_usuario_por_nome(
                        leilao.nome_dono)
                    if vendedor is not None:
                        mensagens.append(','.join([
                            MSG_CONTATO_VENDEDOR, str(leilao.identificador),
                            str(leilao.lance_atual), vendedor.nome,
                            vendedor.endereco, vendedor.telefone,
                            vendedor.email
                        ]))
                    else:
                        mensagens.append(','.join([
                            MSG_CONTATO_VENDEDOR, str(leilao.identificador),
                            str(leilao.lance_atual), 'Usuário apagado',
                            'Usuário apagado', 'Usuário apagado',
                            'Usuário apagado'
                        ]))
            else:
                mensagens.append(','.join([
                    MSG_LANCE, str(leilao.identificador),
                    leilao.nome_autor_do_lance, str(leilao.lance_atual),
                    str(leilao.numero_usuarios), str(leilao.numero_de_lances),
                    str(leilao.tempo_restante())
                ]))
        self.conexao.sendall(';'.join(mensagens))

    def sair(self):
        if self.logado:
            self.logado = False
            self.nome_usuario = None
            self.responde_sucesso()
        else:
            self.responde_erro()

    def responde_erro(self):
        # Envia a mensagem 'not_ok' pro cliente, indicando operação não
        # realizada com sucesso
        self.conexao.sendall(MSG_NOT_OK)

    def responde_sucesso(self):
        # Envia a mensagem 'ok' pro cliente, indicando operação realizada
        # com sucesso
        self.conexao.sendall(MSG_OK)

    def log(self, msg):
        if self.verbose:
            print 'Cliente %d: %s' % (self.id, msg)


if __name__ == '__main__':
    ip = raw_input('Entre com o IP do servidor: ')
    porta = int(raw_input('Entre com a porta do servidor: '))
    servidor = Servidor(ip, porta, verbose=True)
    try:
        raw_input('Pressione [ENTER] para encerrar o servidor.\n')
    except KeyboardInterrupt:
        pass
    servidor.parar()
