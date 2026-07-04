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
| `abrir spotify` | `open_app: spotify` |

Apps conhecidos e apps configurados pelo usuario nao pedem confirmacao. A bridge Electron nao executa comandos vindos da fala; ela recebe apenas a chave do app e procura essa chave no registry.

### App Registry

O desktop carrega apps de:

- `desktop/apps.json`: defaults versionados.
- `%APPDATA%/misaka-desktop/apps.json`: copia editavel criada no primeiro start.

Aliases ficam em `desktop/appAliases.json` e na copia editavel em `%APPDATA%/misaka-desktop/appAliases.json`.

Exemplo:

```json
{
  "apps": {
    "spotify": {
      "label": "Spotify",
      "command": "%APPDATA%\\Spotify\\Spotify.exe",
      "args": []
    }
  }
}
```

Se o comando for `abrir spotify` e o app nao existir no registry, o Electron retorna:

```text
Aplicativo nao configurado. Adicione no desktop/apps.json.
```

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

## Power Actions

| Frase | client_action |
| --- | --- |
| `desligar computador` | `power_action: shutdown` |
| `reiniciar computador` | `power_action: restart` |
| `suspender computador` | `power_action: sleep` |
| `bloquear computador` | `power_action: lock` |

Power actions ficam desativadas por padrao. No drawer de configuracoes:

- `Permitir energia` habilita desligar/reiniciar/suspender/bloquear.
- `Exigir confirmacao` pede confirmacao visual antes de enviar ao desktop.

O Electron executa somente as acoes fixas acima com `spawn(..., { shell: false })`.

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

Nao ha shell arbitrario. Apps sao chaves de registry, URLs aceitam apenas `http://`/`https://`, e power actions exigem configuracao explicita no desktop.
