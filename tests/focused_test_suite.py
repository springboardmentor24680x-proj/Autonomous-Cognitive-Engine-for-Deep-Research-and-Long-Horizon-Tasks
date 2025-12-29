#!/usr/bin/env python3
"""
Focused Test Suite - Key scenarios for PDF report generation
"""

import sys
import os
import json
from datetime import datetime
sys.path.append('src')

from agents.supervisor_agent import SupervisorAgent

def run_focused_tests():
    """Run focused test suite with key scenarios."""
    print("🎯 FOCUSED TEST SUITE - KEY SCENARIOS")
    print("=" * 60)
    
    supervisor = SupervisorAgent()
    
    # Carefully selected representative prompts
    test_prompts = [
        # Planning & Organization (5 tests)
        {"category": "Planning", "subcategory": "Trip Planning", "prompt": "plan a 7-day honeymoon to Japan for $5000"},
        {"category": "Planning", "subcategory": "Event Planning", "prompt": "organize a surprise 50th wedding anniversary party"},
        {"category": "Planning", "subcategory": "Budget Planning", "prompt": "create a monthly budget for a college student with $800 income"},
        
        # Communication & Templates (5 tests)
        {"category": "Communication", "subcategory": "Invitations", "prompt": "write a wedding invitation for a beach ceremony"},
        {"category": "Communication", "subcategory": "Professional", "prompt": "email to negotiate salary increase"},
        {"category": "Communication", "subcategory": "Personal", "prompt": "text to ask someone on a first date"},
        
        # Recipes & Cooking (3 tests)
        {"category": "Recipes", "subcategory": "Specific Dishes", "prompt": "easy pasta recipe for beginners"},
        {"category": "Recipes", "subcategory": "Dietary", "prompt": "vegan chocolate cake recipe"},
        
        # Problem Solving (5 tests)
        {"category": "Problem Solving", "subcategory": "Personal", "prompt": "my roommate is messy and won't clean up"},
        {"category": "Problem Solving", "subcategory": "Technical", "prompt": "my phone battery drains too quickly"},
        {"category": "Problem Solving", "subcategory": "Relationship", "prompt": "friend always cancels plans last minute"},
        
        # Creative Requests (3 tests)
        {"category": "Creative", "subcategory": "Writing", "prompt": "write a funny story about a cat who thinks it's a dog"},
        {"category": "Creative", "subcategory": "Ideas", "prompt": "unique date ideas for winter"},
        
        # Learning & Education (3 tests)
        {"category": "Education", "subcategory": "Study Help", "prompt": "effective study schedule for final exams"},
        {"category": "Education", "subcategory": "Skill Development", "prompt": "learn guitar as a complete beginner"},
        
        # Lifestyle & Home (3 tests)
        {"category": "Lifestyle", "subcategory": "Home", "prompt": "decorate a small apartment on $500 budget"},
        {"category": "Lifestyle", "subcategory": "Health", "prompt": "workout routine for someone who hates gyms"},
        
        # Challenging Edge Cases (8 tests)
        {"category": "Edge Cases", "subcategory": "Vague", "prompt": "help"},
        {"category": "Edge Cases", "subcategory": "Single Word", "prompt": "food"},
        {"category": "Edge Cases", "subcategory": "Contradictory", "prompt": "plan a cheap luxury vacation"},
        {"category": "Edge Cases", "subcategory": "Complex", "prompt": "plan my wedding, create a budget, write vows, and suggest a honeymoon destination all for under $15,000"},
        {"category": "Edge Cases", "subcategory": "Emotional", "prompt": "just got divorced and don't know what to do with my life"},
        {"category": "Edge Cases", "subcategory": "Technical", "prompt": "explain quantum entanglement in simple terms"},
        {"category": "Edge Cases", "subcategory": "Creative", "prompt": "write a haiku about debugging code at 3am"},
        {"category": "Edge Cases", "subcategory": "Impossible", "prompt": "help me travel back in time to fix my mistakes"}
    ]
    
    print(f"Testing {len(test_prompts)} carefully selected prompts...")
    print()
    
    results = []
    start_time = datetime.now()
    
    for i, test in enumerate(test_prompts, 1):
        print(f"[{i}/{len(test_prompts)}] {test['prompt'][:50]}...")
        
        try:
            result = supervisor.run_with_context(test['prompt'], [])
            
            if result['success']:
                response = result['final_response']
                metrics = assess_response_quality(response, test['prompt'])
                
                test_result = {
                    'category': test['category'],
                    'subcategory': test['subcategory'],
                    'prompt': test['prompt'],
                    'response': response,
                    'success': True,
                    'tools_used': result.get('tools_used', 0),
                    'metrics': metrics,
                    'timestamp': datetime.now().isoformat()
                }
                
                status = "✅" if metrics['overall_score'] >= 6 else "⚠️"
                print(f"    {status} {metrics['grade']} ({metrics['overall_score']}/10)")
                
            else:
                test_result = {
                    'category': test['category'],
                    'subcategory': test['subcategory'],
                    'prompt': test['prompt'],
                    'response': None,
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'metrics': {'overall_score': 0, 'grade': 'F'},
                    'timestamp': datetime.now().isoformat()
                }
                print(f"    ❌ F (Error: {result.get('error', 'Unknown')})")
            
            results.append(test_result)
            
        except Exception as e:
            test_result = {
                'category': test['category'],
                'subcategory': test['subcategory'],
                'prompt': test['prompt'],
                'response': None,
                'success': False,
                'error': str(e),
                'metrics': {'overall_score': 0, 'grade': 'F'},
                'timestamp': datetime.now().isoformat()
            }
            results.append(test_result)
            print(f"    ❌ F (Exception: {str(e)[:50]})")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Generate summary statistics
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    success_rate = successful_tests / total_tests * 100
    
    # Grade distribution
    grades = [r['metrics']['grade'] for r in results]
    grade_counts = {grade: grades.count(grade) for grade in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F']}
    
    # Category performance
    category_stats = {}
    for result in results:
        category = result['category']
        if category not in category_stats:
            category_stats[category] = {'total': 0, 'scores': []}
        category_stats[category]['total'] += 1
        category_stats[category]['scores'].append(result['metrics']['overall_score'])
    
    for category in category_stats:
        scores = category_stats[category]['scores']
        category_stats[category]['avg_score'] = sum(scores) / len(scores)
        category_stats[category]['avg_grade'] = get_grade(category_stats[category]['avg_score'])
    
    summary_stats = {
        'total_tests': total_tests,
        'successful_tests': successful_tests,
        'success_rate': success_rate,
        'grade_distribution': grade_counts,
        'category_performance': category_stats,
        'test_duration': duration
    }
    
    # Save results
    report_data = {
        'test_info': {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration
        },
        'summary_stats': summary_stats,
        'detailed_results': results
    }
    
    filename = f"focused_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 FOCUSED TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Average Grade: {get_grade(sum(r['metrics']['overall_score'] for r in results) / len(results))}")
    print(f"Duration: {duration:.1f} seconds")
    print(f"\nGrade Distribution:")
    for grade in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F']:
        count = grade_counts[grade]
        if count > 0:
            print(f"  {grade}: {count} ({count/total_tests*100:.1f}%)")
    
    print(f"\nResults saved to: {filename}")
    
    return filename

