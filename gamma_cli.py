#!/usr/bin/env python3
"""
Command-line interface for Gamma presentation generation in Victoria Terminal.

This script provides a CLI for generating presentations using the Gamma API
from within the Victoria Terminal environment.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from rich.console import Console
from dotenv import load_dotenv

from gamma_client import GammaClient, GammaAPIError

console = Console()

# Default Victoria home directory
DEFAULT_APP_HOME = Path.home() / "Victoria"
APP_HOME = Path(os.environ.get("VICTORIA_HOME", DEFAULT_APP_HOME))


def load_environment() -> None:
    """Load environment variables from the Victoria .env file."""
    env_file = APP_HOME / ".env"
    if env_file.exists():
        load_dotenv(env_file)


def get_gamma_client() -> GammaClient:
    """Get a configured Gamma API client."""
    api_key = os.environ.get("GAMMA_API_KEY")
    if not api_key:
        console.print("[red]❌ Gamma API key not found![/red]")
        console.print("[yellow]Please run 'victoria --reconfigure' to set up your Gamma API key.[/yellow]")
        sys.exit(1)
    
    return GammaClient(api_key)


def parse_text_options(args: argparse.Namespace) -> Optional[Dict[str, Any]]:
    """Parse text options from command line arguments."""
    text_options = {}
    
    if args.text_amount:
        text_options["amount"] = args.text_amount
    if args.text_tone:
        text_options["tone"] = args.text_tone
    if args.text_audience:
        text_options["audience"] = args.text_audience
    if args.text_language:
        text_options["language"] = args.text_language
    
    return text_options if text_options else None


def parse_image_options(args: argparse.Namespace) -> Optional[Dict[str, Any]]:
    """Parse image options from command line arguments."""
    image_options = {}
    
    if args.image_source:
        image_options["source"] = args.image_source
    if args.image_model:
        image_options["model"] = args.image_model
    if args.image_style:
        image_options["style"] = args.image_style
    
    return image_options if image_options else None


def generate_presentation(args: argparse.Namespace) -> None:
    """Generate a presentation using the Gamma API."""
    load_environment()
    client = get_gamma_client()
    
    input_file = Path(args.input)
    if not input_file.exists():
        console.print(f"[red]❌ Input file not found: {input_file}[/red]")
        sys.exit(1)
    
    output_dir = Path(args.output) if args.output else APP_HOME
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Prepare generation parameters
    kwargs = {
        "text_mode": args.text_mode,
        "format_type": args.format,
        "num_cards": args.num_cards,
        "card_split": args.card_split,
    }
    
    if args.theme:
        kwargs["theme_name"] = args.theme
    if args.instructions:
        kwargs["additional_instructions"] = args.instructions
    if args.export_as:
        kwargs["export_as"] = args.export_as
    
    # Add optional parameter groups
    text_options = parse_text_options(args)
    if text_options:
        kwargs["text_options"] = text_options
    
    image_options = parse_image_options(args)
    if image_options:
        kwargs["image_options"] = image_options
    
    try:
        result_file = client.create_presentation_from_file(
            input_file=input_file,
            output_dir=output_dir,
            **kwargs
        )
        
        console.print(f"[green]🎉 Success! Generated presentation: {result_file}[/green]")
        
    except GammaAPIError as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate presentations using the Gamma API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input report.txt --export-as pdf
  %(prog)s --input analysis.md --theme "Night Sky" --num-cards 15
  %(prog)s --input data.txt --text-tone "professional, inspiring" --image-style photorealistic
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to the input text file"
    )
    
    # Output options
    parser.add_argument(
        "--output", "-o",
        help="Output directory (defaults to Victoria home)"
    )
    parser.add_argument(
        "--export-as",
        choices=["pdf", "pptx"],
        help="Export format for the presentation"
    )
    
    # Basic generation options
    parser.add_argument(
        "--text-mode",
        choices=["generate", "condense", "preserve"],
        default="generate",
        help="How to modify the input text (default: generate)"
    )
    parser.add_argument(
        "--format",
        choices=["presentation", "document", "social"],
        default="presentation",
        help="Type of content to create (default: presentation)"
    )
    parser.add_argument(
        "--theme",
        help="Name of the Gamma theme to use"
    )
    parser.add_argument(
        "--num-cards",
        type=int,
        default=10,
        help="Number of cards/slides to create (default: 10)"
    )
    parser.add_argument(
        "--card-split",
        choices=["auto", "inputTextBreaks"],
        default="auto",
        help="How to divide content into cards (default: auto)"
    )
    parser.add_argument(
        "--instructions",
        help="Additional instructions for content generation"
    )
    
    # Text options
    text_group = parser.add_argument_group("text options")
    text_group.add_argument(
        "--text-amount",
        choices=["brief", "medium", "detailed", "extensive"],
        help="Amount of text per card"
    )
    text_group.add_argument(
        "--text-tone",
        help="Tone or voice for the content (e.g., 'professional, inspiring')"
    )
    text_group.add_argument(
        "--text-audience",
        help="Target audience description"
    )
    text_group.add_argument(
        "--text-language",
        help="Output language code (e.g., 'en', 'es', 'fr')"
    )
    
    # Image options
    image_group = parser.add_argument_group("image options")
    image_group.add_argument(
        "--image-source",
        choices=["aiGenerated"],
        help="Source for images"
    )
    image_group.add_argument(
        "--image-model",
        help="AI model for image generation (e.g., 'imagen-4-pro')"
    )
    image_group.add_argument(
        "--image-style",
        help="Style for generated images (e.g., 'photorealistic')"
    )
    
    args = parser.parse_args()
    generate_presentation(args)


if __name__ == "__main__":
    main()
