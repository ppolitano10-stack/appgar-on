
import socket
import json

IP_COZINHA = input("IP do computador da cozinha: ")
PORTA = 5000

cardapio = {
    1: ("Hambúrguer", 25.00),
    2: ("Pizza", 35.00),
    3: ("Hot Dog", 15.00),
    4: ("Batata Frita", 12.00),
    5: ("Refrigerante", 7.00)
}


def enviar_pedido(dados):
    # Conecta à aplicação da cozinha
    with socket.create_connection((IP_COZINHA, PORTA)) as conexao:
        # Envia os dados do pedido em formato JSON
        mensagem = json.dumps(dados, ensure_ascii=False) + "\n"
        conexao.sendall(mensagem.encode("utf-8"))

        # Recebe a confirmação da cozinha
        arquivo = conexao.makefile("r", encoding="utf-8")
        return json.loads(arquivo.readline())


while True:
    print("\n===== SISTEMA DO GARÇOM =====")
    print("1 - Novo pedido")
    print("0 - Sair")

    opcao = input("Escolha: ")

    if opcao == "1":
        cliente = input("Nome do cliente: ")
        itens = []

        while True:
            print("\n--- CARDÁPIO ---")

            for codigo, (nome, preco) in cardapio.items():
                print(f"{codigo} - {nome}: R$ {preco:.2f}")

            print("0 - Finalizar pedido")

            escolha = input("Escolha um produto: ")

            if escolha == "0":
                break

            if not escolha.isdigit() or int(escolha) not in cardapio:
                print("Produto inválido!")
                continue

            codigo = int(escolha)
            nome, preco = cardapio[codigo]

            try:
                quantidade = int(input("Quantidade: "))
                if quantidade <= 0:
                    print("Quantidade deve ser maior que zero.")
                    continue
            except ValueError:
                print("Digite uma quantidade válida.")
                continue

            itens.append({
                "produto": nome,
                "quantidade": quantidade,
                "preco": preco
            })

            print("Produto adicionado!")

        if itens:
            try:
                resposta = enviar_pedido({
                    "acao": "adicionar",
                    "cliente": cliente,
                    "itens": itens
                })

                if resposta.get("ok"):
                    print("Pedido enviado para a cozinha!")
                    print("Número do pedido:", resposta["id"])
                else:
                    print("Erro:", resposta.get("erro"))

            except (OSError, ValueError):
                print("Não foi possível conectar à cozinha.")

        else:
            print("Pedido vazio. Nada foi enviado.")

    elif opcao == "0":
        print("Encerrando o sistema do garçom.")
        break

    else:
        print("Opção inválida!")