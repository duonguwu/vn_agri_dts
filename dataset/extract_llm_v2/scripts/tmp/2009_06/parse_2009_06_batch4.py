import json
import uuid
import os

def generate_id():
    return str(uuid.uuid4())

def normalize_number(s):
    if s is None:
        return None
    if not isinstance(s, str):
        try:
            return float(s)
        except:
            return None
    s = s.strip()
    if s == "" or s == "-" or s == "." or s == "||" or s == "|" or s == '"' or s == "x":
        return None
    s = s.replace(",", "").replace("_", "").replace("*", "").replace("~~", "").replace("%", "")
    if " " in s: s = s.split()[0]
    try:
        return float(s)
    except:
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_pl8a_06():
    metadata = {"year": 2009, "month": 6, "appendix_number": "PL8a", "source_file": "2009_06_PHULUC_T06_2009_PL8a.md"}
    records = []
    
    # Structure: Commodity (starts with no index) followed by Countries (with index)
    # Col 3: 08 Vol, Col 4: 08 Val, Col 5: 09 Vol, Col 6: 09 Val
    
    current_commodity = None
    rows = [
        [None, "Cà phê", "495631", "1016063", "650749", "970165"],
        ["1", "Bỉ", "29014", "60354", "105105", "152163"],
        ["2", "Đức", "67227", "140706", "70418", "105809"],
        ["3", "Hoa Kỳ", "52532", "108994", "68293", "103552"],
        ["4", "Italia", "39848", "81301", "62144", "93441"],
        ["5", "Tây Ban Nha", "40012", "83281", "39458", "58943"],
        ["6", "Nhật Bản", "27842", "61066", "30455", "49111"],
        ["7", "Hà Lan", "8007", "16654", "25961", "37384"],
        ["8", "Pháp", "13156", "26479", "17305", "25293"],
        ["9", "Hàn Quốc", "19698", "41283", "16538", "25141"],
        ["10", "Anh", "21888", "45077", "15105", "22658"],
        
        [None, "Cao su", "187892", "458959", "183657", "258628"],
        ["1", "Trung Quốc", "121211", "300979", "129639", "181008"],
        ["2", "Hàn Quốc", "10987", "24581", "8985", "11540"],
        ["3", "Malaixia", "3134", "7524", "6247", "8579"],
        ["4", "Đức", "7430", "17906", "4747", "7957"],
        ["5", "Đài Loan", "6800", "17252", "5366", "7943"],
        ["6", "Hoa Kỳ", "3590", "7923", "4104", "5984"],
        ["7", "Nhật Bản", "5464", "13923", "3019", "4674"],
        ["8", "Thổ Nhĩ Kỳ", "3168", "6668", "2550", "3767"],
        ["9", "Nga", "4334", "12049", "2303", "3610"],
        
        [None, "Chè", "34118", "44066", "40122", "49778"],
        ["1", "Pakixtan", "3961", "8188", "10299", "14219"],
        ["2", "Nga", "4343", "5237", "7100", "8508"],
        ["3", "Đài Loan", "6588", "7577", "5915", "7205"],
        ["4", "Trung Quốc", "1885", "2107", "2423", "2634"],
        ["5", "Ấn Độ", "813", "736", "1629", "1612"],
        ["6", "Hoa Kỳ", "1537", "1089", "1471", "1387"],
        ["7", "Inđônêxia", "918", "707", "1693", "1280"],
        ["8", "Đức", "706", "1221", "807", "1047"],
        ["9", "Ba Lan", "877", "1005", "546", "605"],
        ["10", "Philippine", "361", "1163", "132", "410"],
        
        [None, "Gạo", "2233572", "1259666", "3152085", "1490977"],
        ["1", "Philippine", "1043131", "580240", "1383609", "752373"],
        ["2", "Malaixia", "205398", "128164", "295560", "128802"],
        ["3", "Cuba", "230398", "70623", "211650", "89183"],
        ["4", "Irắc", "102500", "48130", "168000", "67540"],
        ["5", "Xinh ga po", "21108", "10871", "119285", "50678"],
        ["6", "Đài Loan", "16738", "8346", "58217", "23785"],
        ["7", "Nga", "27303", "13836", "41421", "17960"],
        ["8", "Nam Phi", "3723", "1687", "30073", "12995"],
        ["9", "Ucraina", "3650", "1801", "22041", "9368"],
        ["10", "Inđônêxia", "46622", "21376", "17000", "6789"],
        
        [None, "Gỗ và sản phẩm gỗ", None, "1150083", None, "934453"],
        ["1", "Hoa Kỳ", None, "402632", None, "373695"],
        ["2", "Nhật Bản", None, "135444", None, "140003"],
        ["3", "Anh", None, "103311", None, "68750"],
        ["4", "Trung Quốc", None, "62523", None, "39842"],
        ["5", "Đức", None, "64111", None, "39008"],
        ["6", "Hàn Quốc", None, "39362", None, "32131"],
        ["7", "Hà Lan", None, "36187", None, "31155"],
        ["8", "Pháp", None, "48339", None, "28763"],
        ["9", "Ôxtrâylia", None, "24472", None, "19179"],
        ["10", "Italia", None, "22883", None, "15856"],
        
        [None, "Hàng rau quả", None, "157905", None, "163598"],
        ["1", "Nga", None, "17357", None, "15979"],
        ["2", "Trung Quốc", None, "15501", None, "15684"],
        ["3", "Nhật Bản", None, "12418", None, "12250"],
        ["4", "Đài Loan", None, "11906", None, "6721"],
        ["5", "Inđônêxia", None, "10750", None, "5835"],
        ["6", "Hà Lan", None, "6106", None, "5488"],
        ["7", "Hoa Kỳ", None, "8886", None, "5108"],
        ["8", "Thái Lan", None, "4531", None, "4104"],
        ["9", "Xinh ga po", None, "4716", None, "3917"],
        ["10", "Hàn Quốc", None, "4906", None, "3229"],
        
        [None, "Hàng thủy sản", "423676", "1513494", "401630", "1373455"],
        ["1", "Nhật Bản", "51373", "284265", "36519", "240013"],
        ["2", "Mỹ", "32115", "211083", "39594", "225371"],
        ["3", "Hàn Quốc", "35657", "110651", "34338", "100012"],
        ["4", "Đức", "21263", "74916", "22688", "73500"],
        ["5", "Tây Ban Nha", "24235", "64749", "24751", "61713"],
        ["6", "Ôxtrâylia", "8892", "45942", "8299", "39713"],
        ["7", "Italia", "20060", "66759", "14180", "38929"],
        ["8", "Trung Quốc", "5710", "20828", "9992", "37939"],
        ["9", "Hà Lan", "17496", "56147", "10775", "34543"],
        ["10", "Bỉ", "9378", "37066", "8585", "31817"],
        
        [None, "Hạt điều", "55625", "288604", "57800", "255696"],
        ["1", "Hoa Kỳ", "15286", "78893", "17044", "74157"],
        ["2", "Trung Quốc", "10788", "54739", "13786", "57692"],
        ["3", "Hà Lan", "8556", "44669", "7693", "39574"],
        ["4", "Ôxtrâylia", "3776", "20084", "3461", "15730"],
        ["5", "Anh", "3659", "19550", "2153", "9776"],
        ["6", "Đức", "622", "3395", "1045", "4986"],
        ["7", "Nga", "2875", "13872", "952", "4243"],
        ["8", "Canađa", "2396", "13806", "882", "3977"],
        ["9", "Thái Lan", "552", "3148", "777", "3572"],
        ["10", "UAE", "475", "2751", "864", "3343"],
        
        [None, "Hạt tiêu", "36484", "129527", "52722", "122645"],
        ["1", "Hoa Kỳ", "3957", "10930", "4216", "12538"],
        ["2", "Đức", "2175", "9820", "4205", "10248"],
        ["3", "UAE", "3171", "10863", "4777", "9476"],
        ["4", "Hà Lan", "2329", "8714", "3395", "8683"],
        ["5", "Ai Cập", "2730", "9894", "3670", "7306"],
        ["6", "Ấn Độ", "994", "3381", "2540", "5517"],
        ["7", "Pakixtan", "1497", "5110", "2744", "5402"],
        ["8", "Tây Ban Nha", "955", "3915", "2068", "4871"],
        ["9", "Xinh ga po", "2359", "7809", "2316", "4441"],
        ["10", "Nhật Bản", "537", "2307", "806", "4100"],
        
        [None, "Sản phẩm mây tre cói", None, "91788", None, "71656"],
        ["1", "Đức", None, "14083", None, "11494"],
        ["2", "Nhật Bản", None, "13221", None, "10564"],
        ["3", "Hoa Kỳ", None, "12731", None, "10344"],
        ["4", "Italia", None, "4057", None, "3706"],
        ["5", "Đài Loan", None, "4257", None, "3249"],
        ["6", "Pháp", None, "5134", None, "3024"],
        ["7", "Tây Ban Nha", None, "4206", None, "2957"],
        ["8", "Hà Lan", None, "2882", None, "2283"],
        ["9", "Anh", None, "3136", None, "2146"],
        ["10", "Bỉ", None, "1694", None, "2008"],
    ]

    for r in rows:
        idx, loc, v08, g08, v09, g09 = r
        if idx is None:
            current_commodity = loc
            geo = "National"
            loc_name = "Cả nước"
        else:
            geo = "International"
            loc_name = loc
            
        # 5 months 2008 (Cumulative)
        val_v = normalize_number(v08)
        val_g = normalize_number(g08)
        if val_v:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2008, "month": 5, "period_type": "Cumulative"},
                "geo_context": {"geo_level": geo, "location_name": loc_name},
                "item_context": {"sector": "Trade", "commodity": current_commodity},
                "metric_context": {"attribute": "Export_Volume", "value": val_v, "unit": "ton", "data_type": "Actual"},
                "metadata": metadata
            })
        if val_g:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2008, "month": 5, "period_type": "Cumulative"},
                "geo_context": {"geo_level": geo, "location_name": loc_name},
                "item_context": {"sector": "Trade", "commodity": current_commodity},
                "metric_context": {"attribute": "Export_Value", "value": val_g, "unit": "1000_USD", "data_type": "Actual"},
                "metadata": metadata
            })
            
        # 5 months 2009 (Cumulative)
        val_v = normalize_number(v09)
        val_g = normalize_number(g09)
        if val_v:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative"},
                "geo_context": {"geo_level": geo, "location_name": loc_name},
                "item_context": {"sector": "Trade", "commodity": current_commodity},
                "metric_context": {"attribute": "Export_Volume", "value": val_v, "unit": "ton", "data_type": "Actual"},
                "metadata": metadata
            })
        if val_g:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative"},
                "geo_context": {"geo_level": geo, "location_name": loc_name},
                "item_context": {"sector": "Trade", "commodity": current_commodity},
                "metric_context": {"attribute": "Export_Value", "value": val_g, "unit": "1000_USD", "data_type": "Actual"},
                "metadata": metadata
            })
            
    return {"metadata": metadata, "records": records}


