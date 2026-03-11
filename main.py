import logging
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
from youtube_transcript_api._transcripts import FetchedTranscript

logger = logging.getLogger(__name__)

mcp = FastMCP("YouTube Transcript")

ytt_api = YouTubeTranscriptApi()

VIDEO_ID_PATTERN = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|embed/|shorts/|live/|v/)|youtu\.be/)([\w-]{11})"
)

RAW_ID_PATTERN = re.compile(r"^[\w-]{11}$")


def extract_video_id(video_id_or_url: str) -> str | None:
    """Extract the 11-character video ID from a URL or plain ID.

    Returns the video ID string, or None if the input is not a valid
    YouTube URL or video ID.
    """
    stripped = video_id_or_url.strip()
    match = VIDEO_ID_PATTERN.search(stripped)
    if match:
        return match.group(1)
    if RAW_ID_PATTERN.match(stripped):
        return stripped
    return None


def format_transcript(transcript: FetchedTranscript) -> str:
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
    if video_id is None:
        logger.warning("Invalid video ID or URL provided: %r", video_id_or_url)
        return f"Error: '{video_id_or_url}' is not a valid YouTube video ID or URL."

    if languages is None:
        languages = ["en"]

    logger.info(
        "Fetching transcript for video '%s' (languages=%s)", video_id, languages
    )

    try:
        transcript = ytt_api.fetch(
            video_id,
            languages=languages,
            preserve_formatting=preserve_formatting,
        )
    except TranscriptsDisabled:
        logger.warning("Transcripts disabled for video '%s'", video_id)
        return f"Error: Subtitles/transcripts are disabled for video '{video_id}'."
    except NoTranscriptFound:
        logger.warning(
            "No transcript found for video '%s' in languages %s", video_id, languages
        )
        available = _list_available_languages(video_id)
        return (
            f"Error: No transcript found for video '{video_id}' "
            f"in languages {languages}.\n{available}"
        )
    except VideoUnavailable:
        logger.warning("Video '%s' is unavailable", video_id)
        return f"Error: Video '{video_id}' is unavailable."
    except InvalidVideoId:
        logger.warning("Invalid video ID: '%s'", video_id)
        return f"Error: '{video_id}' is not a valid YouTube video ID."
    except AgeRestricted:
        logger.warning("Video '%s' is age-restricted", video_id)
        return f"Error: Video '{video_id}' is age-restricted."
    except (IpBlocked, RequestBlocked):
        logger.warning("Request blocked by YouTube for video '%s'", video_id)
        return "Error: The request was blocked by YouTube. Try again later."
    except Exception as e:
        logger.error(
            "Unexpected error fetching transcript for '%s': %s",
            video_id,
            e,
            exc_info=True,
        )
        return f"Error: {e}"

    logger.info(
        "Successfully fetched transcript for '%s' (language=%s, auto-generated=%s)",
        video_id,
        transcript.language,
        transcript.is_generated,
    )

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
    if video_id is None:
        logger.warning("Invalid video ID or URL provided: %r", video_id_or_url)
        return f"Error: '{video_id_or_url}' is not a valid YouTube video ID or URL."

    logger.info("Listing transcripts for video '%s'", video_id)
    return _list_available_languages(video_id)


def _list_available_languages(video_id: str) -> str:
    """Return a formatted string of available transcript languages."""
    try:
        transcript_list = ytt_api.list(video_id)
    except Exception as e:
        logger.error(
            "Could not list transcripts for '%s': %s", video_id, e, exc_info=True
        )
        return f"Could not list transcripts: {e}"

    lines = [f"Available transcripts for '{video_id}':"]
    for t in transcript_list:
        generated = " (auto-generated)" if t.is_generated else ""
        lines.append(f"  - {t.language} [{t.language_code}]{generated}")

    if len(lines) == 1:
        lines.append("  (none)")
    return "\n".join(lines)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    mcp.run()
