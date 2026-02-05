#!/usr/bin/env python3
"""
LLM Extraction Script for Vietnamese Agricultural Data
Uses Gemini 2.5 Flash to extract data from merged monthly segments
Output: JSON according to schema_improved_v2.json + CSV conversion
"""

import os
import json
from google.genai import types
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

# Gemini API
from google import genai

# Configuration
GEMINI_API_KEY = " "  # Replace with your actual API key
MODEL_NAME = "gemini-2.5-flash"

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
        self.output_path = self.base_path / "extracted_data"
        
        # Create output directories
        self.output_path.mkdir(exist_ok=True)
        self.raw_output_path = self.base_path / "raw_responses"
        self.raw_output_path.mkdir(exist_ok=True)
        
        # Load guide and schema
        self.extraction_guide = self._load_guide()
        self.schema = self._load_schema()
        
        print(f"🚀 LLM Extractor initialized")
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
    "source_file": "2009_02.md",
    "appendix_number": "PL1",
    "table_index": 1,
    "extraction_method": "LLM_Extraction"
  }}
}}"""

    def _create_user_prompt(self, monthly_file: str, year: int, month: int) -> str:
        """Create user prompt with monthly data"""
        return f"""Extract data from this Vietnamese agricultural report for {year}-{month:02d}:

METADATA:
- Year: {year}
- Month: {month}
- Source file: {year}_{month:02d}.md
- Report date: {year}-{month:02d}-15

MARKDOWN CONTENT:
{monthly_file}

Extract ALL data from ALL appendices in this file. Create separate records for each data point according to the schema and guide."""

    def extract_month(self, year: int, month: int, max_retries: int = 3) -> Dict[str, Any]:
        """Extract data for a specific month"""
        month_key = f"{year}_{month:02d}"
        input_file = self.segment_month_path / f"{month_key}.md"
        
        if not input_file.exists():
            raise FileNotFoundError(f"Monthly file not found: {input_file}")
        
        print(f"📄 Processing: {month_key}")
        
        # Load monthly data
        with open(input_file, 'r', encoding='utf-8') as f:
            monthly_content = f.read()
        
        print(f"📊 File size: {len(monthly_content)} characters")
        
        # Create prompts
        system_prompt = self._create_system_prompt()
        user_prompt = self._create_user_prompt(monthly_content, year, month)
        
        # Estimate tokens (rough)
        total_chars = len(system_prompt) + len(user_prompt)
        estimated_tokens = total_chars // 4  # Rough estimation
        print(f"🔢 Estimated tokens: {estimated_tokens:,}")
        
        if estimated_tokens > 1_000_000:
            print("⚠️  Warning: Approaching token limit!")
        
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
                
                # Save raw response
                raw_file = self.raw_output_path / f"{month_key}_attempt_{attempt + 1}_raw.txt"
                with open(raw_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== RAW RESPONSE ===\n")
                    f.write(f"Month: {month_key}\n")
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
                        "source_file": f"{month_key}.md",
                        "extraction_method": "LLM_Extraction",
                        "extraction_confidence": 0.9,
                        "extraction_timestamp": datetime.now().isoformat()
                    })
                
                return {
                    "success": True,
                    "month_key": month_key,
                    "records_count": len(extracted_data),
                    "data": extracted_data,
                    "metadata": {
                        "year": year,
                        "month": month,
                        "source_file": f"{month_key}.md",
                        "extraction_timestamp": datetime.now().isoformat(),
                        "estimated_tokens": estimated_tokens,
                        "attempts": attempt + 1
                    }
                }
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error (attempt {attempt + 1}): {e}")
                print(f"📍 Error position: line {getattr(e, 'lineno', '?')}, column {getattr(e, 'colno', '?')}")
                
                # Save problematic JSON for debugging
                debug_file = self.raw_output_path / f"{month_key}_attempt_{attempt + 1}_json_error.txt"
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
                error_file = self.raw_output_path / f"{month_key}_attempt_{attempt + 1}_api_error.txt"
                with open(error_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== API ERROR ===\n")
                    f.write(f"Month: {month_key}\n")
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
        
        month_key = result["month_key"]
        data = result["data"]
        
        # Save JSON
        json_file = self.output_path / f"{month_key}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": result["metadata"],
                "records": data
            }, f, indent=2, ensure_ascii=False)
        
        # Convert to CSV
        csv_file = self.output_path / f"{month_key}.csv"
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
    """Main function for testing"""
    # Initialize extractor
    extractor = LLMExtractor(api_key=GEMINI_API_KEY)
    
    # Test with single month
    print("🧪 Testing with single month: 2009-02")
    result = extractor.extract_month(2009, 2)
    save_result = extractor.save_results(result)
    
    if result["success"]:
        print(f"✅ Test successful: {result['records_count']} records extracted")
    else:
        print(f"❌ Test failed: {result.get('error')}")

if __name__ == "__main__":
    main()