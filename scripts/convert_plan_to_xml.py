#!/usr/bin/env python3
"""
Convert Markdown Plan to XML-Tagged Format

Converts plan files from Markdown header format to XML-tagged format
per the plan-mode skill's prompt engineering best practices.

Features:
- Proper line breaks before/after XML tags
- Preserves table formatting
- Clean section separation

Usage:
    python scripts/convert_plan_to_xml.py <plan-file.md>
    python scripts/convert_plan_to_xml.py <plan-file.md> --in-place
    python scripts/convert_plan_to_xml.py <plan-file.md> -o <output-file.md>
"""

import re
import sys
from pathlib import Path


# Mapping of Markdown headers to XML tags
SECTION_MAPPINGS = {
    "Goal": "goal",
    "Context": "context",
    "Approach": "approach",
    "Steps": "steps",
    "Assumptions": "assumptions",
    "Risks": "risks",
    "Risks & Mitigations": "risks",
    "Implementation Todos": "todos",
    "Test Cases": "test_cases",
    "Verification": "verification",
    "Verification Commands": "verification",
    "Success Criteria": "success_criteria",
    "Expected Results": "expected_results",
}


def convert_plan_to_xml(content: str) -> str:
    """
    Convert a Markdown plan to XML-tagged format.
    
    Transforms:
        ## Goal
        Some content here
        
        ## Context
        More content
    
    Into:
        <goal>
        Some content here
        </goal>
        
        <context>
        More content
        </context>
    """
    lines = content.split('\n')
    result = []
    current_tag = None
    section_content = []
    
    def close_current_section():
        """Close the current XML section with proper formatting."""
        nonlocal current_tag, section_content
        if current_tag and section_content:
            # Remove trailing empty lines from section content
            while section_content and section_content[-1].strip() == '':
                section_content.pop()
            # Remove leading empty lines from section content
            while section_content and section_content[0].strip() == '':
                section_content.pop(0)
            
            # Add content with proper indentation/formatting
            for line in section_content:
                result.append(line)
            
            # Close tag with blank line after
            result.append(f'</{current_tag}>')
            result.append('')
            
            section_content = []
            current_tag = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a section header we should convert
        header_match = re.match(r'^##\s+(.+)$', line)
        
        if header_match:
            header_text = header_match.group(1).strip()
            
            # Close previous section if open
            close_current_section()
            
            # Check if this header maps to an XML tag
            if header_text in SECTION_MAPPINGS:
                current_tag = SECTION_MAPPINGS[header_text]
                # Add opening tag
                result.append(f'<{current_tag}>')
            else:
                # Keep as regular header if not in mapping
                result.append(line)
        elif current_tag:
            # We're inside an XML section
            section_content.append(line)
        else:
            result.append(line)
        
        i += 1
    
    # Close final section if open
    close_current_section()
    
    # Clean up multiple consecutive blank lines
    cleaned = []
    prev_blank = False
    for line in result:
        is_blank = line.strip() == ''
        if is_blank and prev_blank:
            continue  # Skip consecutive blank lines
        cleaned.append(line)
        prev_blank = is_blank
    
    return '\n'.join(cleaned)


def main():
    if len(sys.argv) < 2:
        print("Convert Markdown Plan to XML-Tagged Format")
        print()
        print("Usage:")
        print("  python convert_plan_to_xml.py <plan-file.md>              # Preview")
        print("  python convert_plan_to_xml.py <plan-file.md> --in-place   # Modify in place")
        print("  python convert_plan_to_xml.py <plan-file.md> -o out.md    # Write to file")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    
    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    # Parse options
    in_place = "--in-place" in sys.argv or "-i" in sys.argv
    output_file = None
    
    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        if idx + 1 < len(sys.argv):
            output_file = Path(sys.argv[idx + 1])
    
    # Read and convert
    content = input_file.read_text()
    converted = convert_plan_to_xml(content)
    
    # Output
    if in_place:
        input_file.write_text(converted)
        print(f"✓ Converted {input_file} in place")
    elif output_file:
        output_file.write_text(converted)
        print(f"✓ Wrote converted plan to {output_file}")
    else:
        print(converted)


if __name__ == "__main__":
    main()
