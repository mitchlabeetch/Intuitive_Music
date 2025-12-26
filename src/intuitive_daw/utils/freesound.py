"""FreeSound API integration for sample browsing and downloading

This module provides an interface to the FreeSound.org API for searching,
previewing, and downloading audio samples directly within the DAW.
"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import os
import json
import logging
from urllib.parse import urlencode
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class FreeSoundSample:
    """Represents a sample from FreeSound"""
    id: int
    name: str
    description: str
    duration: float
    sample_rate: int
    channels: int
    bitdepth: int
    filesize: int
    license: str
    username: str
    tags: List[str]
    preview_url: str
    download_url: str
    waveform_url: str
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'FreeSoundSample':
        """Create from API JSON response"""
        previews = data.get('previews', {})
        images = data.get('images', {})
        
        return cls(
            id=data.get('id', 0),
            name=data.get('name', 'Unknown'),
            description=data.get('description', ''),
            duration=data.get('duration', 0.0),
            sample_rate=data.get('samplerate', 44100),
            channels=data.get('channels', 1),
            bitdepth=data.get('bitdepth', 16),
            filesize=data.get('filesize', 0),
            license=data.get('license', ''),
            username=data.get('username', 'Unknown'),
            tags=data.get('tags', []),
            preview_url=previews.get('preview-hq-mp3', ''),
            download_url=data.get('download', ''),
            waveform_url=images.get('waveform_m', ''),
        )


@dataclass
class SearchResult:
    """Container for search results"""
    count: int
    next_page: Optional[str]
    previous_page: Optional[str]
    samples: List[FreeSoundSample]


class FreeSoundClient:
    """
    FreeSound API client for searching and downloading samples.
    
    Usage:
        client = FreeSoundClient(api_key="your-api-key")
        results = client.search("kick drum")
        for sample in results.samples:
            client.download(sample, "~/Downloads")
    """
    
    API_BASE = "https://freesound.org/apiv2"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("FREESOUND_API_KEY")
        self.cache_dir = cache_dir or os.path.expanduser("~/.intuitive_daw/cache/freesound")
        self._http = None
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        if not self.api_key:
            logger.warning("No FreeSound API key provided. Set FREESOUND_API_KEY or pass api_key.")
    
    def _get_http(self):
        """Lazy-load HTTP client"""
        if self._http is None:
            try:
                import requests
                self._http = requests
            except ImportError:
                raise ImportError("requests library required: pip install requests")
        return self._http
    
    def _request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated API request"""
        if not self.api_key:
            raise ValueError("FreeSound API key required")
        
        http = self._get_http()
        params = params or {}
        params['token'] = self.api_key
        
        url = f"{self.API_BASE}/{endpoint}?{urlencode(params)}"
        
        response = http.get(url)
        response.raise_for_status()
        return response.json()
    
    def search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 15,
        filter_params: Optional[Dict[str, str]] = None,
        sort: str = "score"
    ) -> SearchResult:
        """
        Search for samples.
        
        Args:
            query: Search query string
            page: Page number (1-indexed)
            page_size: Results per page (max 150)
            filter_params: Additional filters (e.g., {"duration": "[0 TO 5]"})
            sort: Sort order (score, created, downloads, rating)
        
        Returns:
            SearchResult with matching samples
        """
        params = {
            'query': query,
            'page': page,
            'page_size': min(page_size, 150),
            'sort': sort,
            'fields': 'id,name,description,duration,samplerate,channels,bitdepth,'
                      'filesize,license,username,tags,previews,images,download',
        }
        
        if filter_params:
            filter_str = " ".join(f"{k}:{v}" for k, v in filter_params.items())
            params['filter'] = filter_str
        
        data = self._request('search/text', params)
        
        samples = [FreeSoundSample.from_api_response(s) for s in data.get('results', [])]
        
        return SearchResult(
            count=data.get('count', 0),
            next_page=data.get('next'),
            previous_page=data.get('previous'),
            samples=samples
        )
    
    def search_similar(
        self,
        sample_id: int,
        page: int = 1,
        page_size: int = 15
    ) -> SearchResult:
        """
        Find samples similar to a given sample.
        
        Args:
            sample_id: ID of reference sample
            page: Page number
            page_size: Results per page
        
        Returns:
            SearchResult with similar samples
        """
        params = {
            'page': page,
            'page_size': min(page_size, 150),
            'fields': 'id,name,description,duration,samplerate,channels,bitdepth,'
                      'filesize,license,username,tags,previews,images,download',
        }
        
        data = self._request(f'sounds/{sample_id}/similar', params)
        samples = [FreeSoundSample.from_api_response(s) for s in data.get('results', [])]
        
        return SearchResult(
            count=data.get('count', 0),
            next_page=data.get('next'),
            previous_page=data.get('previous'),
            samples=samples
        )
    
    def get_sample(self, sample_id: int) -> FreeSoundSample:
        """
        Get detailed information about a specific sample.
        
        Args:
            sample_id: FreeSound sample ID
        
        Returns:
            FreeSoundSample with full details
        """
        data = self._request(f'sounds/{sample_id}', {
            'fields': 'id,name,description,duration,samplerate,channels,bitdepth,'
                      'filesize,license,username,tags,previews,images,download',
        })
        return FreeSoundSample.from_api_response(data)
    
    def download_preview(
        self,
        sample: FreeSoundSample,
        output_dir: Optional[str] = None
    ) -> str:
        """
        Download sample preview (MP3, no authentication required for preview).
        
        Args:
            sample: Sample to download
            output_dir: Output directory (default: cache)
        
        Returns:
            Path to downloaded file
        """
        output_dir = output_dir or self.cache_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        safe_name = "".join(c if c.isalnum() or c in '.-_' else '_' for c in sample.name)
        filename = f"{sample.id}_{safe_name}.mp3"
        filepath = os.path.join(output_dir, filename)
        
        # Check cache
        if os.path.exists(filepath):
            logger.debug(f"Using cached preview: {filepath}")
            return filepath
        
        # Download
        http = self._get_http()
        response = http.get(sample.preview_url, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Downloaded preview: {filepath}")
        return filepath
    
    def download_full(
        self,
        sample: FreeSoundSample,
        output_dir: Optional[str] = None
    ) -> str:
        """
        Download full quality sample (requires API key with download permission).
        
        Args:
            sample: Sample to download
            output_dir: Output directory
        
        Returns:
            Path to downloaded file
        """
        if not self.api_key:
            raise ValueError("API key required for full downloads")
        
        output_dir = output_dir or self.cache_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Get download URL with auth
        http = self._get_http()
        download_url = f"{sample.download_url}?token={self.api_key}"
        
        # Determine extension from content-type or URL
        response = http.get(download_url, stream=True)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '')
        if 'wav' in content_type:
            ext = 'wav'
        elif 'flac' in content_type:
            ext = 'flac'
        elif 'ogg' in content_type:
            ext = 'ogg'
        else:
            ext = 'wav'  # Default
        
        safe_name = "".join(c if c.isalnum() or c in '.-_' else '_' for c in sample.name)
        filename = f"{sample.id}_{safe_name}.{ext}"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Downloaded full: {filepath}")
        return filepath
    
    def clear_cache(self) -> int:
        """
        Clear the preview cache.
        
        Returns:
            Number of files deleted
        """
        count = 0
        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
                count += 1
        
        logger.info(f"Cleared {count} cached files")
        return count


