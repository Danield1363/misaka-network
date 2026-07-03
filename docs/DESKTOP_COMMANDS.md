# Desktop Commands

Comandos operacionais sao tratados pelo backend antes do LLM. A resposta do chat inclui `metadata.client_action`, e a dashboard executa a acao real pela bridge Electron quando disponivel.

## Apps

| Frase | client_action |
| --- | --- |
| `abrir notepad` | `open_app: notepad` |
| `abrir bloco de notas` | `open_app: notepad` |
| `abrir explorer` | `open_app: explorer` |
| `abrir calculadora` | `open_app: calculator` |
| `abrir discord` | `open_app: discord` |
| `abrir vs code` | `open_app: vscode` |
| `abrir chrome` | `open_app: chrome` |
| `abrir edge` | `open_app: edge` |

## Sites E Pesquisas

| Frase | Resultado |
| --- | --- |
| `abra o youtube` | Abre `https://www.youtube.com` |
| `Misaka, abra o YouTube` | Abre `https://www.youtube.com` |
| `abrir canal do alanzoka no youtube` | Abre busca YouTube por `alanzoka canal` |
| `abrir video do alanzoka de minecraft` | Abre busca YouTube por `alanzoka minecraft video` |
| `pesquise wake on lan no google` | Abre busca Google |
| `pesquise misaka network no github` | Abre busca GitHub |
| `pesquise cobblemon no modrinth` | Abre busca Modrinth |
| `procure atm 10 no curseforge` | Abre busca CurseForge |

## Respostas Do Dashboard

Sucesso URL:

```text
Pagina aberta, diz Misaka Misaka.
```

Sucesso app:

```text
Bloco de Notas aberto no seu computador, diz Misaka Misaka.
Explorador de Arquivos aberto no seu computador, diz Misaka Misaka.
```

Falha app:

```text
Nao consegui abrir {app}. Motivo: {erro}, diz Misaka Misaka.
```

## Seguranca

Comandos perigosos como `desligar computador`, `reiniciar computador`, `apagar arquivo`, `formatar`, `comprar` e `pagar` nao executam diretamente. A voz bloqueia comandos perigosos e o backend retorna confirmacao se receber esse texto.
