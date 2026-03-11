import re

from mcp.server.fastmcp import FastMCP
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    AgeRestricted,
    InvalidVideoId,
    IpBlocked,
    NoTranscriptFound,
    RequestBlocked,
    TranscriptsDisabled,
    VideoUnavailable,
)

mcp = FastMCP("YouTube Transcript")

ytt_api = YouTubeTranscriptApi()

VIDEO_ID_PATTERN = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([\w-]{11})"
)


def extract_video_id(video_id_or_url: str) -> str:
    """Extract the 11-character video ID from a URL or plain ID."""
    match = VIDEO_ID_PATTERN.search(video_id_or_url)
    if match:
        return match.group(1)
    # Assume it's already a raw video ID
    return video_id_or_url.strip()


def format_transcript(transcript) -> str:
    """Format a FetchedTranscript into readable text."""
    lines: list[str] = []
    for snippet in transcript:
        start = snippet.start
        minutes, seconds = divmod(int(start), 60)
        hours, minutes = divmod(minutes, 60)
        timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        lines.append(f"[{timestamp}] {snippet.text}")
    return "\n".join(lines)


@mcp.tool()
def get_transcript(
    video_id_or_url: str,
    languages: list[str] | None = None,
    preserve_formatting: bool = False,
) -> str:
    """Get the transcript / subtitles of a YouTube video.

    Args:
        video_id_or_url: YouTube video ID (e.g. 'dQw4w9WgXcQ') or full URL.
        languages: Preferred language codes in descending priority, e.g. ['de', 'en'].
                   Defaults to ['en'] if not specified.
        preserve_formatting: Keep HTML formatting tags like <i> and <b>.
    """
    video_id = extract_video_id(video_id_or_url)
    if languages is None:
        languages = ["en"]

    try:
        transcript = ytt_api.fetch(
            video_id,
            languages=languages,
            preserve_formatting=preserve_formatting,
        )
    except TranscriptsDisabled:
        return f"Error: Subtitles/transcripts are disabled for video '{video_id}'."
    except NoTranscriptFound:
        available = _list_available_languages(video_id)
        return (
            f"Error: No transcript found for video '{video_id}' "
            f"in languages {languages}.\n{available}"
        )
    except VideoUnavailable:
        return f"Error: Video '{video_id}' is unavailable."
    except InvalidVideoId:
        return f"Error: '{video_id}' is not a valid YouTube video ID."
    except AgeRestricted:
        return f"Error: Video '{video_id}' is age-restricted."
    except (IpBlocked, RequestBlocked):
        return "Error: The request was blocked by YouTube. Try again later."
    except Exception as e:
        return f"Error: {e}"

    header = (
        f"Transcript for video '{video_id}' "
        f"(language: {transcript.language}, "
        f"auto-generated: {transcript.is_generated})\n\n"
    )
    return header + format_transcript(transcript)


@mcp.tool()
def list_transcripts(video_id_or_url: str) -> str:
    """List all available transcript languages for a YouTube video.

    Args:
        video_id_or_url: YouTube video ID or full URL.
    """
    video_id = extract_video_id(video_id_or_url)
    return _list_available_languages(video_id)


def _list_available_languages(video_id: str) -> str:
    """Return a formatted string of available transcript languages."""
    try:
        transcript_list = ytt_api.list(video_id)
    except Exception as e:
        return f"Could not list transcripts: {e}"

    lines = [f"Available transcripts for '{video_id}':"]
    for t in transcript_list:
        generated = " (auto-generated)" if t.is_generated else ""
        lines.append(f"  - {t.language} [{t.language_code}]{generated}")

    if len(lines) == 1:
        lines.append("  (none)")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
