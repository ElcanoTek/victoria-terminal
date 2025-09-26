#!/usr/bin/env python3
"""
Test script for the updated Gamma MCP integration on the feature branch.
"""

import asyncio
import os
import sys
from unittest.mock import patch, MagicMock

# Set environment variable before importing the module
os.environ['GAMMA_API_KEY'] = 'fake-api-key-for-testing'

# Import the module using importlib to handle the hyphen in the filename
import importlib.util
spec = importlib.util.spec_from_file_location("gamma_mcp", "gamma-mcp.py")
gamma_mcp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gamma_mcp)

generate_presentation = gamma_mcp.generate_presentation
check_presentation_status = gamma_mcp.check_presentation_status

async def test_generate_presentation():
    """Test the generate_presentation function with title and thank you slides."""
    print("=== Testing Gamma Presentation Generation (Feature Branch) ===")

    # Mock the make_gamma_request function to avoid actual API calls
    with patch.object(gamma_mcp, 'make_gamma_request') as mock_make_request:
        # Configure the mock to return a successful generation start
        mock_make_request.return_value = {
            "generationId": "test-generation-id-123",
            "status": "pending"
        }

        # Sample markdown content for the presentation body
        sample_content = """
# Campaign Analysis Overview
This presentation covers our Q4 campaign performance.

---

# Key Metrics
- CTR: 2.5%
- CPC: $0.45
- Conversions: 1,234

---

# Recommendations
- Increase budget for top-performing campaigns
- Optimize creative for mobile devices
        """

        # Test with default parameters
        print("\n--- Test 1: Default Parameters ---")
        result = await generate_presentation(input_text=sample_content)

        # Check the API call was made correctly
        assert mock_make_request.called, "make_gamma_request should have been called"
        call_args = mock_make_request.call_args
        payload = call_args[1]['json']

        print("✓ API call made successfully")
        print(f"✓ Theme used: {payload['themeName']}")
        print(f"✓ Export format: {payload['exportAs']}")

        # Verify the input text includes title and thank you slides
        input_text = payload['inputText']
        assert "# Elcano\n## 2025" in input_text, "Title slide should be included"
        assert "# Thank you\n## Elcano" in input_text, "Thank you slide should be included"
        assert sample_content.strip() in input_text, "Original content should be included"
        
        print("✓ Title slide included: '# Elcano\\n## 2025'")
        print("✓ Thank you slide included: '# Thank you\\n## Elcano'")
        print("✓ Original content preserved")

        # Verify the structure
        lines = input_text.split('\n')
        title_found = False
        thank_you_found = False
        
        for i, line in enumerate(lines):
            if line.strip() == "# Elcano" and i + 1 < len(lines) and lines[i + 1].strip() == "## 2025":
                title_found = True
            if line.strip() == "# Thank you" and i + 1 < len(lines) and lines[i + 1].strip() == "## Elcano":
                thank_you_found = True
        
        assert title_found, "Title slide structure should be correct"
        assert thank_you_found, "Thank you slide structure should be correct"
        print("✓ Slide structure is correct")

        # Test custom theme
        print("\n--- Test 2: Custom Theme ---")
        mock_make_request.reset_mock()
        result2 = await generate_presentation(
            input_text=sample_content,
            theme_name="Elcano_Light"
        )
        
        payload2 = mock_make_request.call_args[1]['json']
        assert payload2['themeName'] == 'Elcano_Light', "Custom theme should be used"
        print("✓ Custom theme 'Elcano_Light' applied correctly")

        # Test unsupported theme fallback
        print("\n--- Test 3: Unsupported Theme Fallback ---")
        mock_make_request.reset_mock()
        result3 = await generate_presentation(
            input_text=sample_content,
            theme_name="NonExistentTheme"
        )
        
        payload3 = mock_make_request.call_args[1]['json']
        assert payload3['themeName'] == 'Elcano', "Should fallback to default theme"
        print("✓ Unsupported theme correctly falls back to 'Elcano'")

        print("\n=== All Tests Passed! ===")
        return True

async def test_check_status():
    """Test the check_presentation_status function."""
    print("\n=== Testing Status Check Function ===")
    
    with patch.object(gamma_mcp, 'make_gamma_request') as mock_make_request:
        mock_make_request.return_value = {
            "generationId": "test-id-123",
            "status": "completed",
            "gammaUrl": "https://gamma.app/docs/test-presentation",
            "pptxUrl": "https://gamma.app/downloads/test.pptx"
        }
        
        result = await check_presentation_status("test-id-123")
        
        assert result['status'] == 'completed', "Status should be completed"
        assert 'gammaUrl' in result, "Should include gamma URL"
        print("✓ Status check function works correctly")

async def main():
    """Run all tests."""
    try:
        await test_generate_presentation()
        await test_check_status()
        print("\n🎉 All tests completed successfully!")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
