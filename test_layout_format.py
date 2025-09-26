#!/usr/bin/env python3
"""
Test script for Gamma layout format functionality.
"""

import asyncio
import json
from unittest.mock import AsyncMock, patch
import sys
import os

# Add the current directory to the path so we can import gamma_mcp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gamma_mcp import generate_presentation, generate_and_wait_for_presentation


async def test_layout_format_parameter():
    """Test that layout format parameter is properly included in API calls."""
    
    # Mock the make_gamma_request function
    with patch('gamma_mcp.make_gamma_request') as mock_request:
        # Set up mock response
        mock_request.return_value = {
            "generationId": "test-123",
            "status": "processing"
        }
        
        # Test different layout formats
        test_cases = [
            ("16:9", "Traditional 16:9 format"),
            ("4:3", "Traditional 4:3 format"), 
            ("fluid", "Fluid/responsive format")
        ]
        
        for layout_format, description in test_cases:
            print(f"\n🧪 Testing {description} (layout_format='{layout_format}')")
            
            # Call the function with the layout format
            result = await generate_presentation(
                input_text="# Test Presentation\n\nThis is a test slide.",
                theme_name="Elcano",
                layout_format=layout_format
            )
            
            # Verify the function was called
            assert mock_request.called, "make_gamma_request should have been called"
            
            # Get the call arguments
            call_args = mock_request.call_args
            payload = call_args[1]['json']  # The JSON payload
            
            # Verify layout format is in the payload
            assert 'layoutFormat' in payload, "layoutFormat should be in the API payload"
            assert payload['layoutFormat'] == layout_format, f"layoutFormat should be '{layout_format}'"
            
            # Verify other expected fields
            expected_fields = ['inputText', 'format', 'themeName', 'additionalInstructions', 'exportAs']
            for field in expected_fields:
                assert field in payload, f"'{field}' should be in the API payload"
            
            print(f"✅ Layout format '{layout_format}' correctly included in API payload")
            print(f"   Full payload keys: {list(payload.keys())}")
            
            # Reset the mock for the next test
            mock_request.reset_mock()


async def test_generate_and_wait_layout_format():
    """Test that the convenience function also supports layout format."""
    
    with patch('gamma_mcp.make_gamma_request') as mock_request:
        # Mock successful generation
        mock_request.return_value = {
            "generationId": "test-456",
            "status": "completed",
            "downloadUrl": "https://example.com/presentation.pptx"
        }
        
        print(f"\n🧪 Testing generate_and_wait_for_presentation with layout format")
        
        # Test the convenience function
        result = await generate_and_wait_for_presentation(
            input_text="# Test Presentation\n\nThis is a test slide.",
            layout_format="4:3",
            max_attempts=1  # Don't actually wait
        )
        
        # Verify the function was called
        assert mock_request.called, "make_gamma_request should have been called"
        
        # Get the call arguments - check all calls made
        all_calls = mock_request.call_args_list
        assert len(all_calls) >= 1, "At least one API call should have been made"
        
        # Find the generation call (first call should be the generation)
        generation_call = all_calls[0]
        if 'json' in generation_call[1]:
            payload = generation_call[1]['json']
        else:
            # Handle different call structure
            payload = generation_call[0][2] if len(generation_call[0]) > 2 else None
            
        assert payload is not None, "Should have found a payload"
        assert 'layoutFormat' in payload, "layoutFormat should be in the API payload"
        assert payload['layoutFormat'] == "4:3", "layoutFormat should be '4:3'"
        
        print(f"✅ generate_and_wait_for_presentation correctly supports layout format")


async def test_default_layout_format():
    """Test that the default layout format is 16:9."""
    
    with patch('gamma_mcp.make_gamma_request') as mock_request:
        mock_request.return_value = {
            "generationId": "test-789",
            "status": "processing"
        }
        
        print(f"\n🧪 Testing default layout format")
        
        # Call without specifying layout format
        result = await generate_presentation(
            input_text="# Test Presentation\n\nThis is a test slide."
        )
        
        # Get the call arguments
        call_args = mock_request.call_args
        payload = call_args[1]['json']
        
        # Verify default is 16:9
        assert payload['layoutFormat'] == "16:9", "Default layoutFormat should be '16:9'"
        
        print(f"✅ Default layout format is correctly set to '16:9'")


def print_layout_format_guide():
    """Print a guide for using layout formats."""
    
    print("\n" + "="*60)
    print("📋 GAMMA LAYOUT FORMAT GUIDE")
    print("="*60)
    print()
    print("Available layout format options:")
    print()
    print("🖥️  '16:9' (Traditional) - Standard widescreen presentation format")
    print("    • Best for: Professional business presentations")
    print("    • Aspect ratio: 16:9 (1920x1080)")
    print("    • Export compatibility: PowerPoint, PDF")
    print()
    print("📱 '4:3' (Tall) - Traditional 4:3 aspect ratio format")
    print("    • Best for: Academic presentations, older projectors")
    print("    • Aspect ratio: 4:3 (1024x768)")
    print("    • Export compatibility: PowerPoint, PDF")
    print()
    print("🌊 'fluid' (Default/Fluid) - Responsive layout that adapts to content")
    print("    • Best for: Web presentations, variable content")
    print("    • Aspect ratio: Flexible")
    print("    • Export compatibility: Web, responsive formats")
    print()
    print("Usage examples:")
    print()
    print("# Traditional 16:9 format (recommended for most presentations)")
    print("await generate_presentation(")
    print("    input_text=content,")
    print("    layout_format='16:9'")
    print(")")
    print()
    print("# 4:3 format for traditional projectors")
    print("await generate_presentation(")
    print("    input_text=content,")
    print("    layout_format='4:3'")
    print(")")
    print()
    print("# Fluid format for responsive web presentations")
    print("await generate_presentation(")
    print("    input_text=content,")
    print("    layout_format='fluid'")
    print(")")
    print()
    print("="*60)


async def main():
    """Run all tests."""
    print("🚀 Testing Gamma Layout Format Functionality")
    print("=" * 50)
    
    try:
        await test_layout_format_parameter()
        await test_generate_and_wait_layout_format()
        await test_default_layout_format()
        
        print(f"\n🎉 All tests passed! Layout format functionality is working correctly.")
        
        print_layout_format_guide()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
