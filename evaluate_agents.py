#!/usr/bin/env python3
"""
Agent Evaluation Script
Tests each agent with domain-specific tasks and scores response quality.
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.supervisor_agent import SupervisorAgent

# Test cases: (task, expected_agent, quality_keywords)
TEST_CASES = [
    {
        "task": "Write a Python function to reverse a linked list",
        "expected_agent": "CodeAgent",
        "quality_keywords": ["def ", "node", "next", "return"],
        "category": "code"
    },
    {
        "task": "Create a 3-month project plan for launching a mobile app",
        "expected_agent": "PlanningAgent",
        "quality_keywords": ["phase", "week", "milestone", "timeline"],
        "category": "planning"
    },
    {
        "task": "Translate 'Good morning, how are you?' to French",
        "expected_agent": "TranslationAgent",
        "quality_keywords": ["bonjour", "comment", "allez"],
        "category": "translation"
    },
    {
        "task": "Write a blog post about the benefits of remote work",
        "expected_agent": "CreativeAgent",
        "quality_keywords": ["remote", "work", "productivity", "flexibility"],
        "category": "creative"
    },
    {
        "task": "Research current trends in artificial intelligence for 2024",
        "expected_agent": "SearchAgent",
        "quality_keywords": ["ai", "model", "research", "trend"],
        "category": "research"
    },
    {
        "task": "Summarize the key points of multi-agent systems in AI",
        "expected_agent": "SummarizerAgent",
        "quality_keywords": ["agent", "system", "coordination", "task"],
        "category": "summarization"
    }
]

def score_response(response: str, quality_keywords: list) -> float:
    """Score response quality based on keyword presence and length."""
    if not response or len(response.strip()) < 50:
        return 0.0

    response_lower = response.lower()

    # Keyword score (0-0.5)
    matched = sum(1 for kw in quality_keywords if kw.lower() in response_lower)
    keyword_score = (matched / len(quality_keywords)) * 0.5

    # Length score (0-0.3): reward responses between 100-2000 chars
    length = len(response)
    if length < 100:
        length_score = 0.0
    elif length > 2000:
        length_score = 0.3
    else:
        length_score = (length / 2000) * 0.3

    # Structure score (0-0.2): reward markdown formatting
    structure_score = 0.0
    if "##" in response or "**" in response:
        structure_score += 0.1
    if "\n" in response:
        structure_score += 0.1

    return round(keyword_score + length_score + structure_score, 2)

def evaluate():
    """Run evaluation across all test cases."""
    print("=" * 60)
    print("AGENT EVALUATION REPORT")
    print("=" * 60)

    agent = SupervisorAgent()
    results = []
    total_score = 0.0

    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}] Category: {test['category'].upper()}")
        print(f"Task: {test['task'][:70]}...")

        start = time.time()
        result = agent.run_with_context(test["task"], [], f"eval-session-{i}")
        elapsed = round(time.time() - start, 2)

        success = result.get("success", False)
        response = result.get("final_response", "")
        delegated_to = result.get("delegated_to", "None")
        tools_used = result.get("tools_used", 0)

        # Score the response
        quality_score = score_response(response, test["quality_keywords"])

        # Check delegation accuracy
        delegation_correct = test["expected_agent"] in str(delegated_to)

        print(f"  Delegated to  : {delegated_to}")
        print(f"  Expected agent: {test['expected_agent']}")
        delegation_ok = "YES" if delegation_correct else "NO"
        success_ok = "YES" if success else "NO"
        print(f"  Delegation OK : {delegation_ok}")
        print(f"  Quality score : {quality_score:.2f} / 1.00")
        print(f"  Response len  : {len(response)} chars")
        print(f"  Tools used    : {tools_used}")
        print(f"  Time          : {elapsed}s")
        print(f"  Success       : {success_ok}")

        total_score += quality_score
        results.append({
            "category": test["category"],
            "expected_agent": test["expected_agent"],
            "delegated_to": delegated_to,
            "delegation_correct": delegation_correct,
            "quality_score": quality_score,
            "success": success,
            "elapsed": elapsed
        })

    # Summary
    avg_score = round(total_score / len(TEST_CASES), 2)
    delegation_accuracy = sum(1 for r in results if r["delegation_correct"]) / len(results)
    success_rate = sum(1 for r in results if r["success"]) / len(results)

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"  Total tests       : {len(TEST_CASES)}")
    print(f"  Success rate      : {success_rate*100:.0f}%")
    print(f"  Delegation accuracy: {delegation_accuracy*100:.0f}%")
    print(f"  Avg quality score : {avg_score:.2f} / 1.00")
    print(f"  Avg response time : {round(sum(r['elapsed'] for r in results)/len(results), 2)}s")
    print("=" * 60)

    # Per-category breakdown
    print("\nPER-CATEGORY RESULTS:")
    for r in results:
        status = "OK" if r["delegation_correct"] else "MISS"
        print(f"  [{status}] {r['category']:<15} score={r['quality_score']:.2f}  agent={r['delegated_to']}")

    return results

if __name__ == "__main__":
    evaluate()