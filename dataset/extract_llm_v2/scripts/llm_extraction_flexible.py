#!/usr/bin/env python3
"""
LLM Extraction Script - Flexible Interface
Supports multiple input methods:
1. Single appendix by path
2. Single appendix by year/month/appendix (e.g., 2009 02 PL1)
3. Batch processing by year range
4. Batch processing by specific months
"""

import os
import json
import sys
import re
from google.genai import types
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd

# Gemini API
from google import genai

# Configuration
GEMINI_API_KEY = " "  # Replace with your actual API key
MODEL_NAME = "gemini-2.5-flash"

class FlexibleLLMExtractor:
    def __init__(self, api_key: str):
        """Initialize LLM Extractor with Gemini API"""
        self.client = genai.Client(api_key=api_key)
        self.model_name = MODEL_NAME
        
        # Paths
        self.base_path = Path(__file__).parent.parent
        self.guide_path = self.base_path / "LLM_EXTRACTION_GUIDE.md"
        self.schema_path = self.base_path / "schema_improved_v2.json"
        self.segments_base_path = Path("/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments")
        self.output_path = self.base_path / "extracted_data"
        self.raw_output_path = self.base_path / "raw_responses"
        
        # Create output directories
        self.output_path.mkdir(exist_ok=True)
        self.raw_output_path.mkdir(exist_ok=True)
        
        # Load guide and schema
        self.extraction_guide = self._load_guide()
        self.schema = self._load_schema()
        
        print(f"🚀 Flexible LLM Extractor initialized")
        print(f"📖 Guide loaded: {len(self.extraction_guide)} characters")
        print(f"📋 Schema loaded: {len(self.schema)} fields")
    
    def _load_guide(self) -> str:
        """Load LLM extraction guide"""
        try:
            with open(self.guide_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to load guide: {e}")
    
    def _load_schema(self) -> Dict:
        """Load JSON schema"""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load schema: {e}")
    
    def _create_system_prompt(self) -> str:
        """Create comprehensive system prompt"""
        return f"""You are a Vietnamese Agricultural Data Extraction Expert.

TASK: Extract structured data from Vietnamese agricultural reports (markdown tables) and convert to JSON format.

EXTRACTION GUIDE:
{self.extraction_guide}

JSON SCHEMA:
{json.dumps(self.schema, indent=2, ensure_ascii=False)}

CRITICAL REQUIREMENTS:
1. Follow ALL edge case rules from the guide
2. Output ONLY valid JSON array of records
3. Each record must conform to the schema structure
4. Use sector detection from title (NOT appendix number)
5. Handle multi-period data correctly (separate records per period)
6. Normalize units according to guide (1000_ha, 1000_ton, million_USD)
7. Generate unique record_id (UUID) for each record
8. Set extraction_method="LLM_Extraction"

OUTPUT FORMAT: JSON array only, no markdown formatting, no explanations.

EXAMPLE RECORD STRUCTURE:
{{
  "record_id": "uuid-string",
  "time_context": {{
    "year": 2009,
    "month": 2,
    "report_date": "2009-02-15"
  }},
  "geo_context": {{
    "geo_level": "Provincial",
    "location_name": "An Giang"
  }},
  "item_context": {{
    "sector": "Cultivation",
    "commodity": "Lúa",
    "sub_item": "Đông Xuân"
  }},
  "metric_context": {{
    "attribute": "Area_Planted",
    "value": 234.5,
    "unit": "1000_ha",
    "data_type": "Actual"
  }},
  "metadata": {{
    "source_file": "2009_02_PHULUC_t02_2009_FINAL_PL1.md",
    "appendix_number": "PL1",
    "table_index": 1,
    "extraction_method": "LLM_Extraction"
  }}
}}"""

    def _create_user_prompt(self, appendix_content: str, year: int, month: int, appendix_number: str, source_file: str) -> str:
        """Create user prompt with appendix data"""
        return f"""Extract data from this Vietnamese agricultural appendix for {year}-{month:02d}:

METADATA:
- Year: {year}
- Month: {month}
- Appendix: {appendix_number}
- Source file: {source_file}
- Report date: {year}-{month:02d}-15

MARKDOWN CONTENT:
{appendix_content}

Extract ALL data from this single appendix. Create separate records for each data point according to the schema and guide. Focus on accuracy and completeness."""

    def parse_file_path(self, file_path: str) -> Tuple[int, int, str, str]:
        """Parse file path to extract year, month, appendix number"""
        file_path = Path(file_path)
        filename = file_path.stem
        
        # Pattern: 2009_02_PHULUC_t02_2009_FINAL_PL1
        parts = filename.split('_')
        
        if len(parts) >= 2:
            year = int(parts[0])
            month = int(parts[1])
        else:
            raise ValueError(f"Cannot parse year/month from filename: {filename}")
        
        # Extract appendix number
        appendix_number = "Unknown"
        for part in parts:
            if part.startswith('PL'):
                appendix_number = part
                break
        
        return year, month, appendix_number, file_path.name

    def find_appendix_file(self, year: int, month: int, appendix: str) -> Optional[Path]:
        """Find appendix file by year, month, and appendix number"""
        year_folder = self.segments_base_path / str(year)
        
        if not year_folder.exists():
            print(f"❌ Year folder not found: {year_folder}")
            return None
        
        # Search pattern: {year}_{month:02d}_*_{appendix}.md
        pattern = f"{year}_{month:02d}_*_{appendix}.md"
        matches = list(year_folder.glob(pattern))
        
        if not matches:
            print(f"❌ No file found matching pattern: {pattern}")
            print(f"📁 Available files in {year_folder}:")
            for f in sorted(year_folder.glob("*.md"))[:10]:  # Show first 10
                print(f"   - {f.name}")
            return None
        
        if len(matches) > 1:
            print(f"⚠️  Multiple files found, using first: {matches[0].name}")
        
        return matches[0]

    def extract_single_appendix(self, appendix_file: Path, max_retries: int = 3) -> Dict[str, Any]:
        """Extract data for a specific appendix"""
        print(f"📄 Processing: {appendix_file.name}")
        
        # Load appendix data
        try:
            with open(appendix_file, 'r', encoding='utf-8') as f:
                appendix_content = f.read()
        except Exception as e:
            return {"success": False, "error": f"Failed to read file: {e}"}
        
        print(f"📊 File size: {len(appendix_content)} characters")
        
        # Parse file info
        try:
            year, month, appendix_number, source_file = self.parse_file_path(str(appendix_file))
        except Exception as e:
            return {"success": False, "error": f"Failed to parse file path: {e}"}
        
        # Create prompts
        system_prompt = self._create_system_prompt()
        user_prompt = self._create_user_prompt(appendix_content, year, month, appendix_number, source_file)
        
        # Estimate tokens
        total_chars = len(system_prompt) + len(user_prompt)
        estimated_tokens = total_chars // 4
        print(f"🔢 Estimated tokens: {estimated_tokens:,}")
        
        if estimated_tokens > 1_000_000:
            print("⚠️  Warning: Approaching token limit!")
        
        # Create output directories
        year_month_path = self.output_path / str(year) / f"{month:02d}"
        year_month_path.mkdir(parents=True, exist_ok=True)
        
        raw_year_month_path = self.raw_output_path / str(year) / f"{month:02d}"
        raw_year_month_path.mkdir(parents=True, exist_ok=True)
        
        # Call LLM with retries
        for attempt in range(max_retries):
            try:
                print(f"🤖 Calling Gemini API (attempt {attempt + 1}/{max_retries})...")
                print("⏳ Waiting for response...")
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.1,
                        max_output_tokens=65536,
                        response_mime_type="application/json"
                    )
                )
                
                print("✅ Response received!")
                
                # Print model response to terminal
                print(f"\n{'='*60}")
                print(f"🤖 MODEL RESPONSE FOR {appendix_number}:")
                print(f"{'='*60}")
                print(response.text)
                print(f"{'='*60}\n")
                
                # Save raw response
                raw_file = raw_year_month_path / f"{appendix_file.stem}_attempt_{attempt + 1}_raw.txt"
                with open(raw_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== RAW RESPONSE ===\n")
                    f.write(f"Appendix: {appendix_file.name}\n")
                    f.write(f"Attempt: {attempt + 1}\n")
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"Response length: {len(response.text)} chars\n")
                    f.write(f"===================\n\n")
                    f.write(response.text)
                
                print(f"💾 Raw response saved: {raw_file}")
                print(f"📏 Response length: {len(response.text):,} characters")
                
                # Parse JSON
                json_text = response.text.strip()
                
                # Clean up response
                if json_text.startswith("```json"):
                    json_text = json_text.replace("```json", "").replace("```", "").strip()
                elif json_text.startswith("```"):
                    json_text = json_text.replace("```", "").strip()
                
                print("🔍 Parsing JSON...")
                
                extracted_data = json.loads(json_text)
                
                if not isinstance(extracted_data, list):
                    raise ValueError("Response is not a JSON array")
                
                print(f"✅ Extraction successful: {len(extracted_data)} records")
                
                # Add metadata to each record
                for record in extracted_data:
                    if "record_id" not in record:
                        record["record_id"] = str(uuid.uuid4())
                    if "metadata" not in record:
                        record["metadata"] = {}
                    record["metadata"].update({
                        "source_file": source_file,
                        "appendix_number": appendix_number,
                        "extraction_method": "LLM_Extraction",
                        "extraction_confidence": 0.9,
                        "extraction_timestamp": datetime.now().isoformat()
                    })
                
                return {
                    "success": True,
                    "appendix_key": appendix_file.stem,
                    "records_count": len(extracted_data),
                    "data": extracted_data,
                    "metadata": {
                        "year": year,
                        "month": month,
                        "appendix_number": appendix_number,
                        "source_file": source_file,
                        "extraction_timestamp": datetime.now().isoformat(),
                        "estimated_tokens": estimated_tokens,
                        "attempts": attempt + 1
                    }
                }
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error (attempt {attempt + 1}): {e}")
                print(f"📍 Error position: line {getattr(e, 'lineno', '?')}, column {getattr(e, 'colno', '?')}")
                
                # Save debug info
                debug_file = raw_year_month_path / f"{appendix_file.stem}_attempt_{attempt + 1}_json_error.txt"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== JSON PARSING ERROR ===\n")
                    f.write(f"Error: {e}\n")
                    f.write(f"Position: line {getattr(e, 'lineno', '?')}, column {getattr(e, 'colno', '?')}\n")
                    f.write(f"==========================\n\n")
                    f.write("CLEANED JSON TEXT:\n")
                    f.write(json_text)
                
                print(f"🐛 Debug file saved: {debug_file}")
                
                if attempt == max_retries - 1:
                    return {
                        "success": False,
                        "error": f"JSON parsing failed after {max_retries} attempts: {e}",
                        "debug_file": str(debug_file)
                    }
                
            except Exception as e:
                print(f"❌ API error (attempt {attempt + 1}): {e}")
                
                # Save error info
                error_file = raw_year_month_path / f"{appendix_file.stem}_attempt_{attempt + 1}_api_error.txt"
                with open(error_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== API ERROR ===\n")
                    f.write(f"Appendix: {appendix_file.name}\n")
                    f.write(f"Attempt: {attempt + 1}\n")
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"Error: {str(e)}\n")
                    f.write(f"Error type: {type(e).__name__}\n")
                    f.write(f"=================\n")
                
                print(f"🐛 Error logged: {error_file}")
                
                if attempt == max_retries - 1:
                    return {
                        "success": False,
                        "error": f"API call failed after {max_retries} attempts: {str(e)}",
                        "error_file": str(error_file)
                    }
                else:
                    print(f"🔄 Retrying in 5 seconds...")
                    import time
                    time.sleep(5)
        
        return {"success": False, "error": "Unexpected error"}

    def save_results(self, result: Dict[str, Any]) -> Dict[str, str]:
        """Save extraction results to JSON and CSV with organized folder structure"""
        if not result["success"]:
            print(f"❌ Cannot save failed extraction: {result.get('error', 'Unknown error')}")
            return {"success": False, "error": result.get("error")}
        
        appendix_key = result["appendix_key"]
        data = result["data"]
        metadata = result["metadata"]
        
        # Create year/month folder structure
        year = metadata["year"]
        month = metadata["month"]
        year_month_path = self.output_path / str(year) / f"{month:02d}"
        year_month_path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_file = year_month_path / f"{appendix_key}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": metadata,
                "records": data
            }, f, indent=2, ensure_ascii=False)
        
        # Convert to CSV
        csv_file = year_month_path / f"{appendix_key}.csv"
        self.json_to_csv(data, csv_file)
        
        # Save summary
        summary_file = year_month_path / f"{appendix_key}_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"=== EXTRACTION SUMMARY ===\n")
            f.write(f"Appendix: {appendix_key}\n")
            f.write(f"Year/Month: {year}/{month:02d}\n")
            f.write(f"Records extracted: {len(data)}\n")
            f.write(f"Extraction timestamp: {metadata.get('extraction_timestamp')}\n")
            f.write(f"Attempts: {metadata.get('attempts', 1)}\n")
            f.write(f"Source file: {metadata.get('source_file')}\n")
            f.write(f"Appendix number: {metadata.get('appendix_number')}\n")
            f.write(f"========================\n")
        
        print(f"💾 Saved: {json_file}")
        print(f"💾 Saved: {csv_file}")
        print(f"📋 Summary: {summary_file}")
        
        return {
            "success": True,
            "json_file": str(json_file),
            "csv_file": str(csv_file),
            "summary_file": str(summary_file),
            "records_count": len(data)
        }

    def json_to_csv(self, records: List[Dict], output_file: Path):
        """Convert JSON records to CSV with flattened structure"""
        if not records:
            print("⚠️  No records to convert to CSV")
            return
        
        # Flatten nested dictionaries
        flattened_records = []
        for record in records:
            flat_record = self._flatten_dict(record)
            flattened_records.append(flat_record)
        
        # Create DataFrame
        df = pd.DataFrame(flattened_records)
        
        # Save to CSV
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"📊 CSV created with {len(df)} rows, {len(df.columns)} columns")

    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, json.dumps(v, ensure_ascii=False)))
            else:
                items.append((new_key, v))
        return dict(items)

    def process_batch_by_year_range(self, start_year: int, end_year: int) -> Dict[str, Any]:
        """Process all appendices in a year range"""
        results = {}
        total_records = 0
        successful = 0
        
        for year in range(start_year, end_year + 1):
            year_folder = self.segments_base_path / str(year)
            if not year_folder.exists():
                print(f"⚠️  Year folder not found: {year}")
                continue
            
            appendix_files = list(year_folder.glob("*.md"))
            appendix_files.sort()
            
            print(f"\n📅 Processing year {year}: {len(appendix_files)} files")
            
            for appendix_file in appendix_files:
                print(f"\n{'='*60}")
                print(f"🔄 Processing: {appendix_file.name}")
                
                try:
                    result = self.extract_single_appendix(appendix_file)
                    save_result = self.save_results(result)
                    
                    results[appendix_file.stem] = {
                        "extraction": result,
                        "save": save_result
                    }
                    
                    if result["success"]:
                        print(f"✅ Success: {result['records_count']} records")
                        total_records += result['records_count']
                        successful += 1
                    else:
                        print(f"❌ Failed: {result.get('error')}")
                        
                except Exception as e:
                    print(f"❌ Error processing {appendix_file.name}: {e}")
                    results[appendix_file.stem] = {
                        "extraction": {"success": False, "error": str(e)},
                        "save": {"success": False, "error": str(e)}
                    }
        
        print(f"\n{'='*60}")
        print(f"📊 BATCH SUMMARY:")
        print(f"✅ Successful: {successful}")
        print(f"📈 Total records: {total_records}")
        
        return {
            "total_processed": len(results),
            "successful": successful,
            "total_records": total_records,
            "results": results
        }

