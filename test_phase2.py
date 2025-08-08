#!/usr/bin/env python3
"""
Test script for Phase 2: Content Assessment and Generation Workflow
Tests all three scenarios with comprehensive validation
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_handler.phase2_workflow import Phase2Workflow
from config.email_config import EmailSettings

def test_scenario_1_detailed_input():
    """Test Scenario 1: Detailed user input processing."""
    print("🧪 Testing Scenario 1: Detailed User Input")
    print("=" * 60)
    
    workflow = Phase2Workflow()
    
    # Test case 1: Detailed personal experience
    detailed_content = """I had a client meeting yesterday where they told me they were struggling with employee retention. 
    They had lost 3 key team members in the last 6 months and were desperate for a solution. 
    I shared my 3-step process that I've used with other clients - first, we identify the root causes through exit interviews, 
    then we implement targeted retention strategies, and finally we create a feedback loop to measure success. 
    This approach helped another client reduce turnover by 40% in 6 months. The client was so relieved to have a clear path forward."""
    
    result = workflow.process_user_input(detailed_content, "detailed_content")
    
    print(f"✅ Success: {result['success']}")
    print(f"📝 Scenario: {result['scenario']}")
    print(f"📊 Word Count: {result['metadata']['word_count']}")
    print(f"🎯 Generation Method: {result['metadata']['generation_method']}")
    print(f"💬 Message: {result['message']}")
    print(f"\n📄 Generated Post Preview:")
    print("-" * 40)
    print(result['post'][:300] + "..." if len(result['post']) > 300 else result['post'])
    print("-" * 40)
    
    return result

def test_scenario_2_brief_topic():
    """Test Scenario 2: Brief topic input processing."""
    print("\n🧪 Testing Scenario 2: Brief Topic Input")
    print("=" * 60)
    
    workflow = Phase2Workflow()
    
    # Test case 2: Brief topic
    brief_topic = "hiring challenges"
    
    result = workflow.process_user_input(brief_topic, "general_topic")
    
    print(f"✅ Success: {result['success']}")
    print(f"📝 Scenario: {result['scenario']}")
    print(f"📊 Word Count: {result['metadata']['word_count']}")
    print(f"🎯 Generation Method: {result['metadata']['generation_method']}")
    print(f"🔍 Insights Count: {result['metadata'].get('insights_count', 'N/A')}")
    print(f"📈 Topic Relevance: {result['metadata'].get('topic_analysis', {}).get('relevance_score', 'N/A')}")
    print(f"💬 Message: {result['message']}")
    print(f"\n📄 Generated Post Preview:")
    print("-" * 40)
    print(result['post'][:300] + "..." if len(result['post']) > 300 else result['post'])
    print("-" * 40)
    
    return result

def test_scenario_3_declined_response():
    """Test Scenario 3: Declined response processing."""
    print("\n🧪 Testing Scenario 3: Declined Response")
    print("=" * 60)
    
    workflow = Phase2Workflow()
    
    # Test case 3: User declined
    result = workflow.process_user_input("", "declined")
    
    print(f"✅ Success: {result['success']}")
    print(f"📝 Scenario: {result['scenario']}")
    print(f"📊 Word Count: {result['metadata']['word_count']}")
    print(f"🎯 Generation Method: {result['metadata']['generation_method']}")
    print(f"📈 Selected Topic: {result['metadata'].get('selected_topic', 'N/A')}")
    print(f"🔍 Insights Count: {result['metadata'].get('insights_count', 'N/A')}")
    print(f"💬 Message: {result['message']}")
    print(f"\n📄 Generated Post Preview:")
    print("-" * 40)
    print(result['post'][:300] + "..." if len(result['post']) > 300 else result['post'])
    print("-" * 40)
    
    return result

def test_error_handling():
    """Test error handling and fallback mechanisms."""
    print("\n🧪 Testing Error Handling and Fallbacks")
    print("=" * 60)
    
    workflow = Phase2Workflow()
    
    # Test with invalid content type
    result = workflow.process_user_input("test content", "invalid_type")
    
    print(f"✅ Success: {result['success']}")
    print(f"📝 Scenario: {result['scenario']}")
    print(f"📊 Word Count: {result['metadata']['word_count']}")
    print(f"🎯 Generation Method: {result['metadata']['generation_method']}")
    print(f"💬 Message: {result['message']}")
    
    return result

def test_workflow_status():
    """Test workflow status and component health."""
    print("\n🧪 Testing Workflow Status")
    print("=" * 60)
    
    workflow = Phase2Workflow()
    status = workflow.get_workflow_status()
    
    print(f"🔄 Workflow Status: {status['workflow_status']}")
    print(f"📅 Timestamp: {status['timestamp']}")
    
    print("\n🔧 Component Status:")
    for component, component_status in status['components'].items():
        print(f"  - {component}: {component_status.get('status', 'unknown')}")
    
    return status

def test_performance_metrics():
    """Test performance metrics and timing."""
    print("\n🧪 Testing Performance Metrics")
    print("=" * 60)
    
    workflow = Phase2Workflow()
    
    # Test timing for each scenario
    scenarios = [
        ("detailed_content", "I had a client meeting yesterday where they told me they were struggling with employee retention. I shared my 3-step process that helped them reduce turnover by 40% in 6 months."),
        ("general_topic", "hiring challenges"),
        ("declined", "")
    ]
    
    for content_type, content in scenarios:
        start_time = datetime.now()
        result = workflow.process_user_input(content, content_type)
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️ {content_type.upper()}: {processing_time:.2f}s")
        print(f"   Success: {result['success']}")
        print(f"   Word Count: {result['metadata']['word_count']}")
        print()

def main():
    """Main test function for Phase 2."""
    print("🚀 Phase 2: Content Assessment and Generation Workflow Test")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check configuration
    print("⚙️ Checking Configuration...")
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print("✅ OpenAI API key configured")
    else:
        print("❌ OpenAI API key not found")
        print("Required environment variables:")
        print("- OPENAI_API_KEY")
        print("- PERPLEXITY_API_KEY (optional)")
        return
    
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    if perplexity_key:
        print("✅ Perplexity API key configured")
    else:
        print("⚠️ Perplexity API key not found (will use fallback insights)")
    
    # Run all tests
    results = {}
    
    try:
        # Test Scenario 1
        results['scenario_1'] = test_scenario_1_detailed_input()
        
        # Test Scenario 2
        results['scenario_2'] = test_scenario_2_brief_topic()
        
        # Test Scenario 3
        results['scenario_3'] = test_scenario_3_declined_response()
        
        # Test error handling
        results['error_handling'] = test_error_handling()
        
        # Test workflow status
        results['workflow_status'] = test_workflow_status()
        
        # Test performance
        test_performance_metrics()
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    
    successful_tests = sum(1 for result in results.values() if result.get('success', False))
    total_tests = len(results)
    
    print(f"✅ Successful Tests: {successful_tests}/{total_tests}")
    print(f"📈 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    print("\n📋 Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if 'word_count' in result.get('metadata', {}):
            print(f"    Word Count: {result['metadata']['word_count']}")
    
    print("\n🎯 Phase 2 Testing Complete!")
    print("\nTo integrate with the complete workflow:")
    print("1. Import Phase2Workflow in main.py")
    print("2. Call process_user_input() with Phase 1 results")
    print("3. Handle the returned post and metadata")

if __name__ == "__main__":
    main() 