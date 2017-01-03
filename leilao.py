# -*- coding: utf-8 -*-

from datetime import datetime

FORMATO_DATAHORA = '%d/%m/%Y %H:%M:%S'


class Leilao:

    def __init__(self, nome, descricao, lance_minimo,
                 datahora_inicio, tempo_max_sem_lances, nome_dono,
                 identificador=0, numero_usuarios=0, numero_de_lances=0,
                 lance_atual=0, nome_autor_do_lance="Aguardando o envio",
                 datahora_ultimo_lance=''):
        if nome == '':
            raise ValueError
        self.identificador = identificador
        self.nome = nome
        self.descricao = descricao
        self.lance_minimo = lance_minimo
        self.datahora_inicio = datetime.strptime(datahora_inicio,
                                                 FORMATO_DATAHORA)
        self.tempo_max_sem_lances = tempo_max_sem_lances
        self.nome_dono = nome_dono
        self.numero_usuarios = numero_usuarios
        self.numero_de_lances = numero_de_lances
        self.lance_atual = lance_atual if lance_atual else lance_minimo
        self.nome_autor_do_lance = nome_autor_do_lance
        if datahora_ultimo_lance == '':
            datahora_ultimo_lance = datahora_inicio
        self.datahora_ultimo_lance = datetime.strptime(datahora_ultimo_lance,
                                                       FORMATO_DATAHORA)

    def set_identificador(self, identificador):
        self.identificador = identificador

    def clone(self):
        return Leilao(self.nome, self.descricao, self.lance_minimo,
                      self.datahora_inicio, self.tempo_max_sem_lances,
                      self.nome_dono, self.identificador, self.numero_usuarios,
                      self.numero_de_lances, self.lance_atual,
                      self.nome_autor_do_lance, self.datahora_ultimo_lance)

    def __str__(self):
        return "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % \
          (self.identificador, self.nome, self.descricao, self.lance_minimo,
           self.datahora_inicio.strftime(FORMATO_DATAHORA),
           self.tempo_max_sem_lances, self.nome_dono, self.numero_usuarios,
           self.numero_de_lances, self.lance_atual, self.nome_autor_do_lance,
           self.datahora_ultimo_lance.strftime(FORMATO_DATAHORA))

    def __eq__(self, other):
        if isinstance(other, Leilao):
            return self.identificador == other.identificador and \
                self.nome == other.nome and \
                self.descricao == other.descricao and \
                self.lance_minimo == other.lance_minimo and \
                self.datahora_inicio == other.datahora_inicio and \
                self.tempo_max_sem_lances == other.tempo_max_sem_lances and \
                self.nome_dono == other.nome_dono and \
                self.numero_usuarios == other.numero_usuarios and \
                self.numero_de_lances == other.numero_de_lances and \
                self.lance_atual == other.lance_atual and \
                self.nome_autor_do_lance == other.nome_autor_do_lance and\
                self.datahora_ultimo_lance == other.datahora_ultimo_lance
        return NotImplemented

    def entrada_permitida(self):
        # A entrada não é permitida se o leilão já estiver finalizado.
        if self.finalizado():
            return False
        # A entrada é permitida se o leilão já estiver iniciado
        if datetime.now() >= self.datahora_inicio:
            return True
        # A entrada é permitida até 30 minutos antes do início do leilão
        if (self.datahora_inicio - datetime.now()).seconds <= 60 * 30:
            return True
        return False

    def lance(self, valor, nome_autor):
        # O valor é válido se o leilão estiver acontecendo e o lance for maior
        # do que o lance atual. Este é um ponto crítico (onde duas threads não
        # devem pode acessar ao mesmo tempo) pois decisões são tomadas com
        # base em valores de variáveis compartilhadas (no caso, o valor do
        # lance_atual do leilão). Por isso, quem chama esta função é, na
        # verdade, o módulo arquivo, em seu método lance_leilao(), que adquire
        # o lock sobre o arquivo de leiloes e, portanto, evita interferência
        # de outras threads que possam estar querendo acessar/modificar o
        # mesmo valor utilizado aqui.
        if self.iniciado() and valor > self.lance_atual:
            self.lance_atual = valor
            self.nome_autor_do_lance = nome_autor
            self.numero_de_lances += 1
            self.datahora_ultimo_lance = datetime.now()
            return True
        else:
            return False

    def iniciado(self):
        # Retorna True se o leilão estiver acontencendo
        return datetime.now() > self.datahora_inicio and not self.finalizado()

    def finalizado(self):
        # Retorna True se o leilão já tiver acabado, isto é, não recebeu nenhum
        # lance durante um período equivalente ao seu "tempo máximo sem lances"
        agora = datetime.now()
        if agora > self.datahora_inicio:
            tempo_sem_lances = agora - self.datahora_ultimo_lance
            if tempo_sem_lances.seconds > self.tempo_max_sem_lances:
                return True
        return False

    def tempo_restante(self):
        # Calcula quantos segundos ainda resta antes que o leilão seja
        # finalizado caso não seja feito nenhum lance.
        agora = datetime.now()
        if agora < self.datahora_inicio:
            return "não iniciado"
        tempo_sem_lances = agora - self.datahora_ultimo_lance
        return max(self.tempo_max_sem_lances - tempo_sem_lances.seconds, 0)

    @staticmethod
    def texto_para_leilao(texto):
        campos = texto.rstrip().split(',')
        return Leilao(
            identificador=int(campos[0]), nome=campos[1],
            descricao=campos[2], lance_minimo=float(campos[3]),
            datahora_inicio=campos[4], tempo_max_sem_lances=int(campos[5]),
            nome_dono=campos[6], numero_usuarios=int(campos[7]),
            numero_de_lances=int(campos[8]), lance_atual=float(campos[9]),
            nome_autor_do_lance=campos[10], datahora_ultimo_lance=campos[11]
        )
