#!/usr/bin/env python3
"""
All-in-One Document Converter (Multi-worker Version)
Tự động convert .doc -> .docx -> .md và PDF -> .md với hiệu năng cao.
"""

import subprocess
import sys
import os
import pathlib
import argparse
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
import tempfile
import shutil

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
    
    # Check LibreOffice
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

def _worker_convert_doc(doc_info):
    """Worker function to convert a single .doc to .docx using LibreOffice"""
    doc_file, docx_file = doc_info
    
    if docx_file.exists():
        return True, doc_file.name, "skipped"
    
    # Each worker needs a separate user profile to run LibreOffice in parallel
    temp_profile = tempfile.mkdtemp()
    try:
        cmd = [
            'libreoffice',
            '--headless',
            f'-env:UserInstallation=file://{temp_profile}',
            '--convert-to', 'docx',
            '--outdir', str(doc_file.parent),
            str(doc_file)
        ]
        
        success, _, _ = run_command(cmd)
        status = "success" if (success and docx_file.exists()) else "failed"
        return success, doc_file.name, status
    finally:
        shutil.rmtree(temp_profile, ignore_errors=True)

def convert_doc_files(base_dir, max_workers=None):
    """Convert all .doc files to .docx in parallel"""
    print("\n📝 Step 1: Converting .doc files to .docx (Parallel)...")
    print("=" * 60)
    
    # Find all .doc files
    doc_files = list(pathlib.Path(base_dir).glob("**/*.doc"))
    if not doc_files:
        print("ℹ️  No .doc files found")
        return
    
    # Skip those that already have .docx
    to_convert = []
    for f in doc_files:
        docx = f.with_suffix('.docx')
        to_convert.append((f, docx))
        
    print(f"Found {len(doc_files)} .doc file(s). Using {max_workers} workers.")
    
    success_count = 0
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_worker_convert_doc, info): info for info in to_convert}
        
        for i, future in enumerate(as_completed(futures), 1):
            success, name, status = future.result()
            print(f"[{i}/{len(doc_files)}] {status.upper()}: {name}")
            if success:
                success_count += 1
                
    print(f"\n✅ Finished .doc conversion: {success_count}/{len(doc_files)} success")

def convert_to_markdown(base_dir, output_dir, skip_existing=True, max_workers=None):
    """Convert all documents to markdown using the enhanced script"""
    print("\n📄 Step 2: Converting all documents to Markdown (Parallel)...")
    print("=" * 60)
    
    # Build command
    cmd = [
        sys.executable,
        'doc2md_enhanced.py',
        base_dir,
        '--folder',
        '--output-dir', output_dir,
        '--workers', str(max_workers)
    ]
    
    if skip_existing:
        cmd.append('--skip-existing')
    
    # Run conversion
    print(f"Running: {' '.join(cmd)}\n")
    
    # We call the external script because it handles its own pool
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(
        description='Parallel All-in-One Document to Markdown Converter',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--input', default='./Report', 
                       help='Input directory (default: ./Report)')
    parser.add_argument('--output', default='./markdown_output',
                       help='Output directory (default: ./markdown_output)')
    parser.add_argument('--no-skip', action='store_true',
                       help='Reconvert files even if they already exist')
    parser.add_argument('--skip-doc-conversion', action='store_true',
                       help='Skip .doc to .docx conversion step')
    parser.add_argument('-w', '--workers', type=int, default=multiprocessing.cpu_count(),
                       help='Number of parallel workers (default: CPU count)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 PARALLEL DOCUMENT TO MARKDOWN CONVERTER")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Convert .doc files first
    if not args.skip_doc_conversion:
        convert_doc_files(args.input, max_workers=args.workers)
    
    # Convert all to markdown
    success = convert_to_markdown(
        args.input, 
        args.output, 
        skip_existing=not args.no_skip,
        max_workers=args.workers
    )
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 ALL TASKS COMPLETE!")
        print("=" * 60)
    else:
        print("\n❌ Conversion failed, check logs for details")
        sys.exit(1)

if __name__ == "__main__":
    main()
