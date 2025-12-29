#!/usr/bin/env python3
"""
Comprehensive Scenario Testing - Test different scenarios and fix issues
"""

import sys
import os
sys.path.append('src')

from agents.supervisor_agent import SupervisorAgent
from datetime import datetime

class ScenarioTester:
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.test_results = []
    
    def test_scenario(self, scenario_name, conversation_history, user_input, expected_qualities):
        """Test a specific scenario and check output quality."""
        print(f"\n🎯 TESTING: {scenario_name}")
        print("=" * 60)
        print(f"Input: {user_input}")
        print(f"Expected: {', '.join(expected_qualities)}")
        print("-" * 40)
        
        result = self.supervisor.run_with_context(user_input, conversation_history)
        
        if result['success']:
            response = result['final_response']
            print(f"Response: {response[:200]}...")
            
            # Check quality metrics
            quality_checks = self.check_response_quality(response, expected_qualities)
            
            # Overall score
            score = sum(quality_checks.values()) / len(quality_checks)
            status = "✅ PASS" if score >= 0.7 else "❌ FAIL"
            
            print(f"\nQuality Analysis:")
            for check, passed in quality_checks.items():
                print(f"  {check}: {'✅' if passed else '❌'}")
            print(f"Overall Score: {score:.1%} - {status}")
            
            self.test_results.append({
                'scenario': scenario_name,
                'score': score,
                'response': response,
                'quality_checks': quality_checks
            })
            
        else:
            print(f"❌ Error: {result.get('error')}")
            self.test_results.append({
                'scenario': scenario_name,
                'score': 0.0,
                'response': None,
                'error': result.get('error')
            })
    
    def check_response_quality(self, response, expected_qualities):
        """Check if response meets quality expectations."""
        checks = {}
        
        # Length check - should be substantial
        checks['Substantial Length'] = len(response) > 100
        
        # Actionable content
        actionable_keywords = ['template', 'example', 'here\'s', 'step', 'try', 'use', 'can', 'will']
        checks['Actionable'] = any(keyword in response.lower() for keyword in actionable_keywords)
        
        # Not too many questions
        checks['Not Question-Heavy'] = response.count('?') <= 2
        
        # Specific to expected qualities
        if 'template' in expected_qualities:
            checks['Contains Template'] = 'template' in response.lower() or '"' in response
        
        if 'specific_details' in expected_qualities:
            checks['Specific Details'] = any(word in response.lower() for word in ['specific', 'example', 'step', 'detail'])
        
        if 'practical' in expected_qualities:
            checks['Practical'] = any(word in response.lower() for word in ['practical', 'use', 'try', 'can', 'will', 'should'])
        
        if 'complete' in expected_qualities:
            checks['Complete Answer'] = len(response) > 200 and not response.endswith('?')
        
        if 'context_aware' in expected_qualities:
            checks['Context Aware'] = any(word in response.lower() for word in ['previous', 'conversation', 'mentioned', 'discussed'])
        
        return checks
    
    def run_all_scenarios(self):
        """Run comprehensive scenario testing."""
        print("🧪 COMPREHENSIVE SCENARIO TESTING")
        print("=" * 70)
        
        scenarios = [
            # Invitation scenarios
            {
                'name': 'Simple Party Invitation',
                'history': [],
                'input': 'invite a friend to a party',
                'expected': ['template', 'actionable', 'specific_details']
            },
            {
                'name': 'Dinner Party Follow-up',
                'history': [
                    {'role': 'user', 'content': 'invite a friend to a party'},
                    {'role': 'assistant', 'content': 'Here\'s a party invitation template...'}
                ],
                'input': 'make it for a dinner party',
                'expected': ['template', 'context_aware', 'specific_details']
            },
            {
                'name': 'Casual Style Request',
                'history': [
                    {'role': 'user', 'content': 'invite a friend to a party'},
                    {'role': 'assistant', 'content': 'Here\'s a party invitation...'},
                    {'role': 'user', 'content': 'make it for a dinner party'},
                    {'role': 'assistant', 'content': 'Here\'s a dinner invitation...'}
                ],
                'input': 'make it casual',
                'expected': ['template', 'context_aware', 'actionable']
            },
            
            # Planning scenarios
            {
                'name': 'Trip Planning',
                'history': [],
                'input': 'plan a 5 day trip to Paris for 2 people',
                'expected': ['complete', 'specific_details', 'practical']
            },
            {
                'name': 'Budget Planning',
                'history': [],
                'input': 'create a monthly budget for $4000 income',
                'expected': ['complete', 'specific_details', 'practical']
            },
            {
                'name': 'Event Planning',
                'history': [],
                'input': 'help me plan a birthday party for my friend',
                'expected': ['complete', 'specific_details', 'actionable']
            },
            
            # Question scenarios
            {
                'name': 'Simple Question',
                'history': [],
                'input': 'what are good study tips?',
                'expected': ['complete', 'practical', 'actionable']
            },
            {
                'name': 'Follow-up Question',
                'history': [
                    {'role': 'user', 'content': 'what are good study tips?'},
                    {'role': 'assistant', 'content': 'Here are some effective study tips...'}
                ],
                'input': 'what about for math specifically?',
                'expected': ['context_aware', 'specific_details', 'practical']
            },
            
            # Creative scenarios
            {
                'name': 'Recipe Request',
                'history': [],
                'input': 'give me a recipe for chocolate cake',
                'expected': ['complete', 'specific_details', 'actionable']
            },
            {
                'name': 'Email Template',
                'history': [],
                'input': 'write a professional email to request time off',
                'expected': ['template', 'specific_details', 'actionable']
            },
            
            # Problem-solving scenarios
            {
                'name': 'Technical Help',
                'history': [],
                'input': 'my computer is running slow, what should I do?',
                'expected': ['complete', 'practical', 'actionable']
            },
            {
                'name': 'Relationship Advice',
                'history': [],
                'input': 'how do I apologize to a friend after an argument?',
                'expected': ['practical', 'actionable', 'specific_details']
            }
        ]
        
        for scenario in scenarios:
            self.test_scenario(
                scenario['name'],
                scenario['history'],
                scenario['input'],
                scenario['expected']
            )
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary and identify issues."""
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['score'] >= 0.7)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {passed_tests/total_tests:.1%}")
        
        # Identify common issues
        print("\n🔍 COMMON ISSUES FOUND:")
        issue_counts = {}
        
        for result in self.test_results:
            if result['score'] < 0.7 and 'quality_checks' in result:
                for check, passed in result['quality_checks'].items():
                    if not passed:
                        issue_counts[check] = issue_counts.get(check, 0) + 1
        
        for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {issue}: {count} failures")
        
        # Show worst performing scenarios
        print("\n❌ SCENARIOS NEEDING IMPROVEMENT:")
        failed_scenarios = [r for r in self.test_results if r['score'] < 0.7]
        failed_scenarios.sort(key=lambda x: x['score'])
        
        for result in failed_scenarios[:3]:  # Show top 3 worst
            print(f"  - {result['scenario']}: {result['score']:.1%}")
    
    def suggest_fixes(self):
        """Suggest fixes based on test results."""
        print("\n🔧 SUGGESTED FIXES:")
        
        # Analyze common failure patterns
        all_failures = {}
        for result in self.test_results:
            if result['score'] < 0.7 and 'quality_checks' in result:
                for check, passed in result['quality_checks'].items():
                    if not passed:
                        if check not in all_failures:
                            all_failures[check] = []
                        all_failures[check].append(result['scenario'])
        
        if 'Actionable' in all_failures:
            print("1. Make responses more actionable:")
            print("   - Add more 'how to' instructions")
            print("   - Include specific steps or examples")
            print("   - Use action verbs (try, use, can, will)")
        
        if 'Contains Template' in all_failures:
            print("2. Improve template generation:")
            print("   - Always provide actual text templates")
            print("   - Use quotation marks for template text")
            print("   - Include placeholder fields [Name], [Date], etc.")
        
        if 'Substantial Length' in all_failures:
            print("3. Increase response depth:")
            print("   - Provide more comprehensive answers")
            print("   - Add examples and explanations")
            print("   - Include additional helpful information")
        
        if 'Context Aware' in all_failures:
            print("4. Improve context awareness:")
            print("   - Reference previous conversation more explicitly")
            print("   - Build on previous responses")
            print("   - Use phrases like 'as we discussed' or 'building on that'")

def main():
    """Run comprehensive scenario testing."""
    tester = ScenarioTester()
    tester.run_all_scenarios()
    tester.suggest_fixes()

if __name__ == "__main__":
    main()