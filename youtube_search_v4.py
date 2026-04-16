import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi
import time
import random
import requests

# --- CONFIGURATION ---
CHANNEL_HANDLE = "@CHRBRG"
SEARCH_PHRASES = ["chipmunk", "forest", "earthly", "possessions"]
MIN_DELAY = 2
MAX_DELAY = 5


def search_channel_transcripts(handle, phrases):
    print(f"🔍 Fetching video list for {handle}...")

    video_count = 0
    checked_count = 0
    matches_found = 0

    # Create a session with browser-like headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    })

    try:
        videos = scrapetube.get_channel(channel_url=f"https://www.youtube.com/{handle}")

        for video in videos:
            video_count += 1
            video_id = video['videoId']
            title = video['title']['runs'][0]['text']

            print(f"📺 [{video_count}] Checking: {title[:55]}...")

            try:
                # Use the session for the transcript API
                ytt_api = YouTubeTranscriptApi(http_client=session)
                transcript = ytt_api.fetch(video_id, languages=['en'])

                # Convert to text
                full_text = " ".join([item['text'] for item in transcript.to_raw_data()]).lower()
                checked_count += 1

                # Check each search phrase
                found_phrases = []
                for phrase in phrases:
                    if phrase.lower() in full_text:
                        found_phrases.append(phrase)

                if found_phrases:
                    matches_found += 1
                    print("\n" + "=" * 70)
                    print(f"🎯 MATCH #{matches_found}: {title}")
                    print(f"🔗 https://www.youtube.com/watch?v={video_id}")
                    print(f"📌 Keywords matched: {', '.join(found_phrases)}")

                    # Show context for first matched phrase
                    for phrase in found_phrases[:3]:  # Limit to first 3 to avoid spam
                        idx = full_text.find(phrase.lower())
                        if idx != -1:
                            start = max(0, idx - 80)
                            end = min(len(full_text), idx + len(phrase) + 80)
                            context = full_text[start:end].replace('\n', ' ')
                            print(f"   📝 \"...{context}...\"")
                    print("=" * 70 + "\n")
                else:
                    print(f"   ❌ No matches")

            except Exception as e:
                error_msg = str(e).lower()
                if "subtitles are disabled" in error_msg:
                    print(f"   ⚠️ No captions/transcript available")
                elif "could not retrieve" in error_msg:
                    print(f"   ⚠️ Transcript blocked (rate limited)")
                else:
                    print(f"   ⚠️ Error: {str(e)[:50]}")

            # Random delay with jitter
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            print(f"   ⏳ Waiting {delay:.1f}s...")
            time.sleep(delay)

    except Exception as e:
        print(f"❌ Error fetching channel: {e}")

    print("\n" + "=" * 50)
    print(f"✅ SCAN COMPLETE")
    print(f"   Total videos found: {video_count}")
    print(f"   Transcripts checked: {checked_count}")
    print(f"   Videos with matches: {matches_found}")
    print("=" * 50)


if __name__ == "__main__":
    search_channel_transcripts(CHANNEL_HANDLE, SEARCH_PHRASES)
