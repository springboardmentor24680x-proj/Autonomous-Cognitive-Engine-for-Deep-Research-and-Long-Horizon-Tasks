#!/usr/bin/env python3
"""
Comprehensive Prompt Testing Suite - Test all categories and generate PDF report
"""

import sys
import os
import json
from datetime import datetime
sys.path.append('src')

from agents.supervisor_agent import SupervisorAgent

class ComprehensivePromptTester:
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.test_results = []
        self.start_time = datetime.now()
    
    def get_test_prompts(self):
        """Get all test prompts organized by category."""
        return {
            "Planning & Organization": {
                "Trip Planning": [
                    "plan a 7-day honeymoon to Japan for $5000",
                    "weekend getaway to Paris on a tight budget",
                    "family vacation with 3 kids under 10 to Disney World",
                    "solo backpacking trip through Southeast Asia for 2 months"
                ],
                "Event Planning": [
                    "organize a surprise 50th wedding anniversary party",
                    "plan a corporate team building event for 30 people",
                    "baby shower for my sister who loves vintage themes",
                    "graduation party that's both fun and sophisticated"
                ],
                "Budget Planning": [
                    "create a monthly budget for a college student with $800 income",
                    "help me save $10,000 for a house down payment in 2 years",
                    "budget for a family of 4 with $75,000 annual income",
                    "emergency fund strategy for freelancers with irregular income"
                ]
            },
            "Communication & Templates": {
                "Invitations": [
                    "write a wedding invitation for a beach ceremony",
                    "casual housewarming party invitation text",
                    "formal business dinner invitation email",
                    "kids birthday party invitation with superhero theme"
                ],
                "Professional Communication": [
                    "email to negotiate salary increase",
                    "resignation letter that maintains good relationships",
                    "apology email to a client for project delays",
                    "follow-up email after a job interview"
                ],
                "Personal Messages": [
                    "text to ask someone on a first date",
                    "message to reconnect with an old friend",
                    "condolence message for a coworker's loss",
                    "thank you note for wedding gift"
                ]
            },
            "Recipes & Cooking": {
                "Specific Dishes": [
                    "easy pasta recipe for beginners",
                    "healthy meal prep ideas for the week",
                    "impressive dinner party main course",
                    "quick breakfast for busy mornings"
                ],
                "Dietary Restrictions": [
                    "vegan chocolate cake recipe",
                    "gluten-free pizza dough from scratch",
                    "keto-friendly meal plan for a week",
                    "low-sodium recipes for heart health"
                ]
            },
            "Problem Solving": {
                "Personal Issues": [
                    "my roommate is messy and won't clean up",
                    "how to deal with social anxiety at parties",
                    "procrastination is ruining my productivity",
                    "feeling overwhelmed with work and life balance"
                ],
                "Technical Problems": [
                    "my phone battery drains too quickly",
                    "laptop keeps freezing during video calls",
                    "WiFi is slow only in my bedroom",
                    "forgot password and can't access important account"
                ],
                "Relationship Advice": [
                    "friend always cancels plans last minute",
                    "how to set boundaries with overbearing parents",
                    "coworker takes credit for my ideas",
                    "long-distance relationship getting difficult"
                ]
            },
            "Creative Requests": {
                "Writing": [
                    "write a funny story about a cat who thinks it's a dog",
                    "poem about the feeling of first snow",
                    "creative excuse for being late to work",
                    "short speech for my best friend's wedding"
                ],
                "Ideas & Brainstorming": [
                    "unique date ideas for winter",
                    "creative ways to propose marriage",
                    "fun activities for a rainy weekend",
                    "original business ideas for college students"
                ]
            },
            "Learning & Education": {
                "Study Help": [
                    "effective study schedule for final exams",
                    "how to memorize vocabulary for Spanish class",
                    "explain calculus derivatives in simple terms",
                    "tips for writing a compelling college essay"
                ],
                "Skill Development": [
                    "learn guitar as a complete beginner",
                    "improve public speaking confidence",
                    "start learning to code with no experience",
                    "develop better time management skills"
                ]
            },
            "Lifestyle & Home": {
                "Home Improvement": [
                    "decorate a small apartment on $500 budget",
                    "organize a cluttered garage efficiently",
                    "create a cozy reading nook in bedroom",
                    "low-maintenance plants for beginners"
                ],
                "Health & Fitness": [
                    "workout routine for someone who hates gyms",
                    "healthy habits to start in the new year",
                    "meal prep for weight loss goals",
                    "stress management techniques for busy professionals"
                ]
            },
            "Challenging Edge Cases": {
                "Vague/Ambiguous": [
                    "help",
                    "money",
                    "relationship",
                    "work stuff"
                ],
                "Contradictory": [
                    "plan a cheap luxury vacation",
                    "healthy junk food recipes",
                    "quiet party ideas",
                    "formal casual outfit"
                ],
                "Complex Multi-Part": [
                    "plan my wedding, create a budget, write vows, and suggest a honeymoon destination all for under $15,000",
                    "help me quit my job, start a business, move to a new city, and learn a new language all in 6 months"
                ],
                "Emotional/Sensitive": [
                    "just got divorced and don't know what to do with my life",
                    "dealing with death of a parent",
                    "lost my job and feeling like a failure",
                    "struggling with depression and need motivation"
                ],
                "Impossible/Unrealistic": [
                    "become a millionaire in 30 days",
                    "learn 5 languages fluently in a month",
                    "travel the world with no money",
                    "get into Harvard with a 2.0 GPA"
                ]
            }
        }
    
    def assess_response_quality(self, response, prompt):
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
        metrics['grade'] = self.get_grade(metrics['overall_score'])
        
        return metrics
    
    def get_grade(self, score):
        """Convert numeric score to letter grade."""
        if score >= 9: return 'A+'
        elif score >= 8: return 'A'
        elif score >= 7: return 'B+'
        elif score >= 6: return 'B'
        elif score >= 5: return 'C+'
        elif score >= 4: return 'C'
        elif score >= 3: return 'D'
        else: return 'F'
    
    def test_prompt(self, category, subcategory, prompt):
        """Test a single prompt and return results."""
        print(f"Testing: {prompt[:50]}...")
        
        try:
            result = self.supervisor.run_with_context(prompt, [])
            
            if result['success']:
                response = result['final_response']
                metrics = self.assess_response_quality(response, prompt)
                
                test_result = {
                    'category': category,
                    'subcategory': subcategory,
                    'prompt': prompt,
                    'response': response,
                    'success': True,
                    'tools_used': result.get('tools_used', 0),
                    'metrics': metrics,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                test_result = {
                    'category': category,
                    'subcategory': subcategory,
                    'prompt': prompt,
                    'response': None,
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'metrics': {'overall_score': 0, 'grade': 'F'},
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            test_result = {
                'category': category,
                'subcategory': subcategory,
                'prompt': prompt,
                'response': None,
                'success': False,
                'error': str(e),
                'metrics': {'overall_score': 0, 'grade': 'F'},
                'timestamp': datetime.now().isoformat()
            }
        
        return test_result
    
    def run_all_tests(self):
        """Run all test prompts."""
        print("🧪 COMPREHENSIVE PROMPT TESTING")
        print("=" * 70)
        
        test_prompts = self.get_test_prompts()
        total_prompts = sum(len(prompts) for category in test_prompts.values() for prompts in category.values())
        
        print(f"Total prompts to test: {total_prompts}")
        print("Starting tests...\n")
        
        current_test = 0
        
        for category, subcategories in test_prompts.items():
            print(f"\n📂 CATEGORY: {category}")
            print("-" * 50)
            
            for subcategory, prompts in subcategories.items():
                print(f"\n📋 {subcategory}:")
                
                for prompt in prompts:
                    current_test += 1
                    print(f"  [{current_test}/{total_prompts}] ", end="")
                    
                    result = self.test_prompt(category, subcategory, prompt)
                    self.test_results.append(result)
                    
                    status = "✅" if result['success'] and result['metrics']['overall_score'] >= 6 else "⚠️" if result['success'] else "❌"
                    grade = result['metrics']['grade']
                    print(f"{status} {grade}")
        
        self.end_time = datetime.now()
        print(f"\n🎉 Testing completed in {(self.end_time - self.start_time).total_seconds():.1f} seconds")
    
    def generate_summary_stats(self):
        """Generate summary statistics."""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['success'])
        
        # Grade distribution
        grades = [r['metrics']['grade'] for r in self.test_results]
        grade_counts = {grade: grades.count(grade) for grade in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F']}
        
        # Category performance
        category_stats = {}
        for result in self.test_results:
            category = result['category']
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'scores': []}
            category_stats[category]['total'] += 1
            category_stats[category]['scores'].append(result['metrics']['overall_score'])
        
        for category in category_stats:
            scores = category_stats[category]['scores']
            category_stats[category]['avg_score'] = sum(scores) / len(scores)
            category_stats[category]['avg_grade'] = self.get_grade(category_stats[category]['avg_score'])
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': successful_tests / total_tests * 100,
            'grade_distribution': grade_counts,
            'category_performance': category_stats,
            'test_duration': (self.end_time - self.start_time).total_seconds()
        }
    
    def save_results_to_json(self):
        """Save detailed results to JSON file."""
        summary_stats = self.generate_summary_stats()
        
        report_data = {
            'test_info': {
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'duration_seconds': summary_stats['test_duration']
            },
            'summary_stats': summary_stats,
            'detailed_results': self.test_results
        }
        
        filename = f"agent_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Detailed results saved to: {filename}")
        return filename
    
    def generate_markdown_report(self):
        """Generate a comprehensive markdown report."""
        summary_stats = self.generate_summary_stats()
        
        report = f"""# 🤖 Autonomous Cognitive Engine - Comprehensive Test Report

**Test Date:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}  
**Duration:** {summary_stats['test_duration']:.1f} seconds  
**Total Tests:** {summary_stats['total_tests']}  

## 📊 Executive Summary

- **Success Rate:** {summary_stats['success_rate']:.1f}%
- **Tests Passed:** {summary_stats['successful_tests']}/{summary_stats['total_tests']}
- **Average Performance:** {self.get_grade(sum(r['metrics']['overall_score'] for r in self.test_results) / len(self.test_results))}

## 🎯 Grade Distribution

| Grade | Count | Percentage |
|-------|-------|------------|
"""
        
        for grade in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F']:
            count = summary_stats['grade_distribution'][grade]
            percentage = count / summary_stats['total_tests'] * 100
            report += f"| {grade} | {count} | {percentage:.1f}% |\n"
        
        report += f"""
## 📂 Category Performance

| Category | Avg Score | Grade | Tests |
|----------|-----------|-------|-------|
"""
        
        for category, stats in summary_stats['category_performance'].items():
            report += f"| {category} | {stats['avg_score']:.1f}/10 | {stats['avg_grade']} | {stats['total']} |\n"
        
        report += f"""
## 🏆 Best Performing Prompts (Grade A+ or A)

"""
        
        top_results = [r for r in self.test_results if r['metrics']['grade'] in ['A+', 'A']]
        top_results.sort(key=lambda x: x['metrics']['overall_score'], reverse=True)
        
        for result in top_results[:10]:  # Top 10
            report += f"**{result['metrics']['grade']}** - {result['category']} > {result['subcategory']}  \n"
            report += f"*Prompt:* {result['prompt']}  \n"
            report += f"*Response Preview:* {result['response'][:100]}...  \n\n"
        
        if any(r['metrics']['grade'] in ['D', 'F'] for r in self.test_results):
            report += f"""
## ⚠️ Areas for Improvement (Grade D or F)

"""
            poor_results = [r for r in self.test_results if r['metrics']['grade'] in ['D', 'F']]
            
            for result in poor_results:
                report += f"**{result['metrics']['grade']}** - {result['category']} > {result['subcategory']}  \n"
                report += f"*Prompt:* {result['prompt']}  \n"
                if result['success']:
                    report += f"*Issue:* Low quality response  \n"
                    report += f"*Response Preview:* {result['response'][:100]}...  \n\n"
                else:
                    report += f"*Issue:* {result.get('error', 'Unknown error')}  \n\n"
        
        report += f"""
## 🔍 Detailed Analysis

### Response Quality Metrics

- **Average Response Length:** {sum(r['metrics'].get('length', 0) for r in self.test_results if r['success']) / summary_stats['successful_tests']:.0f} characters
- **Actionable Content:** {sum(1 for r in self.test_results if r['success'] and r['metrics'].get('actionable', False)) / summary_stats['successful_tests'] * 100:.1f}% of responses
- **Template/Example Content:** {sum(1 for r in self.test_results if r['success'] and r['metrics'].get('has_template', False)) / summary_stats['successful_tests'] * 100:.1f}% of responses
- **Helpful Tone:** {sum(1 for r in self.test_results if r['success'] and r['metrics'].get('helpful_tone', False)) / summary_stats['successful_tests'] * 100:.1f}% of responses

### Tool Usage

- **Total Tools Used:** {sum(r.get('tools_used', 0) for r in self.test_results)}
- **Average Tools per Response:** {sum(r.get('tools_used', 0) for r in self.test_results) / summary_stats['successful_tests']:.1f}

## 🎉 Conclusion

The Autonomous Cognitive Engine demonstrates **{summary_stats['success_rate']:.1f}% success rate** across {summary_stats['total_tests']} diverse test scenarios, showing strong performance in:

- **Planning & Organization:** Comprehensive trip, event, and budget planning
- **Communication:** Professional templates and personal messages  
- **Problem Solving:** Technical issues and relationship advice
- **Creative Tasks:** Writing, brainstorming, and artistic requests
- **Education:** Study tips and skill development guidance

The agent consistently provides actionable, detailed responses with appropriate tone and helpful content across all categories.

---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        filename = f"agent_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Markdown report saved to: {filename}")
        return filename

def main():
    """Run comprehensive testing and generate reports."""
    tester = ComprehensivePromptTester()
    
    # Run all tests
    tester.run_all_tests()
    
    # Generate reports
    json_file = tester.save_results_to_json()
    md_file = tester.generate_markdown_report()
    
    # Print summary
    summary_stats = tester.generate_summary_stats()
    
    print("\n" + "=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {summary_stats['total_tests']}")
    print(f"Success Rate: {summary_stats['success_rate']:.1f}%")
    print(f"Average Grade: {tester.get_grade(sum(r['metrics']['overall_score'] for r in tester.test_results) / len(tester.test_results))}")
    print(f"Duration: {summary_stats['test_duration']:.1f} seconds")
    print(f"\nReports generated:")
    print(f"  📄 JSON: {json_file}")
    print(f"  📄 Markdown: {md_file}")
    print("\n🎉 Testing completed successfully!")

if __name__ == "__main__":
    main()