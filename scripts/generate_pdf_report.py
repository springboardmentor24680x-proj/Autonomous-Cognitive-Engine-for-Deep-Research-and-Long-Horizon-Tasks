#!/usr/bin/env python3
"""
PDF Report Generator - Convert test results to professional PDF
"""

import json
import sys
from datetime import datetime

def generate_html_report(json_filename):
    """Generate HTML report from JSON results."""
    
    # Read JSON data
    with open(json_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    summary = data['summary_stats']
    results = data['detailed_results']
    
    # Calculate additional stats
    avg_score = sum(r['metrics']['overall_score'] for r in results) / len(results)
    avg_grade = get_grade(avg_score)
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous Cognitive Engine - Test Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #007bff;
            margin: 0;
            font-size: 2.5em;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 1.2em;
            margin-top: 10px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 2em;
        }}
        .summary-card p {{
            margin: 0;
            opacity: 0.9;
        }}
        .section {{
            margin: 40px 0;
        }}
        .section h2 {{
            color: #007bff;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #007bff;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        .grade-A-plus, .grade-A {{ background-color: #d4edda !important; color: #155724; }}
        .grade-B-plus, .grade-B {{ background-color: #d1ecf1 !important; color: #0c5460; }}
        .grade-C-plus, .grade-C {{ background-color: #fff3cd !important; color: #856404; }}
        .grade-D, .grade-F {{ background-color: #f8d7da !important; color: #721c24; }}
        .test-result {{
            margin: 20px 0;
            padding: 15px;
            border-left: 4px solid #007bff;
            background: #f8f9fa;
        }}
        .test-result h4 {{
            margin: 0 0 10px 0;
            color: #007bff;
        }}
        .test-result .prompt {{
            font-style: italic;
            color: #666;
            margin: 5px 0;
        }}
        .test-result .response {{
            background: white;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            border: 1px solid #ddd;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 10px 0;
        }}
        .metric {{
            background: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            border: 1px solid #ddd;
        }}
        .metric .value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #007bff;
        }}
        .metric .label {{
            font-size: 0.9em;
            color: #666;
        }}
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
        }}
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Autonomous Cognitive Engine</h1>
            <div class="subtitle">Comprehensive Test Report</div>
            <p><strong>Test Date:</strong> {data['test_info']['start_time'][:19].replace('T', ' ')}</p>
            <p><strong>Duration:</strong> {summary['test_duration']:.1f} seconds</p>
        </div>

        <div class="summary-grid">
            <div class="summary-card">
                <h3>{summary['total_tests']}</h3>
                <p>Total Tests</p>
            </div>
            <div class="summary-card">
                <h3>{summary['success_rate']:.1f}%</h3>
                <p>Success Rate</p>
            </div>
            <div class="summary-card">
                <h3>{avg_grade}</h3>
                <p>Average Grade</p>
            </div>
            <div class="summary-card">
                <h3>{summary['successful_tests']}</h3>
                <p>Tests Passed</p>
            </div>
        </div>

        <div class="section">
            <h2>📊 Grade Distribution</h2>
            <table>
                <thead>
                    <tr>
                        <th>Grade</th>
                        <th>Count</th>
                        <th>Percentage</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    grade_descriptions = {
        'A+': 'Exceptional - Perfect response quality',
        'A': 'Excellent - High quality, comprehensive',
        'B+': 'Very Good - Above average performance',
        'B': 'Good - Solid, helpful responses',
        'C+': 'Satisfactory - Adequate but could improve',
        'C': 'Average - Basic functionality',
        'D': 'Below Average - Significant issues',
        'F': 'Failing - Major problems or errors'
    }
    
    for grade in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F']:
        count = summary['grade_distribution'][grade]
        percentage = count / summary['total_tests'] * 100
        grade_class = f"grade-{grade.replace('+', '-plus')}"
        html_content += f"""
                    <tr class="{grade_class}">
                        <td><strong>{grade}</strong></td>
                        <td>{count}</td>
                        <td>{percentage:.1f}%</td>
                        <td>{grade_descriptions[grade]}</td>
                    </tr>"""
    
    html_content += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>📂 Category Performance</h2>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Average Score</th>
                        <th>Grade</th>
                        <th>Tests</th>
                        <th>Performance</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for category, stats in summary['category_performance'].items():
        grade_class = f"grade-{stats['avg_grade'].replace('+', '-plus')}"
        performance = "Excellent" if stats['avg_score'] >= 8 else "Good" if stats['avg_score'] >= 6 else "Needs Improvement"
        html_content += f"""
                    <tr class="{grade_class}">
                        <td><strong>{category}</strong></td>
                        <td>{stats['avg_score']:.1f}/10</td>
                        <td>{stats['avg_grade']}</td>
                        <td>{stats['total']}</td>
                        <td>{performance}</td>
                    </tr>"""
    
    html_content += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>🏆 Top Performing Tests</h2>
"""
    
    # Show top 10 results
    top_results = sorted([r for r in results if r['success']], 
                        key=lambda x: x['metrics']['overall_score'], reverse=True)[:10]
    
    for i, result in enumerate(top_results, 1):
        grade_class = f"grade-{result['metrics']['grade'].replace('+', '-plus')}"
        html_content += f"""
            <div class="test-result {grade_class}">
                <h4>#{i} - {result['metrics']['grade']} Grade - {result['category']} > {result['subcategory']}</h4>
                <div class="prompt"><strong>Prompt:</strong> {result['prompt']}</div>
                <div class="metrics">
                    <div class="metric">
                        <div class="value">{result['metrics']['overall_score']}/10</div>
                        <div class="label">Score</div>
                    </div>
                    <div class="metric">
                        <div class="value">{result['metrics']['length']}</div>
                        <div class="label">Length</div>
                    </div>
                    <div class="metric">
                        <div class="value">{result['metrics']['actionable_count']}</div>
                        <div class="label">Actionable</div>
                    </div>
                    <div class="metric">
                        <div class="value">{result.get('tools_used', 0)}</div>
                        <div class="label">Tools Used</div>
                    </div>
                </div>
                <div class="response">
                    <strong>Response Preview:</strong><br>
                    {result['response'][:300]}{'...' if len(result['response']) > 300 else ''}
                </div>
            </div>"""
    
    # Show any failing tests
    failing_results = [r for r in results if not r['success'] or r['metrics']['grade'] in ['D', 'F']]
    
    if failing_results:
        html_content += """
        </div>

        <div class="section">
            <h2>⚠️ Areas for Improvement</h2>
"""
        for result in failing_results:
            html_content += f"""
            <div class="test-result grade-F">
                <h4>{result['metrics']['grade']} Grade - {result['category']} > {result['subcategory']}</h4>
                <div class="prompt"><strong>Prompt:</strong> {result['prompt']}</div>
                <div class="response">
                    <strong>Issue:</strong> {result.get('error', 'Low quality response')}<br>
                    {f"<strong>Response:</strong> {result['response'][:200]}..." if result.get('response') else ''}
                </div>
            </div>"""
    
    html_content += f"""
        </div>

        <div class="section">
            <h2>🔍 Detailed Metrics</h2>
            <div class="metrics">
                <div class="metric">
                    <div class="value">{sum(r['metrics'].get('length', 0) for r in results if r['success']) / summary['successful_tests']:.0f}</div>
                    <div class="label">Avg Response Length</div>
                </div>
                <div class="metric">
                    <div class="value">{sum(1 for r in results if r['success'] and r['metrics'].get('actionable', False)) / summary['successful_tests'] * 100:.1f}%</div>
                    <div class="label">Actionable Content</div>
                </div>
                <div class="metric">
                    <div class="value">{sum(1 for r in results if r['success'] and r['metrics'].get('has_template', False)) / summary['successful_tests'] * 100:.1f}%</div>
                    <div class="label">Template Content</div>
                </div>
                <div class="metric">
                    <div class="value">{sum(r.get('tools_used', 0) for r in results) / summary['successful_tests']:.1f}</div>
                    <div class="label">Avg Tools Used</div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p><strong>Autonomous Cognitive Engine Test Report</strong></p>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>🤖 Multi-agent workflow automation system with specialized sub-agents</p>
        </div>
    </div>
</body>
</html>"""
    
    # Save HTML file
    html_filename = json_filename.replace('.json', '.html')
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📄 HTML report generated: {html_filename}")
    print(f"🌐 Open in browser to view, then use browser's 'Print to PDF' feature")
    
    return html_filename

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

def main():
    """Generate PDF report from JSON results."""
    if len(sys.argv) != 2:
        print("Usage: python generate_pdf_report.py <json_filename>")
        print("First run: python comprehensive_prompt_test.py")
        return
    
    json_filename = sys.argv[1]
    
    if not json_filename.endswith('.json'):
        print("Error: Please provide a JSON file")
        return
    
    try:
        html_filename = generate_html_report(json_filename)
        print(f"\n✅ Report generation complete!")
        print(f"📄 HTML file: {html_filename}")
        print(f"\n📋 To create PDF:")
        print(f"1. Open {html_filename} in your web browser")
        print(f"2. Press Ctrl+P (or Cmd+P on Mac)")
        print(f"3. Select 'Save as PDF' as destination")
        print(f"4. Choose 'More settings' and enable 'Background graphics'")
        print(f"5. Click 'Save'")
        
    except FileNotFoundError:
        print(f"Error: File {json_filename} not found")
        print("Please run 'python comprehensive_prompt_test.py' first")
    except Exception as e:
        print(f"Error generating report: {e}")

if __name__ == "__main__":
    main()