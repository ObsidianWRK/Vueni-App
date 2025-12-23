#!/usr/bin/env python3
"""
Test suite for skill-check enforcement system.

Tests validate_skill_checks.py detection logic and hook validation.
"""

import sys
import unittest
from pathlib import Path

# Add parent directory to path to import validate_skill_checks
sys.path.insert(0, str(Path(__file__).parent.parent))

from validate_skill_checks import (
    check_skill_mention,
    detect_violations,
    validate_response,
    extract_available_skills,
    SkillCheckViolation,
)


class TestSkillCheckDetection(unittest.TestCase):
    """Test skill check detection logic."""
    
    def test_check_skill_mention_positive(self):
        """Test that skill check patterns are detected."""
        test_cases = [
            "I've read the using-skills skill",
            "openskills read plan-mode",
            "Using frontend-design skill",
            "Skill read: using-skills",
            "Reading: plan-mode",
            "I invoked the debugging skill",
            "checking for relevant skills",
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                self.assertTrue(
                    check_skill_mention(text),
                    f"Should detect skill check in: {text}"
                )
    
    def test_check_skill_mention_negative(self):
        """Test that non-skill-check text is not detected."""
        test_cases = [
            "I'll read the file",
            "Let me check the code",
            "Starting implementation",
            "Reading files now",
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                self.assertFalse(
                    check_skill_mention(text),
                    f"Should NOT detect skill check in: {text}"
                )
    
    def test_detect_violations_with_task_trigger(self):
        """Test violation detection when task trigger exists but no skill check."""
        response = """
        I'll implement the authentication system.
        read_file("auth.js")
        """
        
        violations = detect_violations(response, ["using-skills", "frontend-design"])
        self.assertGreater(len(violations), 0, "Should detect violation")
        self.assertTrue(
            any("task" in v.message.lower() or "tool" in v.message.lower() for v in violations),
            "Violation should mention task or tool"
        )
    
    def test_detect_violations_with_skill_check(self):
        """Test that no violation is detected when skill check exists."""
        response = """
        I've read the using-skills skill and I'm using it.
        Now I'll implement the authentication system.
        Let me start by reading the auth.js file.
        """
        
        violations = detect_violations(response, ["using-skills"])
        # Should have fewer violations or none
        self.assertLessEqual(
            len(violations),
            1,
            "Should have minimal violations when skill check exists"
        )
    
    def test_detect_violations_tool_usage_without_check(self):
        """Test detection of tool usage without skill check."""
        response = """
        read_file("auth.js")
        write("new_file.js", content)
        """
        
        violations = detect_violations(response, ["using-skills"])
        # Should detect violation for tool usage without skill check
        self.assertGreater(len(violations), 0, "Should detect violation")
    
    def test_validate_response_compliant(self):
        """Test validation of compliant response."""
        response = """
        openskills read using-skills
        I've read the using-skills skill.
        Now I'll implement the feature.
        """
        
        is_valid, violations = validate_response(response, ["using-skills"])
        self.assertTrue(is_valid, "Compliant response should be valid")
        self.assertEqual(len(violations), 0, "Should have no violations")
    
    def test_validate_response_non_compliant(self):
        """Test validation of non-compliant response."""
        response = """
        I'll implement the feature.
        read_file("file.js")
        """
        
        is_valid, violations = validate_response(response, ["using-skills"])
        # May have warnings but should not have errors
        errors = [v for v in violations if v.severity == "error"]
        self.assertEqual(len(errors), 0, "Should use warnings, not errors")


class TestViolationExamples(unittest.TestCase):
    """Test real-world violation examples from AGENTS.md."""
    
    def test_example_1_implementing_plan_without_check(self):
        """Test Example 1: Implementing plan without skill check."""
        response = """
        I'll implement the plan now.
        read_file("plan.md")
        Starting implementation...
        """
        
        violations = detect_violations(response, ["using-skills", "plan-mode"])
        self.assertGreater(len(violations), 0, "Should detect violation")
    
    def test_example_2_starting_task_without_check(self):
        """Test Example 2: Starting task without skill check."""
        response = """
        I'll add authentication to the app.
        read_file("auth.js")
        """
        
        violations = detect_violations(response, ["using-skills", "frontend-design"])
        self.assertGreater(len(violations), 0, "Should detect violation")
    
    def test_correct_behavior_with_skill_check(self):
        """Test correct behavior with skill check."""
        response = """
        openskills read using-skills
        openskills read plan-mode
        I've read the using-skills and plan-mode skills.
        Now I'll implement the plan.
        read_file("plan.md")
        """
        
        violations = detect_violations(response, ["using-skills", "plan-mode"])
        # Should have minimal or no violations
        self.assertLessEqual(len(violations), 1, "Should have minimal violations")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def test_empty_response(self):
        """Test empty response."""
        violations = detect_violations("", [])
        self.assertEqual(len(violations), 0, "Empty response should have no violations")
    
    def test_response_with_only_skill_check(self):
        """Test response that only mentions skill check."""
        response = "openskills read using-skills"
        violations = detect_violations(response, ["using-skills"])
        self.assertEqual(len(violations), 0, "Should have no violations")
    
    def test_response_with_multiple_skill_checks(self):
        """Test response with multiple skill checks."""
        response = """
        openskills read using-skills
        openskills read plan-mode
        openskills read frontend-design
        I've read all relevant skills.
        Now implementing...
        """
        
        violations = detect_violations(response, ["using-skills", "plan-mode", "frontend-design"])
        self.assertEqual(len(violations), 0, "Should have no violations")


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSkillCheckDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestViolationExamples))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
