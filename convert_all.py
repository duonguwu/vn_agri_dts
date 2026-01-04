#!/usr/bin/env python3
"""
All-in-One Document Converter
Tự động convert .doc -> .docx -> .md và PDF -> .md
"""

import subprocess
import sys
import os
import pathlib
import argparse

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_dependencies():
    """Check if required tools are available"""
    print("🔍 Checking dependencies...")
    
    issues = []
    
    # Check Python packages
    try:
        import pymupdf4llm
        print("  ✅ pymupdf4llm")
    except ImportError:
        issues.append("pymupdf4llm (pip install pymupdf4llm)")
    
    try:
        import docx
        print("  ✅ python-docx")
    except ImportError:
        issues.append("python-docx (pip install python-docx)")
    
    # Check LibreOffice (optional, for .doc files)
    success, _, _ = run_command(['libreoffice', '--version'])
    if success:
        print("  ✅ LibreOffice (for .doc conversion)")
    else:
        print("  ⚠️  LibreOffice not found (optional, for .doc files)")
        print("     Install: sudo apt-get install libreoffice")
    
    if issues:
        print("\n❌ Missing dependencies:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    print("✅ All required dependencies are installed!\n")
    return True

def convert_doc_files(base_dir):
    """Convert all .doc files to .docx using LibreOffice"""
    print("\n📝 Step 1: Converting .doc files to .docx...")
    print("=" * 60)
    
    # Check if LibreOffice is available
    success, _, _ = run_command(['libreoffice', '--version'])
    if not success:
        print("⚠️  LibreOffice not available, skipping .doc conversion")
        print("   .doc files will be skipped in the final conversion")
        return
    
    # Find all .doc files
    doc_files = list(pathlib.Path(base_dir).glob("**/*.doc"))
    
    if not doc_files:
        print("ℹ️  No .doc files found")
        return
    
    print(f"Found {len(doc_files)} .doc file(s)")
    
    success_count = 0
    for i, doc_file in enumerate(doc_files, 1):
        print(f"\n[{i}/{len(doc_files)}] {doc_file.name}")
        
        # Check if .docx already exists
        docx_file = doc_file.with_suffix('.docx')
        if docx_file.exists():
            print(f"  ⏭️  .docx already exists, skipping")
            success_count += 1
            continue
        
        # Convert using LibreOffice
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', 'docx',
            '--outdir', str(doc_file.parent),
            str(doc_file)
        ]
        
        success, stdout, stderr = run_command(cmd)
        
        if success and docx_file.exists():
            print(f"  ✅ Converted to {docx_file.name}")
            success_count += 1
        else:
            print(f"  ❌ Failed to convert")
    
    print(f"\n✅ Converted {success_count}/{len(doc_files)} .doc files")

def convert_to_markdown(base_dir, output_dir, skip_existing=True):
    """Convert all documents to markdown"""
    print("\n📄 Step 2: Converting all documents to Markdown...")
    print("=" * 60)
    
    # Build command
    cmd = [
        sys.executable,
        'doc2md_enhanced.py',
        base_dir,
        '--folder',
        '--output-dir', output_dir
    ]
    
    if skip_existing:
        cmd.append('--skip-existing')
    
    # Run conversion
    print(f"Running: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(
        description='All-in-One Document to Markdown Converter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script will:
1. Convert all .doc files to .docx (using LibreOffice)
2. Convert all PDF/DOCX files to Markdown

Examples:
  # Convert current directory
  python convert_all.py
  
  # Convert specific directory
  python convert_all.py --input ./documents
  
  # Custom output directory
  python convert_all.py --output ./markdown_files
  
  # Force reconvert all files
  python convert_all.py --no-skip
        """
    )
    
    parser.add_argument('--input', default='.', 
                       help='Input directory (default: current directory)')
    parser.add_argument('--output', default='./markdown_output',
                       help='Output directory (default: ./markdown_output)')
    parser.add_argument('--no-skip', action='store_true',
                       help='Reconvert files even if they already exist')
    parser.add_argument('--skip-doc-conversion', action='store_true',
                       help='Skip .doc to .docx conversion step')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 ALL-IN-ONE DOCUMENT TO MARKDOWN CONVERTER")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        sys.exit(1)
    
    # Convert .doc files first
    if not args.skip_doc_conversion:
        convert_doc_files(args.input)
    else:
        print("\n⏭️  Skipping .doc conversion (--skip-doc-conversion)")
    
    # Convert all to markdown
    success = convert_to_markdown(
        args.input, 
        args.output, 
        skip_existing=not args.no_skip
    )
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 CONVERSION COMPLETE!")
        print("=" * 60)
        print(f"📂 Output directory: {args.output}")
        print(f"📊 Check conversion.log for details")
    else:
        print("\n❌ Conversion failed, check logs for details")
        sys.exit(1)

if __name__ == "__main__":
    main()
