"""
Gamma API Client for Victoria Terminal

This module provides a client for interacting with the Gamma Generate API
to create presentations, documents, and social media content programmatically.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union
import requests
from rich.console import Console

console = Console()


class GammaAPIError(Exception):
    """Custom exception for Gamma API errors."""
    pass


class GammaClient:
    """Client for interacting with the Gamma Generate API."""
    
    BASE_URL = "https://public-api.gamma.app/v0.2"
    
    def __init__(self, api_key: str):
        """
        Initialize the Gamma API client.
        
        Args:
            api_key: The Gamma API key (format: sk-gamma-xxxxxxxx)
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-KEY': api_key,
            'accept': 'application/json'
        })
    
    def generate_presentation(
        self,
        input_text: str,
        text_mode: str = "generate",
        format_type: str = "presentation",
        theme_name: Optional[str] = None,
        num_cards: int = 10,
        card_split: str = "auto",
        additional_instructions: Optional[str] = None,
        export_as: Optional[str] = None,
        text_options: Optional[Dict[str, Any]] = None,
        image_options: Optional[Dict[str, Any]] = None,
        card_options: Optional[Dict[str, Any]] = None,
        sharing_options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a presentation using the Gamma API.
        
        Args:
            input_text: Text content for the presentation
            text_mode: How to modify input text (generate, condense, preserve)
            format_type: Type of content (presentation, document, social)
            theme_name: Name of the Gamma theme to use
            num_cards: Number of cards/slides to create
            card_split: How to divide content (auto, inputTextBreaks)
            additional_instructions: Extra specifications
            export_as: Export format (pdf, pptx)
            text_options: Text generation options
            image_options: Image generation options
            card_options: Card layout options
            sharing_options: Sharing permissions
            
        Returns:
            Generation ID for tracking the request
            
        Raises:
            GammaAPIError: If the API request fails
        """
        payload = {
            "inputText": input_text,
            "textMode": text_mode,
            "format": format_type,
            "numCards": num_cards,
            "cardSplit": card_split
        }
        
        # Add optional parameters
        if theme_name:
            payload["themeName"] = theme_name
        if additional_instructions:
            payload["additionalInstructions"] = additional_instructions
        if export_as:
            payload["exportAs"] = export_as
        if text_options:
            payload["textOptions"] = text_options
        if image_options:
            payload["imageOptions"] = image_options
        if card_options:
            payload["cardOptions"] = card_options
        if sharing_options:
            payload["sharingOptions"] = sharing_options
        
        try:
            response = self.session.post(
                f"{self.BASE_URL}/generations",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("generationId")
            
        except requests.exceptions.RequestException as e:
            raise GammaAPIError(f"Failed to generate presentation: {e}")
        except json.JSONDecodeError as e:
            raise GammaAPIError(f"Invalid JSON response: {e}")
    
    def check_generation_status(self, generation_id: str) -> Dict[str, Any]:
        """
        Check the status of a generation request.
        
        Args:
            generation_id: The ID returned from generate_presentation
            
        Returns:
            Dictionary containing status information
            
        Raises:
            GammaAPIError: If the API request fails
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/generations/{generation_id}"
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise GammaAPIError(f"Failed to check generation status: {e}")
        except json.JSONDecodeError as e:
            raise GammaAPIError(f"Invalid JSON response: {e}")
    
    def wait_for_completion(
        self,
        generation_id: str,
        timeout: int = 300,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        Wait for a generation to complete.
        
        Args:
            generation_id: The ID returned from generate_presentation
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds
            
        Returns:
            Final generation status
            
        Raises:
            GammaAPIError: If generation fails or times out
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.check_generation_status(generation_id)
            
            if status.get("status") == "completed":
                return status
            elif status.get("status") == "failed":
                error_msg = status.get("error", "Unknown error")
                raise GammaAPIError(f"Generation failed: {error_msg}")
            
            time.sleep(poll_interval)
        
        raise GammaAPIError(f"Generation timed out after {timeout} seconds")
    
    def download_file(self, url: str, file_path: Union[str, Path]) -> None:
        """
        Download a file from a URL.
        
        Args:
            url: URL of the file to download
            file_path: Local path where the file should be saved
            
        Raises:
            GammaAPIError: If the download fails
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
        except requests.exceptions.RequestException as e:
            raise GammaAPIError(f"Failed to download file: {e}")
        except IOError as e:
            raise GammaAPIError(f"Failed to save file: {e}")
    
    def create_presentation_from_file(
        self,
        input_file: Union[str, Path],
        output_dir: Union[str, Path],
        **kwargs
    ) -> Path:
        """
        Create a presentation from a text file.
        
        Args:
            input_file: Path to the input text file
            output_dir: Directory to save the generated presentation
            **kwargs: Additional parameters for generate_presentation
            
        Returns:
            Path to the generated presentation file
            
        Raises:
            GammaAPIError: If the process fails
        """
        input_file = Path(input_file)
        output_dir = Path(output_dir)
        
        if not input_file.exists():
            raise GammaAPIError(f"Input file not found: {input_file}")
        
        # Read input text
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                input_text = f.read()
        except IOError as e:
            raise GammaAPIError(f"Failed to read input file: {e}")
        
        # Generate presentation
        console.print("[cyan]🚀 Starting presentation generation...")
        generation_id = self.generate_presentation(input_text, **kwargs)
        
        console.print(f"[cyan]📋 Generation ID: {generation_id}")
        console.print("[cyan]⏳ Waiting for completion...")
        
        # Wait for completion
        result = self.wait_for_completion(generation_id)
        
        # Download the file if export format was specified
        export_format = kwargs.get('export_as')
        if export_format and 'downloadUrls' in result:
            download_urls = result['downloadUrls']
            
            if export_format in download_urls:
                file_extension = 'pdf' if export_format == 'pdf' else 'pptx'
                output_file = output_dir / f"{input_file.stem}_presentation.{file_extension}"
                
                console.print(f"[cyan]📥 Downloading {export_format.upper()} file...")
                self.download_file(download_urls[export_format], output_file)
                
                console.print(f"[green]✅ Presentation saved to: {output_file}")
                return output_file
        
        # Return the Gamma URL if no download was performed
        gamma_url = result.get('url', '')
        console.print(f"[green]✅ Presentation created: {gamma_url}")
        
        # Save URL to a text file
        output_dir.mkdir(parents=True, exist_ok=True)
        url_file = output_dir / f"{input_file.stem}_presentation_url.txt"
        with open(url_file, 'w') as f:
            f.write(gamma_url)
        
        return url_file
