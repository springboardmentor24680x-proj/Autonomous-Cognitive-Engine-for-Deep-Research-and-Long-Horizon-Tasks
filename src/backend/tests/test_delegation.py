import requests
import json
import time
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class TestCase:
    """Test case structure"""
    name: str
    message: str
    expected_agent: str
    expected_outcomes: List[str]
    requires_context: bool = False


@dataclass
class TestResult:
    """Test result structure"""
    test_name: str
    success: bool
    agent_used: str
    result_integrated: bool
    context_passed: bool
    execution_time: float
    error_message: str = ""


class DelegationTester:
    """Test harness for sub-agent delegation"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = f"test-{int(time.time())}"
        self.results: List[TestResult] = []
    
    def run_test(self, test_case: TestCase) -> TestResult:
        """Run a single test case"""
        print(f"\n{'='*60}")
        print(f"Testing: {test_case.name}")
        print(f"Message: {test_case.message}")
        print(f"Expected Agent: {test_case.expected_agent}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Send request
            response = requests.post(
                f"{self.base_url}/chat",
                json={
                    "session_id": self.session_id,
                    "message": test_case.message
                },
                timeout=30
            )
            
            execution_time = time.time() - start_time
            
            if response.status_code != 200:
                return TestResult(
                    test_name=test_case.name,
                    success=False,
                    agent_used="none",
                    result_integrated=False,
                    context_passed=False,
                    execution_time=execution_time,
                    error_message=f"HTTP {response.status_code}"
                )
            
            data = response.json()
            response_text = data.get("response", "").lower()
            
            # Check if expected agent was mentioned
            agent_used = test_case.expected_agent in response_text
            
            # Check if result was integrated (response contains meaningful content)
            result_integrated = len(response_text) > 50 and any(
                outcome.lower() in response_text 
                for outcome in test_case.expected_outcomes
            )
            
            # For context-requiring tests, check if context was used
            context_passed = True
            if test_case.requires_context:
                # Check if response mentions tasks/calendar (indicating context was used)
                context_passed = any(
                    word in response_text 
                    for word in ["task", "todo", "calendar", "pending", "completed"]
                )
            
            success = agent_used and result_integrated and context_passed
            
            result = TestResult(
                test_name=test_case.name,
                success=success,
                agent_used=test_case.expected_agent if agent_used else "unknown",
                result_integrated=result_integrated,
                context_passed=context_passed,
                execution_time=execution_time
            )
            
            # Print result
            print(f" SUCCESS" if success else "FAILED")
            print(f"Agent Used: {'✓' if agent_used else '✗'} {test_case.expected_agent}")
            print(f"Result Integrated: {'✓' if result_integrated else '✗'}")
            print(f"Context Passed: {'✓' if context_passed else '✗'}")
            print(f"Execution Time: {execution_time:.2f}s")
            
            if not success:
                print(f"\nResponse Preview:")
                print(response_text[:200])
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"EXCEPTION: {str(e)}")
            
            return TestResult(
                test_name=test_case.name,
                success=False,
                agent_used="error",
                result_integrated=False,
                context_passed=False,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def setup_test_data(self):
        """Create some test data in the session"""
        print("\n Setting up test data...")
        
        # Create test tasks
        requests.post(
            f"{self.base_url}/chat",
            json={
                "session_id": self.session_id,
                "message": "Create 3 tasks: 'Review code' (high priority), 'Update docs' (medium), and 'Team sync' (low)"
            }
        )
        
        # Create calendar event
        requests.post(
            f"{self.base_url}/chat",
            json={
                "session_id": self.session_id,
                "message": "Schedule a meeting tomorrow at 2pm"
            }
        )
        
        print(" Test data created\n")
        time.sleep(1)
    
    def run_all_tests(self):
        """Run complete test suite"""
        
        # Define test cases
        test_cases = [
            # Category 1: Simple Research
            TestCase(
                name="Simple Research Query",
                message="Research the latest developments in AI",
                expected_agent="web_search",
                expected_outcomes=["research", "findings", "information"],
                requires_context=False
            ),
            
            # Category 2: Content Summarization
            TestCase(
                name="Summarization Request",
                message="Summarize my current tasks",
                expected_agent="summarizer",
                expected_outcomes=["key points", "summary", "tasks"],
                requires_context=True
            ),
            
            # Category 3: Deep Analysis
            TestCase(
                name="Analysis with Context",
                message="Analyze my productivity based on my current tasks",
                expected_agent="analyzer",
                expected_outcomes=["analysis", "productivity", "insights"],
                requires_context=True
            ),
            
            # Category 4: Visualization
            TestCase(
                name="Chart Creation",
                message="Show me a chart of my task priorities",
                expected_agent="visualizer",
                expected_outcomes=["chart", "visualization", "created"],
                requires_context=True
            ),
            
            # Category 5: Report Generation
            TestCase(
                name="Report Creation",
                message="Create a report on my tasks and calendar",
                expected_agent="report_generator",
                expected_outcomes=["report", "executive summary", "recommendations"],
                requires_context=True
            ),
            
            # Category 6: Strategic Planning
            TestCase(
                name="Planning Breakdown",
                message="Help me plan a product launch",
                expected_agent="planning",
                expected_outcomes=["plan", "phase", "timeline"],
                requires_context=False
            ),
            
            # Category 7: Multi-Agent Workflow
            TestCase(
                name="Complex Multi-Step",
                message="Research AI trends, analyze them, and create a report",
                expected_agent="web_search",  # First agent in chain
                expected_outcomes=["research", "analysis", "report"],
                requires_context=False
            ),
            
            # Category 8: Visualization from Analysis
            TestCase(
                name="Analysis with Visualization",
                message="Analyze my tasks and create a progress chart",
                expected_agent="analyzer",
                expected_outcomes=["analysis", "chart", "progress"],
                requires_context=True
            ),
        ]
        
        # Setup test environment
        self.setup_test_data()
        
        # Run all tests
        print("\n" + "="*60)
        print("STARTING DELEGATION TEST SUITE")
        print("="*60)
        
        for test_case in test_cases:
            result = self.run_test(test_case)
            self.results.append(result)
            time.sleep(2)  # Avoid rate limiting
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Required: 80%")
        print(f"Status: {'PASS' if success_rate >= 80 else ' FAIL'}")
        
        # Detailed breakdown
        print("\n" + "-"*60)
        print("DETAILED RESULTS")
        print("-"*60)
        
        for result in self.results:
            status = "" if result.success else ""
            print(f"{status} {result.test_name}")
            print(f"   Agent: {result.agent_used}")
            print(f"   Result Integrated: {result.result_integrated}")
            print(f"   Context Passed: {result.context_passed}")
            print(f"   Time: {result.execution_time:.2f}s")
            if result.error_message:
                print(f"   Error: {result.error_message}")
            print()
        
        # Performance metrics
        avg_time = sum(r.execution_time for r in self.results) / total_tests
        print(f"Average Execution Time: {avg_time:.2f}s")
        
        # Categorize results
        agent_results = {}
        for result in self.results:
            agent = result.agent_used
            if agent not in agent_results:
                agent_results[agent] = {"total": 0, "success": 0}
            agent_results[agent]["total"] += 1
            if result.success:
                agent_results[agent]["success"] += 1
        
        print("\n" + "-"*60)
        print("RESULTS BY AGENT")
        print("-"*60)
        for agent, stats in agent_results.items():
            rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"{agent}: {stats['success']}/{stats['total']} ({rate:.1f}%)")
        
        # Save to file
        self.save_report_to_file()
        
        print("\n" + "="*60)
        print("EVALUATION COMPLETE")
        print("="*60)
        
        if success_rate >= 80:
            print(" SUCCESS: Agent meets Week 6 evaluation criteria!")
        else:
            print("  NEEDS IMPROVEMENT: Success rate below 80% threshold")
    
    def save_report_to_file(self):
        """Save detailed report to JSON file"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": self.session_id,
            "summary": {
                "total_tests": len(self.results),
                "successful": sum(1 for r in self.results if r.success),
                "failed": sum(1 for r in self.results if not r.success),
                "success_rate": (sum(1 for r in self.results if r.success) / len(self.results) * 100) if self.results else 0
            },
            "results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "agent_used": r.agent_used,
                    "result_integrated": r.result_integrated,
                    "context_passed": r.context_passed,
                    "execution_time": r.execution_time,
                    "error_message": r.error_message
                }
                for r in self.results
            ]
        }
        
        filename = f"delegation_test_results_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n Detailed report saved to: {filename}")


# =========================================================
# MAIN EXECUTION
# =========================================================

if __name__ == "__main__":
    
    
    tester = DelegationTester(base_url="http://localhost:8000")
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n Tests interrupted by user")
        tester.generate_report()
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()