def parse_pl8b_06():
    metadata = {"year": 2009, "month": 6, "appendix_number": "PL8b", "source_file": "2009_06_PHULUC_T06_2009_PL8b.md"}
    records = []
    
    current_commodity = None
    # [Idx, Name, 08Vol, 08Val, 09Vol, 09Val]
    rows = [
        [None, "Bông các loại", "124925", "186931", "83874", "106566"],
        ["1", "Hoa Kỳ", "37298", "54810", "51606", "67130"],
        ["2", "Braxin", "3347", "5063", "4434", "6031"],
        ["3", "Inđônêxia", "2465", "3164", "2409", "2390"],
        ["4", "Ấn Độ", "45437", "69883", "1804", "2371"],
        ["5", "Trung Quốc", "197", "388", "1174", "1553"],
        ["6", "Đài Loan", "4088", "5637", "564", "616"],
        ["7", "Thụy Sĩ", "2469", "3469", "470", "591"],
        ["8", "Italia", "1291", "1194", "663", "457"],
        ["9", "Hàn Quốc", "754", "1057", "236", "358"],
        
        [None, "Cao su", "85233", "207785", "96789", "134824"],
        ["1", "Thái Lan", "15674", "37404", "28594", "36783"],
        ["2", "Hàn Quốc", "12362", "30674", "16856", "22712"],
        ["3", "Campuchia", "10412", "26813", "14631", "20426"],
        ["4", "Đài Loan", "16015", "33086", "7170", "11105"],
        ["5", "Inđônêxia", "2506", "6596", "8703", "10836"],
        ["6", "Nhật Bản", "6376", "19849", "4656", "10054"],
        ["7", "Trung Quốc", "3121", "5976", "2835", "5189"],
        ["8", "Malaixia", "2364", "4700", "3948", "4460"],
        ["9", "Nga", "4944", "15619", "1554", "3128"],
        ["10", "Pháp", "526", "1486", "861", "2473"],
        
        [None, "Dầu mỡ động thực vật", None, "337054", None, "182271"],
        ["1", "Malaixia", None, "109625", None, "78652"],
        ["2", "Inđônêxia", None, "137897", None, "56204"],
        ["3", "Achentina", None, "30002", None, "19478"],
        ["4", "Thái Lan", None, "10625", None, "18223"],
        ["5", "Hoa Kỳ", None, "984", None, "1121"],
        ["6", "Xinh ga po", None, "1838", None, "1105"],
        ["7", "Hàn Quốc", None, "2212", None, "1066"],
        ["8", "Ôxtrâylia", None, "1349", None, "677"],
        ["9", "Trung Quốc", None, "31112", None, "426"],
        ["10", "Ấn Độ", None, "2400", None, "231"],
        
        [None, "Gỗ và sản phẩm gỗ", None, "484123", None, "276364"],
        ["1", "Malaixia", None, "75518", None, "43849"],
        ["2", "Trung Quốc", None, "52330", None, "35915"],
        ["3", "Lào", None, "62919", None, "35566"],
        ["4", "Hoa Kỳ", None, "48882", None, "30297"],
        ["5", "Niu zi lân", None, "18484", None, "17130"],
        ["6", "Campuchia", None, "25627", None, "15268"],
        ["7", "Thái Lan", None, "24515", None, "13839"],
        ["8", "Braxin", None, "20813", None, "9187"],
        ["9", "Đài Loan", None, "13467", None, "5714"],
        ["10", "Ôxtrâylia", None, "5815", None, "5035"],
        
        [None, "Lúa mỳ", "339378", "138647", "497984", "124491"],
        ["1", "Ôxtrâylia", "202558", "85372", "396794", "104955"],
        ["2", "Ucraina", "5200", "2532", "70093", "11417"],
        ["3", "Hoa Kỳ", "33426", "13585", "6653", "1968"],
        ["4", "Trung Quốc", "17812", "5486", "198", "97"],
        
        [None, "Phân bón các loại", "1985027", "904811", "1925373", "614671"],
        ["1", "Trung Quốc", "1108425", "536633", "603773", "199111"],
        ["2", "Philippine", "73800", "42550", "177740", "71043"],
        ["3", "Nga", "201710", "75862", "248498", "66254"],
        ["4", "Hoa Kỳ", "387", "658", "101872", "41049"],
        ["5", "Hàn Quốc", "89253", "51704", "147121", "34369"],
        ["6", "Canađa", "82981", "39370", "44029", "30429"],
        ["7", "Đài Loan", "61684", "15446", "76057", "12202"],
        ["8", "Ấn Độ", "6107", "4179", "19130", "8190"],
        ["9", "Nhật Bản", "96473", "25406", "33875", "4786"],
        ["10", "Malaixia", "9181", "3497", "14252", "4497"],
        
        [None, "Sữa & sản phẩm sữa", None, "217059", None, "189839"],
        ["1", "Niu zi lân", None, "64359", None, "46000"],
        ["2", "Hà Lan", None, "60520", None, "28860"],
        ["3", "Đan Mạch", None, "1074", None, "23118"],
        ["4", "Hoa Kỳ", None, "15365", None, "17808"],
        ["5", "Thái Lan", None, "21827", None, "11449"],
        ["6", "Malaixia", None, "11191", None, "10863"],
        ["7", "Ôxtrâylia", None, "8388", None, "8117"],
        ["8", "Pháp", None, "5889", None, "4093"],
        ["9", "Ba Lan", None, "10895", None, "3999"],
        ["10", "Đức", None, "1751", None, "1360"],
        
        [None, "Thức ăn gia súc & nguyên liệu", None, "846506", None, "583367"],
        ["1", "Ấn Độ", None, "494897", None, "233830"],
        ["2", "Achentina", None, "27161", None, "79574"],
        ["3", "Hoa Kỳ", None, "62040", None, "63403"],
        ["4", "Trung Quốc", None, "57746", None, "47494"],
        ["5", "Inđônêxia", None, "19766", None, "19013"],
        ["6", "Thái Lan", None, "24837", None, "13958"],
        ["7", "Italia", None, "4664", None, "10391"],
        ["8", "Đài Loan", None, "8962", None, "8214"],
        ["9", "Hàn Quốc", None, "5285", None, "6873"],
        ["10", "UAE", None, "17530", None, "6076"],
        
        [None, "Thuốc trừ sâu & nguyên liệu", None, "245236", None, "186162"],
        ["1", "Trung Quốc", None, "113735", None, "79958"],
        ["2", "Ấn Độ", None, "19671", None, "17238"],
        ["3", "Thụy Sĩ", None, "331", None, "14242"],
        ["4", "Đức", None, "13803", None, "11792"],
        ["5", "Hàn Quốc", None, "6745", None, "9940"],
        ["6", "Nhật Bản", None, "9042", None, "9359"],
        ["7", "Thái Lan", None, "5929", None, "8136"],
        ["8", "Xinh ga po", None, "43244", None, "6394"],
        ["9", "Inđônêxia", None, "5695", None, "5932"],
        ["10", "Anh", None, "504", None, "4796"],
    ]
    
    for r in rows:
        idx, loc, v08, g08, v09, g09 = r
        if idx is None:
            current_commodity = loc
            geo = "National"
            loc_name = "Cả nước"
        else:
            geo = "International"
            loc_name = loc
            
        # 5 months 2008 (Cumulative)
        val_v = normalize_number(v08)
        val_g = normalize_number(g08)
        if val_v:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2008, "month": 5, "period_type": "Cumulative"},
                "geo_context": {"geo_level": geo, "location_name": loc_name},
                "item_context": {"sector": "Trade", "commodity": current_commodity},
                "metric_context": {"attribute": "Import_Volume", "value": val_v, "unit": "ton", "data_type": "Actual"},
                "metadata": metadata
            })
        if val_g:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2008, "month": 5, "period_type": "Cumulative"},
                "geo_context": {"geo_level": geo, "location_name": loc_name},
                "item_context": {"sector": "Trade", "commodity": current_commodity},
                "metric_context": {"attribute": "Import_Value", "value": val_g, "unit": "1000_USD", "data_type": "Actual"},
                "metadata": metadata
            })
            
        # 5 months 2009 (Cumulative)
        val_v = normalize_number(v09)
        val_g = normalize_number(g09)
        if val_v:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative"},
                "geo_context": {"geo_level": geo, "location_name": loc_name},
                "item_context": {"sector": "Trade", "commodity": current_commodity},
                "metric_context": {"attribute": "Import_Volume", "value": val_v, "unit": "ton", "data_type": "Actual"},
                "metadata": metadata
            })
        if val_g:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 5, "period_type": "Cumulative"},
                "geo_context": {"geo_level": geo, "location_name": loc_name},
                "item_context": {"sector": "Trade", "commodity": current_commodity},
                "metric_context": {"attribute": "Import_Value", "value": val_g, "unit": "1000_USD", "data_type": "Actual"},
                "metadata": metadata
            })
            
    return {"metadata": metadata, "records": records}


