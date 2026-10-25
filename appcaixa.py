
import socketserver
import json
import threading

IP = "0.0.0.0"
PORTA = 5000

# Fila compartilhada dentro da aplicação da cozinha
fila = []
proximo_id = 1
bloqueio = threading.Lock()


class Atendimento(socketserver.StreamRequestHandler):

    def handle(self):
        global proximo_id

        try:
            # Recebe uma mensagem JSON enviada pelo garçom
            linha = self.rfile.readline().decode("utf-8")
            dados = json.loads(linha)

            # Impede alterações simultâneas na fila
            with bloqueio:

                if dados.get("acao") == "adicionar":
                    pedido = {
                        "id": proximo_id,
                        "cliente": dados["cliente"],
                        "itens": dados["itens"],
                        "status": "Pendente"
                    }

                    fila.append(pedido)
                    proximo_id += 1

                    resposta = {
                        "ok": True,
                        "id": pedido["id"]
                    }

                else:
                    resposta = {
                        "ok": False,
                        "erro": "Comando inválido."
                    }

            # Envia a confirmação ao garçom
            mensagem = json.dumps(resposta, ensure_ascii=False) + "\n"
            self.wfile.write(mensagem.encode("utf-8"))

        except (ValueError, KeyError, TypeError):
            resposta = {"ok": False, "erro": "Pedido inválido."}
            mensagem = json.dumps(resposta) + "\n"
            self.wfile.write(mensagem.encode("utf-8"))


# Cria o servidor TCP que recebe os pedidos
servidor = socketserver.ThreadingTCPServer(
    (IP, PORTA), Atendimento
)

# Permite encerrar o servidor sem aguardar conexões inativas
servidor.daemon_threads = True

# Executa o servidor em segundo plano
thread = threading.Thread(
    target=servidor.serve_forever,
    daemon=True
)
thread.start()

print(f"Cozinha conectada! Aguardando pedidos na porta {PORTA}.")


def mostrar_fila():
    # Acessa a fila com proteção contra alterações simultâneas
    with bloqueio:
        print("\n===== FILA DA COZINHA =====")

        if not fila:
            print("Nenhum pedido recebido.")
            return

        for pedido in fila:
            print(f"\nPedido #{pedido['id']}")
            print(f"Cliente: {pedido['cliente']}")
            print(f"Status: {pedido['status']}")

            for item in pedido["itens"]:
                subtotal = item["preco"] * item["quantidade"]
                print(
                    f"  {item['quantidade']}x {item['produto']} "
                    f"- R$ {subtotal:.2f}"
                )


while True:
    print("\n===== COZINHA =====")
    print("1 - Ver pedidos")
    print("2 - Marcar pedido como pronto")
    print("0 - Encerrar")

    opcao = input("Escolha: ")

    if opcao == "1":
        mostrar_fila()

    elif opcao == "2":
        try:
            numero = int(input("Número do pedido pronto: "))

            with bloqueio:
                pedido_encontrado = None

                for pedido in fila:
                    if pedido["id"] == numero:
                        pedido_encontrado = pedido
                        break

                if pedido_encontrado:
                    pedido_encontrado["status"] = "Pronto"
                    print(f"Pedido #{numero} marcado como pronto!")
                else:
                    print("Pedido não encontrado.")

        except ValueError:
            print("Digite um número válido.")

    elif opcao == "0":
        break

    else:
        print("Opção inválida!")

# Encerra o servidor ao sair
servidor.shutdown()
servidor.server_close()
print("Servidor da cozinha encerrado.")

