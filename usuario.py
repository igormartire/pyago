# -*- coding: utf-8 -*-


class Usuario:

    def __init__(self, nome, telefone, endereco, email, senha,
                 ids_leiloes_participando=set([])):
        if nome == '':
            raise ValueError
        self.nome = nome
        self.telefone = telefone
        self.endereco = endereco
        self.email = email
        self.senha = senha
        self.ids_leiloes_participando = ids_leiloes_participando

    def clone(self):
        return Usuario(self.nome, self.telefone, self.endereco,
                       self.email, self.senha, self.ids_leiloes_participando)

    # Este método define como é a representação em texto de um
    # objeto desta classe. Útil para imprimir o objeto na tela
    # ou num arquivo sem precisar definir todas as vezes como
    # converter o objeto para texto.
    def __str__(self):
        return "%s,%s,%s,%s,%s,%s" % \
          (self.nome, self.telefone, self.endereco, self.email, self.senha,
           ','.join(map(str, self.ids_leiloes_participando)))

    # Fonte: http://jcalderone.livejournal.com/32837.html
    def __eq__(self, other):
        if isinstance(other, Usuario):
            return self.nome == other.nome and \
                self.telefone == other.telefone and \
                self.endereco == other.endereco and \
                self.email == other.email and \
                self.senha == other.senha and \
                self.ids_leiloes_participando == other.ids_leiloes_participando
        return NotImplemented

    @staticmethod
    def texto_para_usuario(texto):
        campos = texto.rstrip().split(',')
        ids_leiloes_participando = set([])
        if campos[5] != '':
            ids_leiloes_participando = set(map(int, campos[5:]))
        return Usuario(nome=campos[0], telefone=campos[1],
                       endereco=campos[2], email=campos[3], senha=campos[4],
                       ids_leiloes_participando=ids_leiloes_participando)
