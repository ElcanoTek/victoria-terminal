#!/usr/bin/env python3
"""
Test script for the automatic polling functionality in Gamma MCP integration.
"""

import asyncio
import os
import sys
from unittest.mock import patch, MagicMock, AsyncMock

# Set environment variable before importing the module
os.environ['GAMMA_API_KEY'] = 'fake-api-key-for-testing'

# Import the module using importlib to handle the hyphen in the filename
import importlib.util
spec = importlib.util.spec_from_file_location("gamma_mcp", "gamma-mcp.py")
gamma_mcp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gamma_mcp)

# Import the functions we want to test
generate_presentation = gamma_mcp.generate_presentation
check_presentation_status = gamma_mcp.check_presentation_status
wait_for_presentation_completion = gamma_mcp.wait_for_presentation_completion
generate_and_wait_for_presentation = gamma_mcp.generate_and_wait_for_presentation

async def test_wait_for_completion_success():
    """Test successful completion after a few polling attempts."""
    print("=== Testing wait_for_presentation_completion - Success Case ===")
    
    with patch.object(gamma_mcp, 'check_presentation_status') as mock_check_status:
        # Simulate: pending -> pending -> completed
        mock_check_status.side_effect = [
            {"generationId": "test-id", "status": "pending"},
            {"generationId": "test-id", "status": "pending"},
            {
                "generationId": "test-id", 
                "status": "completed",
                "gammaUrl": "https://gamma.app/docs/test-presentation",
                "pptxUrl": "https://gamma.app/downloads/test.pptx"
            }
        ]
        
        # Mock asyncio.sleep to speed up the test
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            result = await wait_for_presentation_completion(
                generation_id="test-id",
                polling_interval=1,  # Use 1 second for testing
                max_attempts=5
            )
            
            # Verify the result
            assert result["status"] == "completed", "Should return completed status"
            assert "gammaUrl" in result, "Should include gamma URL"
            assert "pptxUrl" in result, "Should include PPTX URL"
            
            # Verify polling behavior
            assert mock_check_status.call_count == 3, "Should have made 3 status checks"
            assert mock_sleep.call_count == 2, "Should have slept 2 times (between checks)"
            
            print("✓ Successfully completed after 3 polling attempts")
            print("✓ Correct number of API calls and sleep intervals")
            print("✓ Returned complete presentation data")

async def test_wait_for_completion_timeout():
    """Test timeout when presentation takes too long."""
    print("\n=== Testing wait_for_presentation_completion - Timeout Case ===")
    
    with patch.object(gamma_mcp, 'check_presentation_status') as mock_check_status:
        # Always return pending status
        mock_check_status.return_value = {"generationId": "test-id", "status": "pending"}
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            result = await wait_for_presentation_completion(
                generation_id="test-id",
                polling_interval=1,
                max_attempts=3  # Small number for testing
            )
            
            # Verify timeout behavior
            assert "error" in result, "Should return error on timeout"
            assert "timed out" in result["error"], "Error should mention timeout"
            assert result["attempts"] == 3, "Should record correct number of attempts"
            
            # Verify polling behavior
            assert mock_check_status.call_count == 3, "Should have made 3 status checks"
            assert mock_sleep.call_count == 2, "Should have slept 2 times"
            
            print("✓ Correctly timed out after maximum attempts")
            print("✓ Returned appropriate error message")
            print("✓ Made correct number of polling attempts")

async def test_wait_for_completion_failure():
    """Test handling of failed presentation generation."""
    print("\n=== Testing wait_for_presentation_completion - Failure Case ===")
    
    with patch.object(gamma_mcp, 'check_presentation_status') as mock_check_status:
        # Simulate: pending -> failed
        mock_check_status.side_effect = [
            {"generationId": "test-id", "status": "pending"},
            {"generationId": "test-id", "status": "failed", "error": "Generation failed"}
        ]
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            result = await wait_for_presentation_completion(
                generation_id="test-id",
                polling_interval=1,
                max_attempts=5
            )
            
            # Verify failure handling
            assert result["status"] == "failed", "Should return failed status"
            assert mock_check_status.call_count == 2, "Should have made 2 status checks"
            assert mock_sleep.call_count == 1, "Should have slept 1 time"
            
            print("✓ Correctly detected failed generation")
            print("✓ Stopped polling after failure detected")

async def test_generate_and_wait():
    """Test the combined generate and wait function."""
    print("\n=== Testing generate_and_wait_for_presentation ===")
    
    with patch.object(gamma_mcp, 'generate_presentation') as mock_generate:
        with patch.object(gamma_mcp, 'wait_for_presentation_completion') as mock_wait:
            # Mock successful generation start
            mock_generate.return_value = {
                "generationId": "new-test-id",
                "status": "pending"
            }
            
            # Mock successful completion
            mock_wait.return_value = {
                "generationId": "new-test-id",
                "status": "completed",
                "gammaUrl": "https://gamma.app/docs/new-presentation"
            }
            
            sample_content = "# Test Presentation\nThis is a test."
            
            result = await generate_and_wait_for_presentation(
                input_text=sample_content,
                polling_interval=1,
                max_attempts=3
            )
            
            # Verify the workflow
            assert mock_generate.called, "Should call generate_presentation"
            assert mock_wait.called, "Should call wait_for_presentation_completion"
            assert result["status"] == "completed", "Should return completed result"
            
            # Verify the generation was called with correct parameters
            gen_call = mock_generate.call_args
            assert sample_content in gen_call[1]['input_text'], "Should pass through input text"
            
            # Verify the wait was called with correct generation ID
            wait_call = mock_wait.call_args
            assert wait_call[1]['generation_id'] == "new-test-id", "Should use returned generation ID"
            
            print("✓ Successfully combined generation and waiting")
            print("✓ Passed parameters correctly between functions")
            print("✓ Returned final completion result")

async def test_generate_and_wait_generation_failure():
    """Test generate_and_wait when initial generation fails."""
    print("\n=== Testing generate_and_wait_for_presentation - Generation Failure ===")
    
    with patch.object(gamma_mcp, 'generate_presentation') as mock_generate:
        with patch.object(gamma_mcp, 'wait_for_presentation_completion') as mock_wait:
            # Mock generation failure
            mock_generate.return_value = {
                "error": "API key invalid"
            }
            
            result = await generate_and_wait_for_presentation(
                input_text="# Test",
                polling_interval=1,
                max_attempts=3
            )
            
            # Verify error handling
            assert "error" in result, "Should return error from generation"
            assert mock_generate.called, "Should call generate_presentation"
            assert not mock_wait.called, "Should not call wait function on generation failure"
            
            print("✓ Correctly handled generation failure")
            print("✓ Did not attempt to wait when generation failed")

async def main():
    """Run all tests."""
    print("🧪 Starting Gamma Polling Tests")
    print("=" * 50)
    
    try:
        await test_wait_for_completion_success()
        await test_wait_for_completion_timeout()
        await test_wait_for_completion_failure()
        await test_generate_and_wait()
        await test_generate_and_wait_generation_failure()
        
        print("\n" + "=" * 50)
        print("🎉 All polling tests completed successfully!")
        print("\nNew MCP Tools Available:")
        print("- wait_for_presentation_completion: Automatic polling with 30s intervals")
        print("- generate_and_wait_for_presentation: One-stop generation + waiting")
        print("\nVictoria can now use these tools to avoid repeated manual status checks!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
