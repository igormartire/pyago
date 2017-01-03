# -*- coding: utf-8 -*-

from datetime import datetime

FORMATO_DATAHORA = '%d/%m/%Y %H:%M:%S'


class Leilao:

    def __init__(self, nome, descricao, lance_minimo,
                 datahora_inicio, tempo_max_sem_lances, nome_dono,
                 identificador=0, numero_de_lances=0, lance_atual=0,
                 nome_autor_do_lance="Aguardando o envio",
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
                      self.nome_dono, self.identificador,
                      self.numero_de_lances, self.lance_atual,
                      self.nome_autor_do_lance, self.datahora_ultimo_lance)

    def __str__(self):
        return "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % \
          (self.identificador, self.nome, self.descricao, self.lance_minimo,
           self.datahora_inicio.strftime(FORMATO_DATAHORA),
           self.tempo_max_sem_lances, self.nome_dono, self.numero_de_lances,
           self.lance_atual, self.nome_autor_do_lance,
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
                self.numero_de_lances == other.numero_de_lances and \
                self.lance_atual == other.lance_atual and \
                self.nome_autor_do_lance == other.nome_autor_do_lance and\
                self.datahora_ultimo_lance == other.datahora_ultimo_lance
        return NotImplemented

    def entrada_permitida(self):
        if self.finalizado():
            return False
        if datetime.now() >= self.datahora_inicio:
            return True
        if (self.datahora_inicio - datetime.now()).seconds <= 60 * 30:
            return True
        return False

    def lance(self, valor, nome_autor):
        if self.iniciado() and valor > self.lance_atual:
            self.lance_atual = valor
            self.nome_autor_do_lance = nome_autor
            self.numero_de_lances += 1
            self.datahora_ultimo_lance = datetime.now()
            return True
        else:
            return False

    def iniciado(self):
        return datetime.now() > self.datahora_inicio and not self.finalizado()

    def finalizado(self):
        agora = datetime.now()
        if agora > self.datahora_inicio:
            tempo_sem_lances = agora - self.datahora_ultimo_lance
            if tempo_sem_lances.seconds > self.tempo_max_sem_lances:
                return True
        return False

    @staticmethod
    def texto_para_leilao(texto):
        campos = texto.rstrip().split(',')
        return Leilao(
            identificador=int(campos[0]), nome=campos[1],
            descricao=campos[2], lance_minimo=float(campos[3]),
            datahora_inicio=campos[4], tempo_max_sem_lances=int(campos[5]),
            nome_dono=campos[6], numero_de_lances=int(campos[7]),
            lance_atual=float(campos[8]), nome_autor_do_lance=campos[9],
            datahora_ultimo_lance=campos[10]
        )
