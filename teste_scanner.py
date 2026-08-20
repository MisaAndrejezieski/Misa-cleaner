from scanner import Scanner


def progresso(caminho):
    print(f"Escaneando: {caminho}")

def resultado(item):
    tamanho = item.get('tamanho_mb', item.get('tamanho_total_mb', 0))
    print(f"Encontrado: {item['caminho']} - {tamanho:.1f} MB")


def testar_scanner():
    scanner = Scanner()
    print("Iniciando varredura de teste...")
    resultados = scanner.escanear_tudo(progresso, resultado)
    total = sum(len(itens) for itens in resultados.values())
    print(f"\nVarredura concluída! {total} itens encontrados.")


if __name__ == "__main__":
    testar_scanner()