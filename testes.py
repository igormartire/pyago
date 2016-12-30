# -*- coding: utf-8 -*-

from cliente import Cliente
from modelos import Usuario
import arquivo
import unittest
from servidor import Servidor

"""
    Arquivo de testes de integração entre cliente e servidor.
    Tutorial para usar unittest:
        https://cgoldberg.github.io/python-unittest-tutorial/
        https://docs.python.org/2/library/unittest.html
"""

Usuario.yago = Usuario("Yago", "1111-1111", "Rua Y",
                       "yago@yago.com", "abc123")
Usuario.riguel = Usuario("Ríguel", "222-222", "Rua R",
                         "riguel@riguel.com", "123abc")


class Teste(unittest.TestCase):

    def setUp(self):
        self.cliente = Cliente(timeout=3)
        self.arquivo = arquivo.Gerenciador()
        self.arquivo.apagar_todos()

    def tearDown(self):
        self.cliente.fechar()

    def test_adiciona_usuario(self):
        self.assertTrue(self.cliente.adiciona_usuario(Usuario.yago))
        self.assertTrue(self.existe_usuario(Usuario.yago))

    def test_adiciona_usuario_repetido(self):
        self.assertTrue(self.cliente.adiciona_usuario(Usuario.yago))
        usuario_repetido = Usuario.riguel.clone()
        usuario_repetido.nome = Usuario.yago.nome
        self.assertFalse(self.cliente.adiciona_usuario(usuario_repetido))
        self.assertFalse(self.existe_usuario(usuario_repetido))

    def test_adiciona_usuario_invalido(self):
        usuario_invalido = Usuario.yago.clone()
        usuario_invalido.nome = ''
        self.assertFalse(self.cliente.adiciona_usuario(usuario_invalido))
        self.assertFalse(self.existe_usuario(usuario_invalido))

    def test_login_com_usuario_e_senha_corretos(self):
        self.cliente.adiciona_usuario(Usuario.yago)
        self.assertTrue(self.cliente.login(Usuario.yago.nome,
                                           Usuario.yago.senha))

    def test_login_com_usuario_errado(self):
        self.cliente.adiciona_usuario(Usuario.yago)
        self.assertFalse(self.cliente.login(Usuario.riguel.nome,
                                            Usuario.yago.senha))

    def test_login_com_senha_errada(self):
        self.cliente.adiciona_usuario(Usuario.yago)
        self.assertFalse(self.cliente.login(Usuario.yago.nome,
                                            Usuario.riguel.senha))

    def test_lista_leiloes_sem_leiloes(self):
        self.assertEqual(self.cliente.lista_leiloes(), "Listagem")

    def test_lista_leiloes_somente_com_leiloes_fechados(self):
        pass

    def test_lista_leiloes_com_leiloes_fechados_abertos_e_futuros(self):
        pass

    def test_multiple_bids(self):
        pass
        # for client_id in range(NUM_OF_CLIENTS):
        #     t = threading.Thread(target=client.client, args=(client_id,))
        #     t.start()

    def existe_usuario(self, usuario):
        u = self.arquivo.get_usuario_por_nome(usuario.nome)
        return usuario == u


if __name__ == "__main__":
    servidor = Servidor('localhost', 8888, False)
    try:
        unittest.main()
    finally:
        servidor.parar()
