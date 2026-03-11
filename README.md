# YouTube Transcript MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server that
provides YouTube transcript retrieval as tools for AI assistants. Built on top
of [`youtube-transcript-api`](https://github.com/jdepoix/youtube-transcript-api).

## Features

- **`get_transcript`** -- Fetch the transcript of a YouTube video with
  timestamps. Supports video IDs and full URLs, language selection, and optional
  HTML formatting preservation.
- **`list_transcripts`** -- List all available transcript languages for a video.

## Supported URL Formats

The server accepts YouTube video IDs and URLs in the following formats:

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- `https://www.youtube.com/live/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/v/VIDEO_ID`
- Raw 11-character video IDs (e.g. `dQw4w9WgXcQ`)

## Installation

```bash
uv sync
```

## Usage

### Stdio transport (standard for MCP clients)

```bash
uv run mcp run main.py
```

### Integration with Claude Desktop / VS Code

Add the following configuration to your MCP settings. Replace the path with the
absolute path to your local clone of this repository:

```json
{
  "mcpServers": {
    "youtube-transcript": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/youtube-mcp",
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

| Parameter             | Type        | Description                                                        |
| --------------------- | ----------- | ------------------------------------------------------------------ |
| `video_id_or_url`     | `str`       | YouTube video ID or full URL                                       |
| `languages`           | `list[str]` | Preferred languages in descending priority (default: `["en"]`)     |
| `preserve_formatting` | `bool`      | Keep HTML formatting tags like `<i>` and `<b>` (default: `false`)  |

### `list_transcripts`

| Parameter         | Type  | Description                  |
| ----------------- | ----- | ---------------------------- |
| `video_id_or_url` | `str` | YouTube video ID or full URL |

## Development

Install dev dependencies:

```bash
uv sync --dev
```

Run linting and type checking:

```bash
uv run ruff check main.py    # linter
uv run ruff format main.py   # formatter
uv run mypy main.py          # type checker
```
