"""AI assistant integration for music composition and production"""
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
import os
from dataclasses import dataclass


@dataclass
class AIRequest:
    """AI request data structure"""
    prompt: str
    context: Dict[str, Any]
    max_tokens: int = 2000
    temperature: float = 0.7


@dataclass
class AIResponse:
    """AI response data structure"""
    content: str
    metadata: Dict[str, Any]
    success: bool = True
    error: Optional[str] = None


class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    def generate(self, request: AIRequest) -> AIResponse:
        """Generate AI response"""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI integration"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self._client = None
    
    def _get_client(self):
        """Lazy load OpenAI client"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package not installed")
        return self._client
    
    def generate(self, request: AIRequest) -> AIResponse:
        """Generate response using OpenAI"""
        try:
            client = self._get_client()
            
            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": request.prompt}
            ]
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            return AIResponse(
                content=response.choices[0].message.content,
                metadata={
                    "model": self.model,
                    "tokens_used": response.usage.total_tokens
                }
            )
        except Exception as e:
            return AIResponse(
                content="",
                metadata={},
                success=False,
                error=str(e)
            )
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for music production"""
        return """You are an expert music production AI assistant integrated into a DAW.
You help with:
- Chord progressions and harmony
- Melody generation and suggestions
- Arrangement and structure
- Mixing and mastering advice
- Sound design recommendations
- Music theory guidance

Provide practical, actionable advice for music producers."""


class AIAssistant:
    """
    Main AI assistant class that provides various music production features
    """
    
    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or self._create_default_provider()
        self.conversation_history: List[Dict[str, str]] = []
    
    def _create_default_provider(self) -> AIProvider:
        """Create default AI provider"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return OpenAIProvider(api_key=api_key)
        else:
            print("Warning: No AI provider configured")
            return None
    
    def suggest_chords(
        self, 
        key: str, 
        style: str = "pop",
        num_chords: int = 4
    ) -> AIResponse:
        """
        Suggest chord progressions
        
        Args:
            key: Musical key (e.g., "C major", "A minor")
            style: Music style (e.g., "pop", "jazz", "rock")
            num_chords: Number of chords to suggest
            
        Returns:
            AIResponse with chord suggestions
        """
        prompt = f"""Suggest a {num_chords}-chord progression in {key} 
for a {style} song. Provide the chord symbols and explain why 
this progression works."""
        
        request = AIRequest(
            prompt=prompt,
            context={"key": key, "style": style}
        )
        
        return self.provider.generate(request)
    
    def generate_melody(
        self,
        key: str,
        chord_progression: List[str],
        style: str = "pop"
    ) -> AIResponse:
        """
        Generate melody suggestions
        
        Args:
            key: Musical key
            chord_progression: List of chord symbols
            style: Music style
            
        Returns:
            AIResponse with melody suggestions
        """
        chords_str = " - ".join(chord_progression)
        prompt = f"""Given this chord progression in {key}: {chords_str}
Suggest a memorable melody for a {style} song. Describe the melodic 
contour, rhythm, and specific notes."""
        
        request = AIRequest(
            prompt=prompt,
            context={
                "key": key,
                "chords": chord_progression,
                "style": style
            }
        )
        
        return self.provider.generate(request)
    
    def analyze_arrangement(
        self,
        track_info: List[Dict[str, Any]]
    ) -> AIResponse:
        """
        Analyze arrangement and suggest improvements
        
        Args:
            track_info: List of track information dictionaries
            
        Returns:
            AIResponse with arrangement suggestions
        """
        tracks_description = "\n".join([
            f"- {t.get('name', 'Track')}: {t.get('type', 'unknown')}"
            for t in track_info
        ])
        
        prompt = f"""Analyze this DAW arrangement and suggest improvements:
{tracks_description}

Provide specific advice on:
1. Frequency balance
2. Spatial positioning
3. Energy flow
4. Missing elements"""
        
        request = AIRequest(
            prompt=prompt,
            context={"tracks": track_info}
        )
        
        return self.provider.generate(request)
    
    def mixing_advice(
        self,
        track_name: str,
        track_type: str,
        issues: List[str]
    ) -> AIResponse:
        """
        Get mixing advice for a track
        
        Args:
            track_name: Name of the track
            track_type: Type of track (drums, bass, vocals, etc.)
            issues: List of identified issues
            
        Returns:
            AIResponse with mixing suggestions
        """
        issues_str = "\n".join([f"- {issue}" for issue in issues])
        
        prompt = f"""Provide mixing advice for a {track_type} track 
named "{track_name}".

Issues identified:
{issues_str}

Suggest specific EQ, compression, and effects settings."""
        
        request = AIRequest(
            prompt=prompt,
            context={
                "track_name": track_name,
                "track_type": track_type,
                "issues": issues
            }
        )
        
        return self.provider.generate(request)
    
    def mastering_suggestions(
        self,
        genre: str,
        target_loudness: float = -14.0
    ) -> AIResponse:
        """
        Get mastering suggestions
        
        Args:
            genre: Music genre
            target_loudness: Target LUFS
            
        Returns:
            AIResponse with mastering advice
        """
        prompt = f"""Provide mastering chain suggestions for a {genre} track 
with target loudness of {target_loudness} LUFS.

Include recommendations for:
1. EQ moves
2. Compression settings
3. Limiting
4. Stereo enhancement
5. Reference tracks"""
        
        request = AIRequest(
            prompt=prompt,
            context={"genre": genre, "target_loudness": target_loudness}
        )
        
        return self.provider.generate(request)
    
    def chat(self, message: str) -> AIResponse:
        """
        General chat interface with the AI assistant
        
        Args:
            message: User message
            
        Returns:
            AIResponse with assistant's reply
        """
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        request = AIRequest(
            prompt=message,
            context={"history": self.conversation_history}
        )
        
        response = self.provider.generate(request)
        
        if response.success:
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })
        
        return response
    
    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []
