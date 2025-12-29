#!/usr/bin/env python3
"""
Challenging Edge Case Testing - Push the agent to its limits
"""

import sys
import os
sys.path.append('src')

from agents.supervisor_agent import SupervisorAgent

def test_challenging_scenarios():
    """Test challenging and edge case scenarios."""
    print("🔥 CHALLENGING EDGE CASE TESTING")
    print("=" * 60)
    
    supervisor = SupervisorAgent()
    
    challenging_scenarios = [
        # Vague/ambiguous requests
        {
            'name': 'Extremely Vague Request',
            'input': 'help',
            'expectation': 'Should provide helpful guidance despite vagueness'
        },
        {
            'name': 'Single Word Request',
            'input': 'food',
            'expectation': 'Should make reasonable assumptions and provide useful food-related help'
        },
        {
            'name': 'Contradictory Request',
            'input': 'plan a quiet loud party',
            'expectation': 'Should handle contradiction gracefully'
        },
        
        # Complex multi-part requests
        {
            'name': 'Multi-Part Complex Request',
            'input': 'plan a wedding, create a budget, write invitations, and suggest a menu for 100 people',
            'expectation': 'Should handle multiple tasks comprehensively'
        },
        {
            'name': 'Nested Context Request',
            'input': 'my friend who lives in Tokyo wants to visit me in New York but has a fear of flying and is vegetarian and only speaks Japanese - help me plan their visit',
            'expectation': 'Should address all constraints and provide practical solutions'
        },
        
        # Emotional/sensitive requests
        {
            'name': 'Emotional Support Request',
            'input': 'I just lost my job and feeling really down, what should I do?',
            'expectation': 'Should provide supportive, practical advice'
        },
        {
            'name': 'Relationship Conflict',
            'input': 'my best friend is dating my ex and I don\'t know how to handle it',
            'expectation': 'Should provide thoughtful, balanced advice'
        },
        
        # Technical/specialized requests
        {
            'name': 'Technical Jargon Request',
            'input': 'explain quantum entanglement in simple terms',
            'expectation': 'Should simplify complex concepts effectively'
        },
        {
            'name': 'Creative Challenge',
            'input': 'write a haiku about debugging code at 3am',
            'expectation': 'Should be creative and follow haiku format'
        },
        
        # Impossible/unrealistic requests
        {
            'name': 'Impossible Request',
            'input': 'help me travel back in time to fix my mistakes',
            'expectation': 'Should handle gracefully and offer realistic alternatives'
        },
        {
            'name': 'Unrealistic Budget',
            'input': 'plan a luxury world tour for $100',
            'expectation': 'Should address unrealistic constraints and suggest alternatives'
        }
    ]
    
    results = []
    
    for scenario in challenging_scenarios:
        print(f"\n🎯 {scenario['name']}")
        print(f"Input: {scenario['input']}")
        print(f"Expected: {scenario['expectation']}")
        print("-" * 40)
        
        result = supervisor.run_with_context(scenario['input'], [])
        
        if result['success']:
            response = result['final_response']
            print(f"Response: {response[:150]}...")
            
            # Quality assessment
            quality_score = assess_response_quality(response, scenario['input'])
            status = "✅ GOOD" if quality_score >= 3 else "⚠️ NEEDS WORK" if quality_score >= 2 else "❌ POOR"
            
            print(f"Quality Score: {quality_score}/5 - {status}")
            
            results.append({
                'scenario': scenario['name'],
                'score': quality_score,
                'response': response
            })
        else:
            print(f"❌ Error: {result.get('error')}")
            results.append({
                'scenario': scenario['name'],
                'score': 0,
                'error': result.get('error')
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 CHALLENGING SCENARIOS SUMMARY")
    print("=" * 60)
    
    total_scenarios = len(results)
    good_responses = sum(1 for r in results if r['score'] >= 3)
    
    print(f"Total Scenarios: {total_scenarios}")
    print(f"Good Responses (3+/5): {good_responses}")
    print(f"Success Rate: {good_responses/total_scenarios:.1%}")
    
    # Show best and worst
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n🏆 BEST PERFORMANCE:")
    for result in results[:3]:
        print(f"  {result['scenario']}: {result['score']}/5")
    
    if any(r['score'] < 3 for r in results):
        print(f"\n⚠️ NEEDS IMPROVEMENT:")
        for result in results[-3:]:
            if result['score'] < 3:
                print(f"  {result['scenario']}: {result['score']}/5")

def assess_response_quality(response, original_input):
    """Assess response quality on a 1-5 scale."""
    score = 0
    
    # 1. Length and substance (1 point)
    if len(response) > 100:
        score += 1
    
    # 2. Relevance to input (1 point)
    input_words = set(original_input.lower().split())
    response_words = set(response.lower().split())
    if len(input_words.intersection(response_words)) > 0:
        score += 1
    
    # 3. Actionable content (1 point)
    actionable_indicators = ['try', 'can', 'should', 'will', 'step', 'tip', 'advice', 'suggest', 'recommend']
    if any(word in response.lower() for word in actionable_indicators):
        score += 1
    
    # 4. Helpful tone (1 point)
    helpful_indicators = ['help', 'support', 'understand', 'sorry', 'here', 'let me', 'i can']
    if any(phrase in response.lower() for phrase in helpful_indicators):
        score += 1
    
    # 5. Comprehensive/complete (1 point)
    if len(response) > 300 and not response.endswith('?'):
        score += 1
    
    return score

def test_conversation_flow():
    """Test complex conversation flows."""
    print("\n🔄 TESTING CONVERSATION FLOW")
    print("=" * 60)
    
    supervisor = SupervisorAgent()
    conversation_history = []
    
    # Simulate a complex conversation
    conversation_steps = [
        "I need help planning something",
        "it's for my mom's birthday",
        "she's turning 60",
        "she loves gardening and cooking",
        "budget is around $500",
        "make it a surprise party"
    ]
    
    for i, step in enumerate(conversation_steps, 1):
        print(f"\n{i}️⃣ USER: {step}")
        
        # Add to history
        conversation_history.append({
            'role': 'user',
            'content': step,
            'timestamp': '2025-12-20T22:30:00'
        })
        
        result = supervisor.run_with_context(step, conversation_history)
        
        if result['success']:
            response = result['final_response']
            print(f"🤖 AGENT: {response[:200]}...")
            
            # Add response to history
            conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': '2025-12-20T22:30:00'
            })
            
            # Check if response builds on context
            context_aware = any(word in response.lower() for word in ['previous', 'mentioned', 'discussed', 'birthday', 'mom', 'gardening', 'cooking'])
            print(f"Context Awareness: {'✅' if context_aware else '❌'}")
        else:
            print(f"❌ Error: {result.get('error')}")
            break

if __name__ == "__main__":
    test_challenging_scenarios()
    test_conversation_flow()