def assess_response_quality(response, prompt):
    """Assess response quality with detailed metrics."""
    metrics = {}
    
    # Length and substance
    metrics['length'] = len(response)
    metrics['substantial'] = len(response) > 200
    
    # Actionable content
    actionable_keywords = ['try', 'can', 'should', 'will', 'step', 'tip', 'advice', 'suggest', 'recommend', 'here\'s', 'template', 'example']
    metrics['actionable_count'] = sum(1 for word in actionable_keywords if word in response.lower())
    metrics['actionable'] = metrics['actionable_count'] > 0
    
    # Question density (lower is better)
    metrics['question_count'] = response.count('?')
    metrics['not_question_heavy'] = metrics['question_count'] <= 2
    
    # Specific content indicators
    specific_indicators = ['specific', 'example', 'step', 'detail', '$', '%', 'recipe', 'template', 'email', 'message']
    metrics['specific_count'] = sum(1 for word in specific_indicators if word in response.lower())
    metrics['specific'] = metrics['specific_count'] > 0
    
    # Helpful tone
    helpful_indicators = ['help', 'support', 'understand', 'sorry', 'here', 'let me', 'i can', 'happy to', 'glad to']
    metrics['helpful_count'] = sum(1 for phrase in helpful_indicators if phrase in response.lower())
    metrics['helpful_tone'] = metrics['helpful_count'] > 0
    
    # Template/example content
    metrics['has_template'] = any(indicator in response for indicator in ['"', 'template:', 'example:', 'sample:'])
    
    # Calculate overall score (0-10)
    score_components = [
        2 if metrics['substantial'] else 1,  # Length (2 points)
        2 if metrics['actionable_count'] >= 3 else 1 if metrics['actionable'] else 0,  # Actionable (2 points)
        2 if metrics['not_question_heavy'] else 0,  # Not question heavy (2 points)
        2 if metrics['specific_count'] >= 2 else 1 if metrics['specific'] else 0,  # Specific (2 points)
        2 if metrics['helpful_tone'] else 0  # Helpful tone (2 points)
    ]
    
    metrics['overall_score'] = sum(score_components)
    metrics['grade'] = get_grade(metrics['overall_score'])
    
    return metrics

def get_grade(score):
    """Convert numeric score to letter grade."""
    if score >= 9: return 'A+'
    elif score >= 8: return 'A'
    elif score >= 7: return 'B+'
    elif score >= 6: return 'B'
    elif score >= 5: return 'C+'
    elif score >= 4: return 'C'
    elif score >= 3: return 'D'
    else: return 'F'

if __name__ == "__main__":
    json_filename = run_focused_tests()
    
    print(f"\n🎯 To generate PDF report:")
    print(f"python generate_pdf_report.py {json_filename}")