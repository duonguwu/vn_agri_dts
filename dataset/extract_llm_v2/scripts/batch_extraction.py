#!/usr/bin/env python3
"""
Batch Extraction Script
Process multiple months/years in batch
"""

import os
import sys
from pathlib import Path
from llm_extraction import LLMExtractor

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def get_available_months(segment_month_path: Path) -> list:
    """Get list of available month files"""
    available = []
    for file in segment_month_path.glob("*.md"):
        try:
            year_month = file.stem  # e.g., "2009_02"
            year, month = year_month.split("_")
            available.append((int(year), int(month)))
        except ValueError:
            continue
    
    return sorted(available)

def main():
    """Main batch processing function"""
    # Configuration
    API_KEY = input("🔑 Enter your Gemini API key: ").strip()
    if not API_KEY:
        print("❌ API key is required!")
        return
    
    # Initialize extractor
    extractor = LLMExtractor(api_key=API_KEY)
    
    # Get available months
    available_months = get_available_months(extractor.segment_month_path)
    
    if not available_months:
        print("❌ No monthly segment files found!")
        print(f"📁 Check directory: {extractor.segment_month_path}")
        return
    
    print(f"📅 Found {len(available_months)} available months:")
    for i, (year, month) in enumerate(available_months, 1):
        print(f"  {i:2d}. {year}-{month:02d}")
    
    # User selection
    print("\n🎯 Select processing mode:")
    print("1. Process single month")
    print("2. Process all months")
    print("3. Process year range")
    print("4. Process specific months")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        # Single month
        month_num = int(input(f"Enter month number (1-{len(available_months)}): ")) - 1
        if 0 <= month_num < len(available_months):
            year, month = available_months[month_num]
            print(f"🔄 Processing {year}-{month:02d}...")
            
            result = extractor.extract_month(year, month)
            save_result = extractor.save_results(result)
            
            if result["success"]:
                print(f"✅ Success: {result['records_count']} records")
            else:
                print(f"❌ Failed: {result.get('error')}")
        else:
            print("❌ Invalid month number!")
    
    elif choice == "2":
        # All months
        print(f"🔄 Processing all {len(available_months)} months...")
        confirm = input("Continue? (y/N): ").strip().lower()
        
        if confirm == 'y':
            results = extractor.process_multiple_months(available_months)
            
            # Summary
            successful = sum(1 for r in results["results"].values() 
                           if r["extraction"]["success"])
            print(f"\n📊 SUMMARY:")
            print(f"✅ Successful: {successful}/{len(available_months)}")
            print(f"📈 Total records: {results['total_records']}")
        else:
            print("❌ Cancelled")
    
    elif choice == "3":
        # Year range
        start_year = int(input("Enter start year: "))
        end_year = int(input("Enter end year: "))
        
        selected_months = [(y, m) for y, m in available_months 
                          if start_year <= y <= end_year]
        
        if selected_months:
            print(f"🔄 Processing {len(selected_months)} months from {start_year}-{end_year}...")
            results = extractor.process_multiple_months(selected_months)
            
            successful = sum(1 for r in results["results"].values() 
                           if r["extraction"]["success"])
            print(f"\n📊 SUMMARY:")
            print(f"✅ Successful: {successful}/{len(selected_months)}")
            print(f"📈 Total records: {results['total_records']}")
        else:
            print("❌ No months found in specified range!")
    
    elif choice == "4":
        # Specific months
        print("Enter month numbers (comma-separated):")
        month_input = input("Example: 1,3,5: ").strip()
        
        try:
            month_indices = [int(x.strip()) - 1 for x in month_input.split(",")]
            selected_months = [available_months[i] for i in month_indices 
                             if 0 <= i < len(available_months)]
            
            if selected_months:
                print(f"🔄 Processing {len(selected_months)} selected months...")
                results = extractor.process_multiple_months(selected_months)
                
                successful = sum(1 for r in results["results"].values() 
                               if r["extraction"]["success"])
                print(f"\n📊 SUMMARY:")
                print(f"✅ Successful: {successful}/{len(selected_months)}")
                print(f"📈 Total records: {results['total_records']}")
            else:
                print("❌ No valid months selected!")
        except ValueError:
            print("❌ Invalid input format!")
    
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()