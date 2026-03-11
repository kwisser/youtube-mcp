# YouTube Transcript MCP Server

Ein [Model Context Protocol](https://modelcontextprotocol.io/) Server, der
YouTube-Transkripte über die `youtube-transcript-api` bereitstellt.

## Features

- **`get_transcript`** – Transkript eines YouTube-Videos abrufen (mit
  Zeitstempeln). Unterstützt Video-IDs und volle URLs sowie Sprachwahl.
- **`list_transcripts`** – Alle verfügbaren Transkript-Sprachen für ein Video
  auflisten.

## Installation

```bash
uv sync
```

## Verwendung

### Stdio-Transport (Standard für MCP-Clients wie Claude Desktop / VS Code)

```bash
uv run mcp run main.py
```

### In Claude Desktop / VS Code einbinden

Füge folgende Konfiguration in die MCP-Settings ein:

```json
{
  "mcpServers": {
    "youtube-transcript": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absoluter/pfad/zu/youtube-mcp",
        "mcp",
        "run",
        "main.py"
      ]
    }
  }
}
```

## Tools

### `get_transcript`

| Parameter             | Typ         | Beschreibung                                                      |
| --------------------- | ----------- | ----------------------------------------------------------------- |
| `video_id_or_url`     | `str`       | YouTube Video-ID oder volle URL                                   |
| `languages`           | `list[str]` | Bevorzugte Sprachen in absteigender Priorität (default: `["en"]`) |
| `preserve_formatting` | `bool`      | HTML-Tags (`<i>`, `<b>`) beibehalten (default: `false`)           |

### `list_transcripts`

| Parameter         | Typ   | Beschreibung                    |
| ----------------- | ----- | ------------------------------- |
| `video_id_or_url` | `str` | YouTube Video-ID oder volle URL |
