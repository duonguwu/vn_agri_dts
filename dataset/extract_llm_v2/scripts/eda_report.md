# 📊 Agricultural Data EDA & Quality Report
**Total Records:** 61,339
**Date Analysis:** 2008.0 - 2012.0

## 1. Missing Values (Nulls)
|                  |   Missing Count |   Percentage (%) |
|:-----------------|----------------:|-----------------:|
| year             |              50 |             0.08 |
| month            |              83 |             0.14 |
| report_date      |            7157 |            11.67 |
| period_type      |              98 |             0.16 |
| region_id        |            4520 |             7.37 |
| region_name_vn   |           17855 |            29.11 |
| sub_item         |           40035 |            65.27 |
| variety          |           61339 |           100    |
| processing_level |           61291 |            99.92 |
| comparison_type  |           60585 |            98.77 |
| comparison_value |           60597 |            98.79 |
| base_period      |           61321 |            99.97 |
| base_value       |           61295 |            99.93 |
| source_file      |           12836 |            20.93 |

## 2. Duplicate & Conflict Analysis
- **Strict Duplicates (all columns same):** 0 records
- **Logic Conflicts (Same Object, Different Values):** 129 cases found

   Sample Conflict Groups (Keys with >1 unique values):
|    |   year |   month | location_name   | sector      | commodity   | sub_item   | attribute     | data_type   | unit        |   value |
|---:|-------:|--------:|:----------------|:------------|:------------|:-----------|:--------------|:------------|:------------|--------:|
|  0 |   2009 |       2 | Bắc Trung Bộ    | Cultivation | Lúa         | Đông Xuân  | Area_Planted  | Actual      | 1000_ha     |       2 |
|  1 |   2009 |       2 | Cả nước         | Trade       | D A P       | Trong đó   | Import_Value  | Estimated   | million_USD |       2 |
|  2 |   2009 |       2 | Cả nước         | Trade       | D A P       | Trong đó   | Import_Volume | Estimated   | 1000_ton    |       2 |
|  3 |   2009 |       2 | Cả nước         | Trade       | N P K       | Trong đó   | Import_Value  | Estimated   | million_USD |       2 |
|  4 |   2009 |       2 | Cả nước         | Trade       | N P K       | Trong đó   | Import_Volume | Estimated   | 1000_ton    |       2 |

## 3. Schema Validity (Enums)
- ❌ **sector**: Found 4 invalid values: `['Industrial_Processing', 'Industry', 'Salt', 'Metadata']`
- ❌ **attribute**: Found 27 invalid values: `['Investment_Value', 'Forest_Area_Cared', 'Head_Count', 'Area_Maintained', 'Trees_Planted', 'Area_Regenerated', 'Area_Protected', 'Area_Damaged', 'Inventory', 'Draft_Power']`
- ❌ **unit**: Found 49 invalid values: `['head', '1000_eggs', '1000_USD', '1000 ha', 'Tr.cây', '1000 m3', '1000 Tấn', 'Triêụ USD', 'quintal_per_ha', 'tạ/ha']`
- ❌ **data_type**: Found 1 invalid values: `['Estimate']`
- ❌ **period_type**: Found 4 invalid values: `['Annual', 'Point_In_Time', 'Event', 'Yearly']`
- ❌ **geo_level**: Found 2 invalid values: `['International', 'Country']`

## 4. Value Distribution & Outliers
|       |   count |   mean |    std |   min |     25% |   50% |   75% |        max |
|:------|--------:|-------:|-------:|------:|--------:|------:|------:|-----------:|
| value |   61339 |  51913 | 533253 |  -155 | 10.0045 |   469 |  9700 | 6.4502e+07 |

- ⚠️ **Negative Values Found:** 2 records.
- ⚠️ **Suspected Extreme Area (>5M ha):** 1 records.

## 5. Coverage Analysis

Records per Month/Year:
|   year |   1.0 |   2.0 |   3.0 |   4.0 |   5.0 |   6.0 |   7.0 |   8.0 |   9.0 |   10.0 |   11.0 |   12.0 |
|-------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|-------:|-------:|-------:|
|   2008 |     0 |    72 |    26 |    37 |   343 |    17 |    17 |    14 |    23 |     37 |     12 |     76 |
|   2009 |   173 |   870 |   791 |  1035 |  1309 |  1424 |  1530 |  1520 |  1341 |   1135 |    839 |    842 |
|   2010 |   988 |   937 |   856 |  1070 |  1380 |  1478 |  1362 |  1574 |  1521 |   1120 |   1302 |   1149 |
|   2011 |  1005 |  1184 |  1459 |  1228 |   307 |  2005 |  1954 |  1789 |  1835 |   1331 |   1750 |   1348 |
|   2012 |  1088 |  1245 |  1314 |  1065 |  1473 |  1550 |  1707 |  1652 |  1298 |   1337 |   1454 |    658 |

## 6. Sector & Geography Distribution
| sector                |   count |
|:----------------------|--------:|
| Cultivation           |   35448 |
| Trade                 |   13999 |
| Forestry              |    6642 |
| Fishery               |    2736 |
| Investment            |    1368 |
| Livestock             |     566 |
| Metadata              |     437 |
| Industry              |      88 |
| Salt                  |      28 |
| Pest                  |      19 |
| Industrial_Processing |       8 |

| geo_level     |   count |
|:--------------|--------:|
| Provincial    |   37079 |
| National      |    8725 |
| Country       |    7598 |
| Regional      |    7358 |
| International |     579 |