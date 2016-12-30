# -*- coding: utf-8 -*-

from cliente import Cliente
from usuario import Usuario
from leilao import Leilao
import arquivo
import unittest
from servidor import Servidor
import threading

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

NUMERO_DE_THREADS = 10

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
        self.assertTrue(self.cliente.faz_login(Usuario.yago.nome,
                                               Usuario.yago.senha))

    def test_login_com_usuario_errado(self):
        self.cliente.adiciona_usuario(Usuario.yago)
        self.assertFalse(self.cliente.faz_login(Usuario.riguel.nome,
                                                Usuario.yago.senha))

    def test_login_com_senha_errada(self):
        self.cliente.adiciona_usuario(Usuario.yago)
        self.assertFalse(self.cliente.faz_login(Usuario.yago.nome,
                                                Usuario.riguel.senha))

    def test_lanca_produto_com_usuario_deslogado(self):
        self.assertFalse(self.cliente.lanca_produto(
            'Laptop', 'Macbook Pro Late 2016',
            8000, '25/01/2017 15:45:00', 300
        ))

    def test_lanca_produto_com_usuario_logado(self):
        self.cliente.adiciona_usuario(Usuario.yago)
        self.cliente.faz_login(Usuario.yago.nome, Usuario.yago.senha)
        self.assertTrue(self.cliente.lanca_produto(
            'Laptop', 'Macbook Pro Late 2016', 8000,
            '25/01/2017 15:45:00', 300
        ))
        self.assertEquals(
            self.arquivo.get_leilao_por_identificador(1),
            Leilao(
                'Laptop', 'Macbook Pro Late 2016', 8000,
                '25/01/2017 15:45:00', 300, Usuario.yago.nome, 1
            )
        )

    def test_lanca_produto_sem_nome(self):
        self.cliente.adiciona_usuario(Usuario.yago)
        self.cliente.faz_login(Usuario.yago.nome, Usuario.yago.senha)
        self.assertFalse(self.cliente.lanca_produto(
            '', 'Macbook Pro Late 2016', 8000,
            '25/01/2017 15:45:00', 300
        ))

    def test_lanca_produto_duas_vezes(self):
        self.cliente.adiciona_usuario(Usuario.yago)
        self.cliente.faz_login(Usuario.yago.nome, Usuario.yago.senha)
        self.assertTrue(self.cliente.lanca_produto(
            'Laptop', 'Macbook Pro Late 2016', 8000,
            '25/01/2017 15:45:00', 300
        ))
        self.assertTrue(self.cliente.lanca_produto(
            'Laptop', 'Macbook Pro Late 2016', 8000,
            '25/01/2017 15:45:00', 300
        ))
        self.assertEquals(
            self.arquivo.get_leilao_por_identificador(1),
            Leilao(
                'Laptop', 'Macbook Pro Late 2016', 8000,
                '25/01/2017 15:45:00', 300, Usuario.yago.nome, 1
            )
        )
        self.assertEquals(
            self.arquivo.get_leilao_por_identificador(2),
            Leilao(
                'Laptop', 'Macbook Pro Late 2016', 8000,
                '25/01/2017 15:45:00', 300, Usuario.yago.nome, 2
            )
        )

    def test_lanca_produtos_em_paralelo(self):
        def loga_e_lanca_produto():
            cliente = Cliente(timeout=3)
            cliente.faz_login(Usuario.yago.nome, Usuario.yago.senha)
            self.assertTrue(
                cliente.lanca_produto(
                    'Laptop', 'Macbook Pro Late 2016', 8000,
                    '25/01/2017 15:45:00', 300
                )
            )
        self.cliente.adiciona_usuario(Usuario.yago)
        threads = []
        for i in range(1, NUMERO_DE_THREADS+1):
            t = threading.Thread(target=loga_e_lanca_produto)
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        for i in range(1, NUMERO_DE_THREADS+1):
            self.assertEquals(
                self.arquivo.get_leilao_por_identificador(i),
                Leilao(
                    'Laptop', 'Macbook Pro Late 2016', 8000,
                    '25/01/2017 15:45:00', 300, Usuario.yago.nome, i
                )
            )

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