def show_usage():
    """Show usage instructions"""
    print("""
🚀 FLEXIBLE LLM EXTRACTION TOOL

📋 USAGE OPTIONS:

1️⃣ SINGLE APPENDIX BY PATH:
   python llm_extraction_flexible.py /path/to/appendix.md

2️⃣ SINGLE APPENDIX BY YEAR/MONTH/APPENDIX:
   python llm_extraction_flexible.py 2009 02 PL1
   
3️⃣ BATCH BY YEAR RANGE:
   python llm_extraction_flexible.py --batch-year 2009 2013
   
4️⃣ BATCH BY SPECIFIC MONTHS:
   python llm_extraction_flexible.py --batch-months 2009-02 2009-03 2010-01

📁 OUTPUT STRUCTURE:
   extracted_data/
   ├── 2009/
   │   ├── 02/
   │   │   ├── 2009_02_PHULUC_t02_2009_FINAL_PL1.json
   │   │   ├── 2009_02_PHULUC_t02_2009_FINAL_PL1.csv
   │   │   └── 2009_02_PHULUC_t02_2009_FINAL_PL1_summary.txt
   │   └── 03/
   └── 2010/

🔧 EXAMPLES:
   # Single file
   python llm_extraction_flexible.py 2009 02 PL1
   
   # Full path
   python llm_extraction_flexible.py "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/segments/2009/2009_02_PHULUC_t02_2009_FINAL_PL1.md"
   
   # Year range
   python llm_extraction_flexible.py --batch-year 2009 2010
""")

