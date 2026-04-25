"""
Lyrics API client with intelligent search and fallback handling.

Uses iTunes Search API to resolve typos in artist/song names,
then uses Lyrics.ovh API to fetch the actual lyrics.
"""
import httpx
import logging
import re
from typing import Optional, List, Tuple
from urllib.parse import quote

logger = logging.getLogger(__name__)


class LyricsClient:
    """Client for fetching song lyrics from external APIs."""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.lyrics_url = "https://api.lyrics.ovh/v1"
        self.itunes_url = "https://itunes.apple.com/search"

    async def _resolve_typos(self, artist: str, title: str) -> Tuple[str, str]:
        """
        Use iTunes Search API to intelligently resolve typos.
        Returns the corrected (artist, title) or original if not found.
        """
        query = f"{artist} {title}".strip()
        url = f"{self.itunes_url}?term={quote(query)}&entity=song&limit=1"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("resultCount", 0) > 0:
                        result = data["results"][0]
                        corrected_artist = result.get("artistName", artist)
                        corrected_title = result.get("trackName", title)
                        logger.info(f"iTunes resolved: '{artist} - {title}' -> '{corrected_artist} - {corrected_title}'")
                        return corrected_artist, corrected_title
        except Exception as e:
            logger.error(f"iTunes API resolution failed: {e}")
            
        return artist, title

    def _normalize_name(self, name: str) -> str:
        """Normalize artist/song name for API queries."""
        name = name.strip()
        name = re.sub(r'^the\s+', '', name, flags=re.IGNORECASE)
        return name

    def _generate_variations(self, artist: str, title: str) -> List[Tuple[str, str]]:
        variations = []
        variations.append((artist.strip(), title.strip()))
        
        artist_norm = self._normalize_name(artist)
        if artist_norm != artist.strip():
            variations.append((artist_norm, title.strip()))
            
        variations.append((artist.lower().strip(), title.lower().strip()))
        
        title_clean = re.sub(r'\s*\([^)]*\)\s*$', '', title).strip()
        if title_clean != title.strip():
            variations.append((artist.strip(), title_clean))
            variations.append((artist_norm, title_clean))
            
        seen = set()
        unique_variations = []
        for a, t in variations:
            key = (a.lower(), t.lower())
            if key not in seen:
                seen.add(key)
                unique_variations.append((a, t))
                
        return unique_variations

    async def _try_fetch(self, artist: str, title: str) -> Optional[str]:
        try:
            artist_encoded = quote(artist, safe='')
            title_encoded = quote(title, safe='')
            url = f"{self.lyrics_url}/{artist_encoded}/{title_encoded}"
            
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict):
                        lyrics = data.get("lyrics", "").strip()
                        if lyrics and len(lyrics) > 50:
                            return lyrics
                return None
        except Exception as e:
            logger.debug(f"Error fetching lyrics for {artist} - {title}: {e}")
            return None

    async def fetch_lyrics(self, artist: str, title: str) -> Optional[str]:
        if not title:
            return None
            
        # Step 1: Intelligently resolve typos using iTunes
        artist_resolved, title_resolved = await self._resolve_typos(artist or "", title)
        
        # Step 2: Try fetching with resolved names and variations
        variations = self._generate_variations(artist_resolved, title_resolved)
        
        for artist_var, title_var in variations:
            if not artist_var:
                continue
            lyrics = await self._try_fetch(artist_var, title_var)
            if lyrics:
                return lyrics

        # Step 3: If resolved failed, fallback to original user input variations
        if artist_resolved != artist or title_resolved != title:
            orig_variations = self._generate_variations(artist or "", title)
            for artist_var, title_var in orig_variations:
                if not artist_var:
                    continue
                lyrics = await self._try_fetch(artist_var, title_var)
                if lyrics:
                    return lyrics

        logger.warning(f"Could not find lyrics for {artist} - {title}")
        return None
