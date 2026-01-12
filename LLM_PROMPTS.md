# LLM Prompts for Agricultural Data Extraction (v2.0)

This document contains updated prompts aligned with `schema_final.json`.

---

## Strategy A: Table Extraction (Appendices 2008-2019)
**Target**: `Phuluc` files with Markdown tables.

### System Prompt
```text
You are a Data Engineer expert in Vietnamese Agriculture. Your goal is to transform Markdown tables into structured JSON records following a specific hierarchy.
```

### User Prompt Template
```text
Analyze the following Markdown content from an Agricultural Report (Year: {YEAR}).
Focus on tables about: {THEME}.

**Required Schema (JSON List):**
[
  {
    "record_id": "Unique string (format: YEAR_MONTH_LOC_ITEM_METRIC)",
    "time_context": {
      "year": {YEAR},
      "month": {MONTH},
      "report_date": "YYYY-MM-DD (extract from report header if available)"
    },
    "geo_context": {
      "geo_level": "National" | "Regional" | "Provincial",
      "location_name": "Standardized Vietnamese Name",
      "region_id": "Identifier (e.g., Mekong_Delta, Red_River_Delta)"
    },
    "item_context": {
      "sector": "Cultivation" | "Livestock" | "Fishery" | "Forestry" | "Trade" | "Pest",
      "commodity": "Core product name (e.g., Lúa, Lợn, Cá tra)",
      "sub_item": "Specific season/variety (e.g., Đông Xuân, Tôm thẻ chân trắng)",
      "variety": "Specific strain if mentioned"
    },
    "metric_context": {
      "attribute": "Metric type (Area, Output, Yield, Headcount, Value_USD)",
      "value": float,
      "unit": "Standardized unit (ha, ton, heads, USD)",
      "data_type": "Actual" | "Plan" | "Cumulative" | "Estimated"
    },
    "metadata": {
      "source_file": "{FILENAME}",
      "extraction_method": "Table_Parsing"
    }
  }
]

**Critical Extraction Rules:**
1. Flatten hierarchical headers. 
2. Normalize Numbers: "." is thousands sep, "," is decimal. Convert "1.234,5" to 1234.5.
3. Normalize Units: Convert "1000 ha" to "ha" by multiplying the value by 1000.
4. Normalize Provinces: Use standard names (e.g., "H.Nội" -> "Hà Nội").
```

---

## Strategy B: Narrative Text Extraction (Reports 2020-2022)
**Target**: `Baocao` text-heavy files.

### User Prompt Template
```text
Extract quantitative agricultural metrics from the following text ({YEAR}).

**Required Schema (JSON List):**
Follow the same nested structure as Strategy A, but set `metadata.extraction_method` to "Text_NER".

**Extraction Rules:**
1. Identify claims like "Production reached X tons" or "Export value was Y USD".
2. Capture the context (National vs Region) for geo_context.
3. For units like "triệu USD", convert to numeric Value: Value * 1000000, Unit: "USD".
4. If a range is given (e.g., 36000-38000), provide the average value.
```

## Data Augmentation & Standardization Strategy
After extraction, run a Python script to:
1.  **Normalize Units**: Convert "1000 ha" to "ha", "Tỷ USD" to "USD".
2.  **Standardize Province Names**: Map variants ("T.p HCM", "TP. Hồ Chí Minh") to a canonical ID.
3.  **Fill Gaps**: Interpolate missing months if cumulative data is available (e.g., Month 11 - Month 10 = November estimate).
