from scanner import Scanner


def progresso(caminho):
    print(f"Escaneando: {caminho}")

def resultado(item):
    print(f"📂 Encontrado: {item['caminho']} - {item['tamanho_mb']:.1f} MB")

scanner = Scanner()
print("🚀 Iniciando varredura de teste...")
resultados = scanner.escanear_tudo(progresso, resultado)

print(f"\n✅ Varredura concluída! {len(resultados)} pastas obsoletas encontradas.")