#!/usr/bin/env python3
"""
LLM Extraction Script for Vietnamese Agricultural Data
Uses Gemini 2.5 Flash to extract data from merged monthly segments
Output: JSON according to schema_improved_v2.json + CSV conversion
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd

# Gemini API
from google import genai
from google.genai import types

# Configuration
GEMINI_API_KEY = " "
MODEL_NAME = "gemini-2.0-flash-lite"

class LLMExtractor:
    def __init__(self, api_key: str):
        """Initialize LLM Extractor with Gemini API"""
        self.client = genai.Client(api_key=api_key)
        self.model_name = MODEL_NAME
        
        # Paths
        self.base_path = Path(__file__).parent.parent
        self.guide_path = self.base_path / "LLM_EXTRACTION_GUIDE.md"
        self.schema_path = self.base_path / "schema_improved_v2.json"
        self.segment_month_path = self.base_path / "segment_month"
        self.output_base_path = self.base_path / "extracted_data"
        
        # Create base output directory
        self.output_base_path.mkdir(exist_ok=True)
        
        # Load guide and schema
        self.extraction_guide = self._load_guide()
        self.schema = self._load_schema()
        
        print("🚀 LLM Extractor initialized")
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

TASK: Extract structured data from Vietnamese agricultural reports \
(markdown tables) and convert to JSON format.

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
7. Set record_id is "xxxx", don't need uuid

OUTPUT FORMAT: JSON array only, no markdown formatting, no explanations.

EXAMPLE RECORD STRUCTURE:
{{
  "record_id": "xxxx",
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
    "source_file": "2009_02.md",
    "appendix_number": "PL1",
  }}
}}"""

    def _create_user_prompt(self, appendix_content: str, year: int,
                            month: int, appendix_number: str) -> str:
        """Create user prompt with appendix data"""
        return f"""Extract data from this Vietnamese agricultural appendix \
for {year}-{month:02d}:

METADATA:
- Year: {year}
- Month: {month}
- Appendix: {appendix_number}
- Report date: {year}-{month:02d}-15

MARKDOWN CONTENT:
{appendix_content}

Extract ALL data from this single appendix. Create separate records for \
each data point according to the schema and guide. Focus on accuracy and \
completeness."""

    def parse_filename(self, filename: str) -> Dict[str, Any]:
        """Parse filename to extract year, month, appendix number
        Format: 2009_02_PHULUC_t02_2009_FINAL_PL1.md
        """
        parts = filename.replace('.md', '').split('_')
        
        # Extract year (first part)
        year = int(parts[0])
        
        # Extract month (second part or from 't02' format)
        month = None
        if len(parts) > 1 and parts[1].isdigit():
            month = int(parts[1])
        else:
            # Look for 't02' format
            for part in parts:
                if part.startswith('t') and len(part) == 3 and part[1:].isdigit():
                    month = int(part[1:])
                    break
        
        if month is None:
            raise ValueError(f"Cannot extract month from filename: {filename}")
        
        # Extract appendix number (PL1, PL2, etc.)
        appendix_number = "Unknown"
        for part in parts:
            if part.startswith('PL') and len(part) > 2:
                appendix_number = part
                break
        
        return {
            "year": year,
            "month": month,
            "appendix_number": appendix_number,
            "filename": filename
        }

    def extract_appendix(self, appendix_file: Path, max_retries: int = 1) -> Dict[str, Any]:
        """Extract data for a specific appendix"""
        appendix_name = appendix_file.stem
        print(f"📄 Processing: {appendix_name}")
        
        # Load appendix data
        with open(appendix_file, 'r', encoding='utf-8') as f:
            appendix_content = f.read()
        
        print(f"📊 File size: {len(appendix_content)} characters")
        
        # Parse filename to get metadata
        file_info = self.parse_filename(appendix_file.name)
        year = file_info["year"]
        month = file_info["month"]
        appendix_number = file_info["appendix_number"]
        
        print(f"📅 Detected: Year={year}, Month={month:02d}, "
              f"Appendix={appendix_number}")
        
        # Create prompts
        system_prompt = self._create_system_prompt()
        user_prompt = self._create_user_prompt(appendix_content, year, month, appendix_number)
        
        # Estimate tokens (rough)
        total_chars = len(system_prompt) + len(user_prompt)
        estimated_tokens = total_chars // 4  # Rough estimation
        print(f"🔢 Estimated tokens: {estimated_tokens:,}")
        
        if estimated_tokens > 1_000_000:
            print("⚠️  Warning: Approaching token limit!")
        
        # Create year/month specific directories (before API call for error handling)
        year_month_dir = (self.output_base_path / f"{year}" /
                          f"{month:02d}")
        year_month_dir.mkdir(parents=True, exist_ok=True)
        
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
                print("📝 Model response preview:")
                print("=" * 50)
                print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
                print("=" * 50)
                
                # Save raw response
                raw_file = (year_month_dir /
                           f"{appendix_name}_attempt_{attempt + 1}_raw.txt")
                with open(raw_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== RAW RESPONSE ===\n")
                    f.write(f"Appendix: {appendix_name}\n")
                    f.write(f"Attempt: {attempt + 1}\n")
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"Response length: {len(response.text)} chars\n")
                    f.write(f"===================\n\n")
                    f.write(response.text)
                
                print(f"💾 Raw response saved: {raw_file}")
                print(f"📏 Response length: {len(response.text):,} characters")
                
                # Extract JSON from response
                json_text = response.text.strip()
                
                # Clean up response (remove markdown if present)
                if json_text.startswith("```json"):
                    json_text = json_text.replace("```json", "").replace("```", "").strip()
                elif json_text.startswith("```"):
                    json_text = json_text.replace("```", "").strip()
                
                print("🔍 Parsing JSON...")
                
                # Parse JSON
                extracted_data = json.loads(json_text)
                
                # Validate structure
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
                        "source_file": appendix_file.name,
                        "appendix_number": appendix_number,
                        "extraction_confidence": 0.9,
                        "extraction_timestamp": datetime.now().isoformat()
                    })
                
                return {
                    "success": True,
                    "appendix_key": appendix_name,
                    "records_count": len(extracted_data),
                    "data": extracted_data,
                    "metadata": {
                        "year": year,
                        "month": month,
                        "appendix_number": appendix_number,
                        "source_file": appendix_file.name,
                        "extraction_timestamp": datetime.now().isoformat(),
                        "estimated_tokens": estimated_tokens,
                        "attempts": attempt + 1
                    }
                }
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error (attempt {attempt + 1}): {e}")
                print(f"📍 Error position: line {getattr(e, 'lineno', '?')}, column {getattr(e, 'colno', '?')}")
                
                # Save problematic JSON for debugging
                debug_file = year_month_dir / f"{appendix_name}_attempt_{attempt + 1}_json_error.txt"
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
                        "raw_response_file": str(raw_file) if 'raw_file' in locals() else None,
                        "debug_file": str(debug_file)
                    }
                
            except Exception as e:
                print(f"❌ API error (attempt {attempt + 1}): {e}")
                
                # Save API error for debugging  
                error_file = year_month_dir / f"{appendix_name}_attempt_{attempt + 1}_api_error.txt"
                with open(error_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== API ERROR ===\n")
                    f.write(f"Appendix: {appendix_name}\n")
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
        """Save extraction results to JSON and CSV"""
        if not result["success"]:
            print(f"❌ Cannot save failed extraction: {result.get('error', 'Unknown error')}")
            return {"success": False, "error": result.get("error")}
        
        appendix_key = result["appendix_key"]
        data = result["data"]
        metadata = result["metadata"]
        
        # Create year/month directory
        year = metadata["year"]
        month = metadata["month"]
        year_month_dir = self.output_base_path / f"{year}" / f"{month:02d}"
        year_month_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_file = year_month_dir / f"{appendix_key}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": metadata,
                "records": data
            }, f, indent=2, ensure_ascii=False)
        
        # Convert to CSV
        csv_file = year_month_dir / f"{appendix_key}.csv"
        self.json_to_csv(data, csv_file)
        
        print(f"💾 Saved: {json_file}")
        print(f"💾 Saved: {csv_file}")
        
        return {
            "success": True,
            "json_file": str(json_file),
            "csv_file": str(csv_file),
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
                # Convert list to string representation
                items.append((new_key, json.dumps(v, ensure_ascii=False)))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def process_multiple_months(self, year_month_pairs: List[tuple]) -> Dict[str, Any]:
        """Process multiple months"""
        results = {}
        total_records = 0
        
        print(f"🔄 Processing {len(year_month_pairs)} months...")
        
        for year, month in year_month_pairs:
            month_key = f"{year}_{month:02d}"
            print(f"\n📅 Processing {month_key}...")
            
            try:
                result = self.extract_month(year, month)
                save_result = self.save_results(result)
                
                results[month_key] = {
                    "extraction": result,
                    "save": save_result
                }
                
                if result["success"]:
                    total_records += result["records_count"]
                    
            except Exception as e:
                print(f"❌ Error processing {month_key}: {e}")
                results[month_key] = {
                    "extraction": {"success": False, "error": str(e)},
                    "save": {"success": False, "error": str(e)}
                }
        
        print(f"\n✅ Processing complete!")
        print(f"📊 Total records extracted: {total_records}")
        
        return {
            "total_months": len(year_month_pairs),
            "total_records": total_records,
            "results": results
        }

def main():
    """Main function for processing a single appendix file"""
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 2:
        print("Usage: python llm_extraction.py <appendix_file>")
        print("Example: python llm_extraction.py segments/2009/2009_02_PHULUC_t02_2009_FINAL_PL1.md")
        return
    
    appendix_file = Path(sys.argv[1])
    if not appendix_file.exists():
        print(f"❌ File not found: {appendix_file}")
        return
    
    if not appendix_file.suffix == '.md':
        print(f"❌ File must be a markdown file (.md): {appendix_file}")
        return
    
    # Initialize extractor
    extractor = LLMExtractor(api_key=GEMINI_API_KEY)
    
    print(f"📁 Processing single file: {appendix_file.name}")
    print(f"{'='*60}")
    
    try:
        # Parse filename first to show detected info
        file_info = extractor.parse_filename(appendix_file.name)
        print(f"📅 Detected metadata:")
        print(f"   Year: {file_info['year']}")
        print(f"   Month: {file_info['month']:02d}")
        print(f"   Appendix: {file_info['appendix_number']}")
        print(f"{'='*60}")
        
        # Extract data
        result = extractor.extract_appendix(appendix_file)
        
        if result["success"]:
            # Save results
            save_result = extractor.save_results(result)
            
            if save_result["success"]:
                print(f"\n✅ EXTRACTION SUCCESSFUL!")
                print(f"📈 Records extracted: {result['records_count']}")
                print(f"💾 JSON file: {save_result['json_file']}")
                print(f"💾 CSV file: {save_result['csv_file']}")
                print(f"📁 Output directory: {Path(save_result['json_file']).parent}")
            else:
                print(f"\n❌ SAVE FAILED: {save_result.get('error')}")
        else:
            print(f"\n❌ EXTRACTION FAILED: {result.get('error')}")
            if 'raw_response_file' in result:
                print(f"🐛 Raw response saved: {result['raw_response_file']}")
            if 'debug_file' in result:
                print(f"🐛 Debug file saved: {result['debug_file']}")
            if 'error_file' in result:
                print(f"🐛 Error file saved: {result['error_file']}")
                
    except Exception as e:
        print(f"❌ Error processing {appendix_file.name}: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("🏁 Processing complete!")

if __name__ == "__main__":
    main()