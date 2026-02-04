for month in 01 02 03 04 05 06 07 08 10 11 12; do echo "=== Processing 2009/$month ==="; python3 dataset/extract_llm/scripts/extract_data.py 2009 $month 2>&1 | tail -3; done



for month in 01 02 03 04 05 06 07 08 10 11 12; do echo "=== Processing 2009/$month ==="; python3 extract_data.py 2009 $month 2>&1 | tail -3; done