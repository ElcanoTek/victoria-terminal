#!/usr/bin/env python3
"""
Test script for Gamma layout format functionality with correct API parameters.
"""

import asyncio
import json
from unittest.mock import AsyncMock, patch
import sys
import os

# Add the current directory to the path so we can import gamma_mcp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gamma_mcp import generate_presentation, generate_and_wait_for_presentation


async def test_corrected_layout_format():
    """Test that layout format parameter uses correct API structure."""
    
    # Mock the make_gamma_request function
    with patch('gamma_mcp.make_gamma_request') as mock_request:
        # Set up mock response
        mock_request.return_value = {
            "generationId": "test-123",
            "status": "processing"
        }
        
        # Test different layout formats with correct API names
        test_cases = [
            ("16x9", "Traditional 16:9 format"),
            ("4x3", "Traditional 4:3 format"), 
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
            
            # Verify cardOptions structure is correct
            assert 'cardOptions' in payload, "cardOptions should be in the API payload"
            assert 'dimensions' in payload['cardOptions'], "dimensions should be in cardOptions"
            assert payload['cardOptions']['dimensions'] == layout_format, f"dimensions should be '{layout_format}'"
            
            # Verify layoutFormat is NOT in the payload (since it was causing the error)
            assert 'layoutFormat' not in payload, "layoutFormat should NOT be in the API payload"
            
            # Verify other expected fields
            expected_fields = ['inputText', 'format', 'themeName', 'additionalInstructions', 'exportAs']
            for field in expected_fields:
                assert field in payload, f"'{field}' should be in the API payload"
            
            print(f"✅ Layout format '{layout_format}' correctly included in cardOptions.dimensions")
            print(f"   cardOptions: {payload['cardOptions']}")
            
            # Reset the mock for the next test
            mock_request.reset_mock()


def print_corrected_layout_format_guide():
    """Print the corrected guide for using layout formats."""
    
    print("\n" + "="*60)
    print("📋 CORRECTED GAMMA LAYOUT FORMAT GUIDE")
    print("="*60)
    print()
    print("Available layout format options (corrected API format):")
    print()
    print("🖥️  '16x9' (Traditional) - Standard widescreen presentation format")
    print("    • Best for: Professional business presentations")
    print("    • Aspect ratio: 16:9 (1920x1080)")
    print("    • Export compatibility: PowerPoint, PDF")
    print()
    print("📱 '4x3' (Tall) - Traditional 4:3 aspect ratio format")
    print("    • Best for: Academic presentations, older projectors")
    print("    • Aspect ratio: 4:3 (1024x768)")
    print("    • Export compatibility: PowerPoint, PDF")
    print()
    print("🌊 'fluid' (Default/Fluid) - Responsive layout that adapts to content")
    print("    • Best for: Web presentations, variable content")
    print("    • Aspect ratio: Flexible")
    print("    • Export compatibility: Web, responsive formats")
    print()
    print("API Structure (corrected):")
    print()
    print('# Correct API payload structure:')
    print('{')
    print('  "cardOptions": {')
    print('    "dimensions": "16x9"  # NOT "layoutFormat"')
    print('  }')
    print('}')
    print()
    print("Usage examples:")
    print()
    print("# Traditional 16x9 format (recommended for most presentations)")
    print("await generate_presentation(")
    print("    input_text=content,")
    print("    layout_format='16x9'  # Note: 16x9, not 16:9")
    print(")")
    print()
    print("# 4x3 format for traditional projectors")
    print("await generate_presentation(")
    print("    input_text=content,")
    print("    layout_format='4x3'  # Note: 4x3, not 4:3")
    print(")")
    print()
    print("="*60)


async def main():
    """Run all tests."""
    print("🚀 Testing CORRECTED Gamma Layout Format Functionality")
    print("=" * 55)
    
    try:
        await test_corrected_layout_format()
        
        print(f"\n🎉 All tests passed! Corrected layout format functionality is working.")
        
        print_corrected_layout_format_guide()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
