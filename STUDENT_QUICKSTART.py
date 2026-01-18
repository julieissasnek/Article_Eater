#!/usr/bin/env python3
"""
Article Eater v20.7.0 - Student Quick Start
===========================================

This script helps students get Article Eater running in under 5 minutes.
No prior knowledge required!
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_step(num, text):
    print(f"\n[Step {num}] {text}")
    print("-" * 70)

def run_command(cmd, error_msg):
    """Run a command and handle errors gracefully"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error: {error_msg}")
            print(f"   {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Failed: {error_msg}")
        print(f"   {e}")
        return False

def main():
    print_header("Article Eater v20.7.0 - Student Quick Start")
    
    print("This script will:")
    print("  1. Install required Python packages")
    print("  2. Test that everything works")
    print("  3. Show you how to run your first extraction")
    print()
    input("Press Enter to continue...")
    
    # Step 1: Check Python version
    print_step(1, "Checking Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ required. Please upgrade Python.")
        sys.exit(1)
    print("✅ Python version OK")
    
    # Step 2: Install dependencies
    print_step(2, "Installing Dependencies")
    print("This may take a few minutes...")
    
    if not run_command(
        f"{sys.executable} -m pip install --quiet --upgrade pip",
        "Could not upgrade pip"
    ):
        print("⚠️  Continuing anyway...")
    
    if run_command(
        f"{sys.executable} -m pip install --quiet -r requirements.txt",
        "Could not install requirements"
    ):
        print("✅ All packages installed")
    else:
        print("⚠️  Some packages may have failed. Continuing...")
    
    # Step 3: Test imports
    print_step(3, "Testing Agent Imports")
    try:
        from src.agents.agent_stubs import Agent_Finder, Agent_Aggregator, Agent_Linker
        print("✅ All agents imported successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("\nTroubleshooting:")
        print("  - Make sure you're in the ae_v20_7_0 directory")
        print("  - Try: pip install jsonschema pyyaml pydantic")
        sys.exit(1)
    
    # Step 4: Test mock provider
    print_step(4, "Testing Mock Provider (No API Key Needed)")
    os.environ['AE_LLM_PROVIDER'] = 'mock'
    
    try:
        result = Agent_Finder("Test paper about architecture", "Test abstract")
        print(f"✅ Agent_Finder works!")
        print(f"   Provider: {result.provider}")
        print(f"   Items extracted: {len(result.items)}")
    except Exception as e:
        print(f"❌ Mock test failed: {e}")
        sys.exit(1)
    
    # Step 5: Configuration instructions
    print_step(5, "Configuration for Real LLM Use")
    print("\nTo use real LLM providers, set these environment variables:")
    print()
    print("For Gemini (Google):")
    print("  export AE_LLM_PROVIDER=gemini")
    print("  export GEMINI_API_KEY=your-key-here")
    print()
    print("For OpenAI:")
    print("  export AE_LLM_PROVIDER=openai")
    print("  export OPENAI_API_KEY=your-key-here")
    print()
    print("For Anthropic (Claude):")
    print("  export AE_LLM_PROVIDER=anthropic")
    print("  export ANTHROPIC_API_KEY=your-key-here")
    
    # Step 6: Example usage
    print_step(6, "Example: Extract Findings from a Paper")
    print()
    print("Create a file 'test_extraction.py' with this code:")
    print()
    print('```python')
    print('from src.agents.agent_stubs import Agent_Finder')
    print()
    print('# Your paper text (or read from file)')
    print('paper_text = """')
    print('Natural light exposure in office environments has been shown')
    print('to reduce cortisol levels by an average of 23% (p < 0.01, d = 0.67).')
    print('"""')
    print()
    print('abstract = "This study examined stress reduction..."')
    print()
    print('# Extract findings')
    print('result = Agent_Finder(paper_text, abstract)')
    print()
    print('# Show results')
    print('for item in result.items:')
    print('    print(f"Finding: {item.finding_text}")')
    print('    print(f"  p-value: {item.statistics.p_value}")')
    print('    print(f"  Effect size: {item.statistics.effect_size}")')
    print('```')
    
    # Success!
    print_header("✅ Setup Complete!")
    print()
    print("You're ready to use Article Eater!")
    print()
    print("Next steps:")
    print("  1. Get an API key from your LLM provider")
    print("  2. Set environment variables (see Step 5)")
    print("  3. Run your first extraction (see Step 6)")
    print()
    print("Documentation:")
    print("  - README.md - Overview")
    print("  - HANDOFF_v20.7.0_BUGFIX.md - Complete guide")
    print("  - docs/ADMIN_POLICY.md - Security settings")
    print()
    print("Need help? Check the docs/ directory!")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
