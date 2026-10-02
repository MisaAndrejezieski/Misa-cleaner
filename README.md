# MISA-CLEANER

> Scanner de resquícios digitais para Windows. Encontra resquícios de programas deletados, arquivos obsoletos e duplicados. **Não deleta nada** — você decide o que fazer.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Estável-brightgreen)

---

## Sumário

- [O que é](#o-que-é)
- [O que NÃO faz](#o-que-não-faz)
- [Como funciona](#como-funciona)
- [Instalação](#instalação)
- [Uso](#uso)
- [Diagnóstico](#diagnóstico)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Desenvolvimento](#desenvolvimento)
- [Gerar executável (.exe)](#gerar-executável-exe)
- [Segurança](#segurança)
- [Licença](#licença)
- [Autor](#autor)

---

## O que é

O **MISA-CLEANER** é uma ferramenta de **diagnóstico** que varre pastas de usuário do Windows (`AppData`, `LocalAppData`, `Program Files`) em busca de três categorias de itens:

| Camada | O que procura | Critério |
|--------|---------------|----------|
| **1. Resquícios** | Pastas de programas que já foram desinstalados | Nome bate com programa conhecido + programa não está instalado |
| **2. Obsoletos** | Arquivos e pastas sem acesso há mais de 1 ano | `st_atime` > 365 dias |
| **3. Duplicados** | Arquivos idênticos (mesmo hash MD5) | Tamanho > 1 MB |

A interface é inspirada no filme *Matrix*: durante a varredura, um efeito de "chuva de código" toma conta da tela. Ao terminar, os resultados aparecem em uma tabela estilizada.

---

## O que NÃO faz

Isso é importante:

- ❌ **Não deleta nada.** A ferramenta apenas encontra e lista. Você decide o que fazer com cada item.
- ❌ **Não modifica o registro do Windows.**
- ❌ **Não envia dados para nenhum servidor.** Tudo roda localmente.
- ❌ **Não funciona em Linux/macOS.** É específica para caminhos do Windows.
- ❌ **Não força exclusão de arquivos protegidos.** Se não puder ler, ignora.

---

## Como funciona

### Camada 1 — Resquícios de programas deletados

Para cada pasta em `AppData`, `LocalAppData` e `Program Files`, o scanner compara o nome com uma lista de ~70 programas conhecidos (Adobe, Steam, Discord, VSCode, Chrome, etc.). Se o nome bate **mas o programa não está instalado** (verificado via registro do Windows), a pasta é marcada como resquício.

### Camada 2 — Arquivos obsoletos

Percorre recursivamente as pastas de usuário em busca de arquivos e pastas cujo último acesso (`st_atime`) foi há mais de **365 dias**. Pastas com menos de 1 MB são ignoradas.

### Camada 3 — Duplicados

Calcula o hash MD5 de arquivos maiores que 1 MB em `AppData` e `LocalAppData`. Se dois ou mais arquivos têm o mesmo hash, são marcados como duplicados.

### Proteção de sistema

Uma lista negra abrangente impede a varredura de:

- `C:\Windows`, `C:\Windows\System32`, `WinSxS`, `Installer`
- `C:\Program Files\Common Files`, `WindowsApps`, `dotnet`, `Microsoft SQL Server`
- `C:\ProgramData`, `C:\Users\Public`, `C:\$Recycle.Bin`
- `AppData\Local\Comms`, `AppData\Local\Packages`, caches de navegadores
- Pastas de desenvolvimento (`node_modules`, `.git`, `.venv`, `__pycache__`)
- Arquivos em uso por outros processos (detectados via tentativa de leitura)

---

## Instalação

### Requisitos

- **Windows 10 ou superior**
- **Python 3.9+** ([download](https://www.python.org/downloads/))
- **Tkinter** (já vem com o Python no Windows)

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/MisaAndrejezieski/Misa-cleaner.git
cd Misa-cleaner

# 2. Crie um ambiente virtual (recomendado)
python -m venv .venv
.venv\Scripts\activate

# 3. Instale as dependências (nenhuma externa obrigatória)
pip install -r requirements.txt

# 4. Execute
python main.py
```

**Observação:** o `requirements.txt` está vazio de propósito. O projeto usa apenas a biblioteca padrão do Python.

---

## Uso

1. Clique em **INICIAR VARREDURA**.
2. A interface é substituída pelo efeito *Matrix Rain* enquanto a varredura roda em background (thread separada, sem travar a UI).
3. Ao terminar, a tabela mostra os itens encontrados, classificados por tipo (Resquício, Obsoleto, Duplicado).
4. Selecione um item na tabela e:
   - Clique em **ABRIR NO EXPLORER** — abre a pasta do item no Windows Explorer.
   - Clique duas vezes no item — mesma ação.
   - Clique em **EXPORTAR LISTA** — salva todos os resultados em um `.txt` para revisão.
5. Clique em **DIAGNÓSTICO** para ver estatísticas detalhadas da varredura.
6. Clique em **PARAR** a qualquer momento para interromper a varredura.

---

## Diagnóstico

O botão **DIAGNÓSTICO** abre uma janela com:

- Total de pastas/arquivos verificados
- Itens encontrados separados por tipo (Resquícios, Obsoletos, Duplicados)
- Itens ignorados automaticamente, separados por motivo:
  - Pastas/arquivos do sistema
  - Arquivos em uso
  - Pastas da lista negra
  - Extensões ignoradas
- Erros e avisos
- Estatísticas de logs por nível (INFO, SUCESSO, AVISO, ERRO, CRÍTICO)

---

## Estrutura do projeto

```
Misa-cleaner/
├── main.py                # Ponto de entrada
├── ui.py                  # Interface Tkinter (thread-safe)
├── scanner.py             # Lógica de varredura (3 camadas)
├── logger.py              # Sistema de logs centralizado
├── matrix_rain.py         # Efeito visual de chuva de código
├── test_matrix.py         # Testes automatizados do MatrixRain
├── requirements.txt       # Deps de runtime (nenhuma externa)
├── requirements-dev.txt   # Deps de desenvolvimento (pytest)
├── README.md              # Este arquivo
├── LICENSE                # Licença MIT
└── assets/                # Imagens e recursos
```

### Arquitetura

```
┌──────────────┐
│   main.py    │  ← ponto de entrada
└──────┬───────┘
       │
       ▼
┌──────────────┐     callbacks     ┌──────────────┐
│    ui.py     │ ←──────────────── │  logger.py   │
│  (Tkinter)   │                   │  (central)   │
└──────┬───────┘                   └──────┬───────┘
       │                                  │
       │ usa                              │ usa
       ▼                                  ▼
┌──────────────┐                   ┌──────────────┐
│matrix_rain.py│                   │ scanner.py   │
│  (visual)    │                   │ (3 camadas)  │
└──────────────┘                   └──────────────┘
```

O `ui.py` não conhece o `scanner.py` diretamente. Ele só recebe eventos via `logger` e via callbacks (`callback_progresso`, `callback_resultado`). Isso permite testar o scanner isoladamente.

---

## Desenvolvimento

### Rodar os testes

```bash
pip install -r requirements-dev.txt
python test_matrix.py
# ou
pytest test_matrix.py -v
```

Saída esperada:

```
OK: 100 colunas criadas
OK: parar() cancelou o after
OK: parar() idempotente
OK: destroy() apos parar() sem crash

Todos os testes do MatrixRain passaram
```

---

## Gerar executável (.exe)

Requer `pyinstaller`:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name MisaCleaner main.py
```

O executável será gerado em `dist/MisaCleaner.exe`.

**Tamanho esperado:** ~10 MB (o projeto não tem dependências externas).

---

## Segurança

- A ferramenta **nunca** deleta arquivos. Ela apenas lista.
- Pastas do sistema são protegidas por lista negra.
- Arquivos em uso por outros processos são detectados e ignorados.
- Erros de permissão são capturados silenciosamente.
- O código usa apenas a biblioteca padrão do Python — sem dependências de terceiros que possam ser comprometidas.

**Ainda assim:** revise manualmente cada item antes de deletar. O scanner pode ter falsos positivos. Arquivos em `AppData` nem sempre são seguros de remover — alguns são recriados pelo Windows, outros são usados por programas em execução.

**Recomendação:** antes de deletar qualquer coisa, faça um backup ou use a opção **EXPORTAR LISTA** para salvar o que foi encontrado.

---

## Licença

MIT. Veja [LICENSE](LICENSE) para detalhes.

---

## Autor

Desenvolvido por **Misa Andrejezieski**.

Repositório: [github.com/MisaAndrejezieski/Misa-cleaner](https://github.com/MisaAndrejezieski/Misa-cleaner)

Se este projeto foi útil, considere dar uma ⭐ no repositório.