class SampleBrowser:
    """
    High-level sample browser for the DAW.
    Combines FreeSound search with local file browsing.
    """
    
    def __init__(
        self,
        freesound_key: Optional[str] = None,
        local_paths: Optional[List[str]] = None
    ):
        self.freesound = FreeSoundClient(api_key=freesound_key)
        self.local_paths = local_paths or [
            os.path.expanduser("~/Music"),
            os.path.expanduser("~/Downloads"),
        ]
        self._recent_searches: List[str] = []
        self._favorites: List[int] = []  # FreeSound IDs
    
    def search_online(
        self,
        query: str,
        max_duration: float = 30.0,
        **kwargs
    ) -> SearchResult:
        """
        Search FreeSound with duration filter.
        
        Args:
            query: Search query
            max_duration: Maximum sample duration in seconds
            **kwargs: Additional search parameters
        
        Returns:
            SearchResult with matching samples
        """
        filter_params = {'duration': f'[0 TO {max_duration}]'}
        
        # Track search history
        if query not in self._recent_searches:
            self._recent_searches.append(query)
            if len(self._recent_searches) > 20:
                self._recent_searches.pop(0)
        
        return self.freesound.search(query, filter_params=filter_params, **kwargs)
    
    def search_local(
        self,
        query: str,
        extensions: Optional[List[str]] = None
    ) -> List[str]:
        """
        Search local directories for audio files.
        
        Args:
            query: Filename pattern to match
            extensions: File extensions to include
        
        Returns:
            List of matching file paths
        """
        extensions = extensions or ['.wav', '.mp3', '.aiff', '.flac', '.ogg']
        query_lower = query.lower()
        results = []
        
        for base_path in self.local_paths:
            if not os.path.exists(base_path):
                continue
            
            for root, dirs, files in os.walk(base_path):
                # Limit depth
                depth = root.replace(base_path, '').count(os.sep)
                if depth > 3:
                    continue
                
                for filename in files:
                    name_lower = filename.lower()
                    ext = os.path.splitext(name_lower)[1]
                    
                    if ext in extensions and query_lower in name_lower:
                        results.append(os.path.join(root, filename))
                        
                        if len(results) >= 50:
                            return results
        
        return results
    
    def add_favorite(self, sample_id: int) -> None:
        """Add a sample to favorites"""
        if sample_id not in self._favorites:
            self._favorites.append(sample_id)
    
    def remove_favorite(self, sample_id: int) -> None:
        """Remove a sample from favorites"""
        if sample_id in self._favorites:
            self._favorites.remove(sample_id)
    
    def get_favorites(self) -> List[FreeSoundSample]:
        """Get all favorite samples"""
        samples = []
        for sample_id in self._favorites:
            try:
                samples.append(self.freesound.get_sample(sample_id))
            except Exception as e:
                logger.warning(f"Failed to fetch favorite {sample_id}: {e}")
        return samples
    
    def get_recent_searches(self) -> List[str]:
        """Get recent search queries"""
        return self._recent_searches.copy()


# Quick access functions
def search_freesound(query: str, api_key: Optional[str] = None) -> SearchResult:
    """Quick FreeSound search"""
    client = FreeSoundClient(api_key=api_key)
    return client.search(query)


def download_sample(
    sample_id: int,
    output_dir: str,
    api_key: Optional[str] = None
) -> str:
    """Quick sample download"""
    client = FreeSoundClient(api_key=api_key)
    sample = client.get_sample(sample_id)
    return client.download_preview(sample, output_dir)