def parse_pl9_06():
    metadata = {"year": 2009, "month": 6, "appendix_number": "PL9", "source_file": "2009_06_PHULUC_T06_2009_PL9.md"}
    records = []
    
    rows = [
        ["A", "Vốn ngân sách giao đầu năm", "2954763", "1168050", "166160", "1334210"],
        ["I", "Vốn thực hiện đầu tư", "2611500", "1109850", "157660", "1267510"],
        ["1", "Đầu tư Thuỷ lợi", "1483500", "760020", "115000", "875020"],
        ["2", "Đầu tư Nông nghiệp", "493000", "215145", "25460", "240605"],
        ["3", "Đầu tư Lâm nghiệp", "230000", "43688", "5200", "48888"],
        ["4", "Đầu tư Thuỷ sản", "24000", "9900", "1500", "11400"],
        ["5", "Khoa học - Công nghệ", "230000", "33170", "5000", "38170"],
        ["6", "Giáo dục - Đào tạo", "90000", "32677", "4500", "37177"],
        ["7", "Các ngành khác", "61000", "15250", "1000", "16250"],
        ["II", "Chương trình mục tiêu", "40263", "7050", "1000", "8050"],
        ["III", "Vốn đầu tư theo các mục tiêu nhiệm vụ cụ thể", "208000", "41150", "6500", "47650"],
        ["IV", "Bổ sung dự trữ Quốc gia", "65000", None, None, None],
        ["V", "Vốn chuẩn bị đầu tư", "30000", "10000", "1000", "11000"],
        ["B", "Vốn ứng trước cho các dự án cấp bách", "1000000", "219674", "43934", "263608"],
        ["", "Tổng vốn NS (A+B)", "3954763", "1387724", "210094", "1597818"],
        ["C", "Vốn TPCP theo quyết định 171/2006/QĐ-TTg", "3250000", "1113505", "184597", "1298102"],
        ["D", "Các dự án cấp bách bổ sung", "200000", "16153", "3500", "19653"],
        ["E", "Các dự án thuỷ lợi ĐB Sông Hồng", "400000", "18908", "3800", "22708"],
        ["", "Tổng vốn TPCP (C+D+E)", "3850000", "1148566", "191897", "1340463"],
    ]
    
    for r in rows:
        idx, name, plan, actual5, est_m6, est_6t = r
        # 1. Plan
        val = normalize_number(plan)
        if val:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 12, "period_type": "Annual"},
                "geo_context": {"geo_level": "National", "location_name": "Bộ NN&PTNT"},
                "item_context": {"sector": "Investment", "commodity": name},
                "metric_context": {"attribute": "Investment_Value", "value": val, "unit": "million_VND", "data_type": "Plan"},
                "metadata": metadata
            })
        # 2. Month 6
        val = normalize_number(est_m6)
        if val:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 6, "period_type": "Monthly"},
                "geo_context": {"geo_level": "National", "location_name": "Bộ NN&PTNT"},
                "item_context": {"sector": "Investment", "commodity": name},
                "metric_context": {"attribute": "Investment_Value", "value": val, "unit": "million_VND", "data_type": "Estimated"},
                "metadata": metadata
            })
        # 3. Cumulative 6 months
        val = normalize_number(est_6t)
        if val:
            records.append({
                "record_id": generate_id(),
                "time_context": {"year": 2009, "month": 6, "period_type": "Cumulative"},
                "geo_context": {"geo_level": "National", "location_name": "Bộ NN&PTNT"},
                "item_context": {"sector": "Investment", "commodity": name},
                "metric_context": {"attribute": "Investment_Value", "value": val, "unit": "million_VND", "data_type": "Estimated"},
                "metadata": metadata
            })
            
    return {"metadata": metadata, "records": records}


if __name__ == "__main__":
    out_dir = "/media/duongn/New Volume/UIT/aThacSy/Data Mining/2. Data Pre-processing/vn_agri_dts/dataset/extract_llm_v2/extracted_data/2009/06"
    os.makedirs(out_dir, exist_ok=True)
    save_json(parse_pl8a_06(), os.path.join(out_dir, "2009_06_PHULUC_T06_2009_PL8a.json"))
    save_json(parse_pl8b_06(), os.path.join(out_dir, "2009_06_PHULUC_T06_2009_PL8b.json"))
    save_json(parse_pl9_06(), os.path.join(out_dir, "2009_06_PHULUC_T06_2009_PL9.json"))
    print("FINISHED EXAUSTIVE EXTRACTION FOR PL8a, PL8b, PL9.")