def main():
    """Main function with flexible interface"""
    if len(sys.argv) < 2:
        show_usage()
        return
    
    # Initialize extractor
    extractor = FlexibleLLMExtractor(api_key=GEMINI_API_KEY)
    
    args = sys.argv[1:]
    
    try:
        if args[0] == "--batch-year" and len(args) >= 3:
            # Batch processing by year range
            start_year = int(args[1])
            end_year = int(args[2])
            print(f"🔄 Batch processing years {start_year}-{end_year}")
            result = extractor.process_batch_by_year_range(start_year, end_year)
            
        elif args[0] == "--batch-months" and len(args) >= 2:
            # Batch processing by specific months
            months = args[1:]
            print(f"🔄 Batch processing months: {months}")
            # TODO: Implement batch by months
            print("⚠️  Batch by months not implemented yet")
            
        elif len(args) == 1 and os.path.exists(args[0]):
            # Single file by full path
            appendix_file = Path(args[0])
            print(f"📄 Processing single file: {appendix_file}")
            
            result = extractor.extract_single_appendix(appendix_file)
            save_result = extractor.save_results(result)
            
            if result["success"]:
                print(f"✅ Success: {result['records_count']} records extracted")
            else:
                print(f"❌ Failed: {result.get('error')}")
                
        elif len(args) == 3:
            # Single appendix by year/month/appendix
            year = int(args[0])
            month = int(args[1])
            appendix = args[2]
            
            print(f"🔍 Looking for: Year={year}, Month={month:02d}, Appendix={appendix}")
            
            appendix_file = extractor.find_appendix_file(year, month, appendix)
            if not appendix_file:
                return
            
            print(f"📄 Found file: {appendix_file}")
            
            result = extractor.extract_single_appendix(appendix_file)
            save_result = extractor.save_results(result)
            
            if result["success"]:
                print(f"✅ Success: {result['records_count']} records extracted")
            else:
                print(f"❌ Failed: {result.get('error')}")
                
        else:
            print("❌ Invalid arguments")
            show_usage()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        show_usage()

if __name__ == "__main__":
    main()