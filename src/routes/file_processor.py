from flask import Blueprint, request, jsonify
import os
import re
import json
from werkzeug.utils import secure_filename
from pypdf import PdfReader # User's version uses pypdf

file_processor_bp = Blueprint('file_processor', __name__)

# Configure upload settings - User's version
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'uploads'))
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# --- Pre-compiled Regex Patterns ---
# Vessel name patterns
COMPILED_VESSEL_PATTERNS = [
    re.compile(r'vessel\s*name[:\s]+([A-Za-z0-9\s]+)', re.IGNORECASE),
    re.compile(r'ship\s*name[:\s]+([A-Za-z0-9\s]+)', re.IGNORECASE),
    re.compile(r'mv\s+([A-Za-z0-9\s]+)', re.IGNORECASE),
    re.compile(r'm/v\s+([A-Za-z0-9\s]+)', re.IGNORECASE),
    re.compile(r'vessel[:\s]+([A-Za-z0-9\s]+)', re.IGNORECASE)
]
# Vessel type patterns
COMPILED_VESSEL_TYPE_PATTERNS = [
    re.compile(r'vessel\s*type[:\s]+([A-Za-z\s-]+)', re.IGNORECASE),
    re.compile(r'ship\s*type[:\s]+([A-Za-z\s-]+)', re.IGNORECASE),
    re.compile(r'type[:\s]+(auto\s*carrier|roro|ro-ro|container|multi-purpose)', re.IGNORECASE),
]
# Port patterns
COMPILED_PORT_PATTERNS = [
    re.compile(r'port[:\s]+([A-Za-z\s,]+)', re.IGNORECASE), # Added comma for "Brunswick, GA"
    re.compile(r'destination[:\s]+([A-Za-z\s,]+)', re.IGNORECASE),
    re.compile(r'colonel\s*island', re.IGNORECASE),
    re.compile(r'brunswick,\s*ga', re.IGNORECASE), # More specific
    re.compile(r'brunswick', re.IGNORECASE),
    re.compile(r'savannah', re.IGNORECASE),
    re.compile(r'charleston', re.IGNORECASE)
]
# Date patterns
COMPILED_DATE_PATTERNS = [
    re.compile(r'(\d{4}-\d{2}-\d{2})'),
    re.compile(r'(\d{1,2}/\d{1,2}/\d{4})'), # MM/DD/YYYY or M/D/YYYY
    re.compile(r'(\d{1,2}-\d{1,2}-\d{4})'), # MM-DD-YYYY or M-D-YYYY
    re.compile(r'date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', re.IGNORECASE) # More flexible date after "date:"
]
# Company patterns
COMPILED_COMPANY_PATTERNS = [
    re.compile(r'stevedoring[:\s]+([A-Za-z\s.&]+)', re.IGNORECASE), # Added . &
    re.compile(r'company[:\s]+([A-Za-z\s.&]+)', re.IGNORECASE),
    re.compile(r'aps\s*stevedoring', re.IGNORECASE),
    re.compile(r'ssa\s*marine', re.IGNORECASE),
    re.compile(r'ports\s*america', re.IGNORECASE)
]
# Vehicle count patterns
COMPILED_TOTAL_AUTOMOBILES_DISCHARGE_PATTERNS = [
    re.compile(r'total\s*automobiles\s*to\s*discharge[:\s]+(\d+)', re.IGNORECASE),
    re.compile(r'total\s*vehicles?[:\s]+(\d+)', re.IGNORECASE), # General, might be overridden if specific above not found
    re.compile(r'automobiles?[:\s]+(\d+)', re.IGNORECASE),
    re.compile(r'cars?[:\s]+(\d+)', re.IGNORECASE)
]
# Heavy equipment patterns
COMPILED_HEAVY_EQUIPMENT_DISCHARGE_PATTERNS = [
    re.compile(r'heavy\s*equipment\s*to\s*discharge[:\s]+(\d+)', re.IGNORECASE),
    re.compile(r'heavy\s*equipment[:\s]+(\d+)', re.IGNORECASE),
    re.compile(r'hh[:\s]+(\d+)', re.IGNORECASE),
    re.compile(r'high\s*&\s*heavy[:\s]+(\d+)', re.IGNORECASE)
]
# Brand-specific patterns map
COMPILED_BRAND_PATTERNS_MAP = {
    'mbCount': re.compile(r'mercedes[-\s]*benz\s*\(MB\)[:\s]+(\d+)|mb[:\s]+(\d+)', re.IGNORECASE),
    'bmwCount': re.compile(r'bmw[:\s]+(\d+)', re.IGNORECASE),
    'lrCount': re.compile(r'land\s*rover\s*\(LR\)[:\s]+(\d+)|lr[:\s]+(\d+)', re.IGNORECASE),
    'rrCount': re.compile(r'rolls[-\s]*royce\s*\(RR\)[:\s]+(\d+)|rr[:\s]+(\d+)', re.IGNORECASE),
    'audi': re.compile(r'audi[:\s]+(\d+)', re.IGNORECASE), # Changed key to match form/js
    'porsche': re.compile(r'porsche[:\s]+(\d+)', re.IGNORECASE),
    'mini': re.compile(r'mini[:\s]+(\d+)', re.IGNORECASE),
    'jaguar': re.compile(r'jaguar[:\s]+(\d+)', re.IGNORECASE),
}
# Operation type patterns
COMPILED_OPERATION_TYPE_PATTERNS = [
    re.compile(r'operation\s*type[:\s]+(discharge\s*\+\s*loading|discharge\s*only|loading\s*only)', re.IGNORECASE),
    re.compile(r'(discharge\s*\+\s*loading|discharge\s*only|loading\s*only)', re.IGNORECASE) # More general
]
# Team assignment section regexes
RE_AUTO_OPS_TEAM_SECTION = re.compile(r'Auto Operations Team:([\s\S]*?)(?=High & Heavy Team:|CARGO CONFIGURATION|OPERATIONAL PARAMETERS|STEVEDORE TEAM ASSIGNMENTS|$)', re.IGNORECASE)
RE_HEAVY_OPS_TEAM_SECTION = re.compile(r'High & Heavy Team:([\s\S]*?)(?=CARGO CONFIGURATION|OPERATIONAL PARAMETERS|STEVEDORE TEAM ASSIGNMENTS|$)', re.IGNORECASE)
RE_LEAD_SUPERVISOR = re.compile(r'Lead Supervisor[:\s]+([A-Za-z\s]+)', re.IGNORECASE)
RE_ASSISTANT_SUPERVISOR = re.compile(r'Assistant Supervisor[:\s]+([A-Za-z\s]+)', re.IGNORECASE)
# Operation Manager patterns
COMPILED_OPERATION_MANAGER_PATTERNS = [
    re.compile(r'operation\s*manager[:\s]+([A-Za-z\s]+)', re.IGNORECASE),
    re.compile(r'manager[:\s]+([A-Za-z\s]+)', re.IGNORECASE),
    re.compile(r'john\s+smith', re.IGNORECASE),
]
# Berth location patterns
COMPILED_BERTH_LOCATION_PATTERNS = [
    re.compile(r'berth\s*location[:\s]+(Berth\s*[1-3])', re.IGNORECASE),
    re.compile(r'berth[:\s]+(Berth\s*[1-3])', re.IGNORECASE),
    re.compile(r'berth[:\s]+([1-3])', re.IGNORECASE), # For just number
]
# Loading target patterns
RE_BRV_TARGET = re.compile(r'BRV\s*Loading\s*Target[:\s]+(\d+)', re.IGNORECASE)
RE_ZEE_TARGET = re.compile(r'ZEE\s*Loading\s*Target[:\s]+(\d+)', re.IGNORECASE)
RE_SOU_TARGET = re.compile(r'SOU\s*Loading\s*Target[:\s]+(\d+)', re.IGNORECASE)
# Other Operational Parameters
COMPILED_EXPECTED_RATE_PATTERNS = [re.compile(r'Expected\s*Rate[:\s]+(\d+(?:\.\d)?)\s*cars/hour', re.IGNORECASE), re.compile(r'Expected\s*Rate[:\s]+(\d+(?:\.\d)?)', re.IGNORECASE)]
COMPILED_TOTAL_DRIVERS_PATTERNS = [re.compile(r'Total\s*Drivers[:\s]+(\d+)', re.IGNORECASE)]
COMPILED_SHIFT_START_PATTERNS = [re.compile(r'Shift\s*Start\s*Time[:\s]+(\d{1,2}:\d{2}(?:\s*[AP]M)?)', re.IGNORECASE)]
COMPILED_SHIFT_END_PATTERNS = [re.compile(r'Shift\s*End\s*Time[:\s]+(\d{1,2}:\d{2}(?:\s*[AP]M)?)', re.IGNORECASE)]
COMPILED_BREAK_DURATION_PATTERNS = [re.compile(r'Break\s*Duration[:\s]+(\d+)\s*minutes', re.IGNORECASE), re.compile(r'Break\s*Duration[:\s]+(\d+)', re.IGNORECASE)]
COMPILED_ELECTRIC_VEHICLES_PATTERNS = [re.compile(r'Electric\s*Vehicles[:\s]+(\d+)', re.IGNORECASE)]
COMPILED_STATIC_CARGO_PATTERNS = [re.compile(r'Static\s*Cargo\s*Units[:\s]+(\d+)', re.IGNORECASE)]
COMPILED_CARGO_BRAND_TYPE_PATTERNS = [re.compile(r'Cargo\s*Brand/Type[:\s]+([A-Za-z0-9\s-]+)', re.IGNORECASE)]
# Zone patterns
RE_ZONE_A_VEHICLES = re.compile(r'Zone\s*A\s*-\s*Vehicles[:\s]+(\d+)', re.IGNORECASE)
RE_ZONE_A_DESC = re.compile(r'Zone\s*A\s*-\s*Description[:\s]+(.+)', re.IGNORECASE)
RE_ZONE_B_VEHICLES = re.compile(r'Zone\s*B\s*-\s*Vehicles[:\s]+(\d+)', re.IGNORECASE)
RE_ZONE_B_DESC = re.compile(r'Zone\s*B\s*-\s*Description[:\s]+(.+)', re.IGNORECASE)
RE_ZONE_C_VEHICLES = re.compile(r'Zone\s*C\s*-\s*Vehicles[:\s]+(\d+)', re.IGNORECASE)
RE_ZONE_C_DESC = re.compile(r'Zone\s*C\s*-\s*Description[:\s]+(.+)', re.IGNORECASE)
# TICO Transportation
COMPILED_NUM_VANS_PATTERNS = [re.compile(r'Number\s*of\s*Vans[:\s]+(\d+)', re.IGNORECASE)]
COMPILED_NUM_STATION_WAGONS_PATTERNS = [re.compile(r'Number\s*of\s*Station\s*Wagons[:\s]+(\d+)', re.IGNORECASE)]
# Specific Van/Wagon IDs
COMPILED_VAN_ID_PATTERNS_SPECIFIC = [re.compile(rf'Van\s*{i}\s*ID[:\s]+([A-Za-z0-9]+)', re.IGNORECASE) for i in range(1, 16)]
COMPILED_WAGON_ID_PATTERNS_SPECIFIC = [re.compile(rf'Station\s*Wagon\s*{i}\s*ID[:\s]+([A-Za-z0-9]+)', re.IGNORECASE) for i in range(1, 16)]
# --- End of Pre-compiled Regex Patterns ---

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file. Returns (text, error_message)."""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
        if not text.strip():
            return None, "No text could be extracted from PDF or PDF is empty."
        return text, None
    except Exception as e:
        return None, f"Error reading PDF: {str(e)}"

def extract_data_from_csv(file_path):
    """Extract data from CSV file. Returns (text, error_message)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        if not text.strip():
            return None, "CSV file is empty or contains only whitespace."
        return text, None
    except Exception as e:
        return None, f"Error reading CSV file: {str(e)}"

def _search_patterns(patterns, text):
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None

def parse_maritime_data(text):
    data = {}

    data['vesselName'] = _search_patterns(COMPILED_VESSEL_PATTERNS, text)

    vessel_type_str = _search_patterns(COMPILED_VESSEL_TYPE_PATTERNS, text)
    if vessel_type_str:
        vessel_type_lower = vessel_type_str.lower()
        if 'auto' in vessel_type_lower or 'car' in vessel_type_lower: data['vesselType'] = 'Auto Carrier'
        elif 'roro' in vessel_type_lower or 'ro-ro' in vessel_type_lower: data['vesselType'] = 'RoRo Vessel'
        elif 'container' in vessel_type_lower: data['vesselType'] = 'Container Ship'
        elif 'multi' in vessel_type_lower: data['vesselType'] = 'Multi-Purpose'
        else: data['vesselType'] = vessel_type_str # Fallback to exact match if not standard

    port_match_val = _search_patterns(COMPILED_PORT_PATTERNS, text)
    if port_match_val:
        if 'colonel' in port_match_val.lower(): data['port'] = 'Colonel Island'
        elif 'brunswick, ga' in port_match_val.lower(): data['port'] = 'Brunswick, GA'
        else: data['port'] = port_match_val

    date_str = _search_patterns(COMPILED_DATE_PATTERNS, text)
    if date_str:
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                 year = parts[2] if len(parts[2]) == 4 else '20' + parts[2] # Handle YY and YYYY
                 data['operationDate'] = f"{year}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
        elif '-' in date_str:
            parts = date_str.split('-')
            if len(parts) == 3:
                year = parts[0] if len(parts[0]) == 4 else parts[2] # YYYY-MM-DD or MM-DD-YYYY
                year_val = year if len(year) == 4 else '20' + year
                if len(parts[0])==4 : #YYYY-MM-DD
                     data['operationDate'] = f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                else: #MM-DD-YYYY
                     data['operationDate'] = f"{year_val}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"


    company_match_val = _search_patterns(COMPILED_COMPANY_PATTERNS, text)
    if company_match_val:
        if 'aps' in company_match_val.lower(): data['company'] = 'APS Stevedoring'
        elif 'ssa' in company_match_val.lower(): data['company'] = 'SSA Marine'
        elif 'ports' in company_match_val.lower(): data['company'] = 'Ports America'
        else: data['company'] = company_match_val

    val = _search_patterns(COMPILED_TOTAL_AUTOMOBILES_DISCHARGE_PATTERNS, text)
    if val: data['totalAutomobilesDischarge'] = int(val)

    val = _search_patterns(COMPILED_HEAVY_EQUIPMENT_DISCHARGE_PATTERNS, text)
    if val: data['heavyEquipmentDischarge'] = int(val)

    for key, pattern in COMPILED_BRAND_PATTERNS_MAP.items():
        match = pattern.search(text)
        if match:
            count_str = next((g for g in match.groups() if g and g.isdigit()), None)
            if count_str:
                data[key] = int(count_str) # Keys are already correct: mbCount, bmwCount, audi etc.

    op_type_str = _search_patterns(COMPILED_OPERATION_TYPE_PATTERNS, text)
    if op_type_str:
        op_type_lower = op_type_str.lower()
        if 'discharge' in op_type_lower and 'loading' in op_type_lower: data['operationType'] = 'Discharge + Loading'
        elif 'discharge' in op_type_lower: data['operationType'] = 'Discharge Only'
        elif 'loading' in op_type_lower: data['operationType'] = 'Loading Only'
        else: data['operationType'] = op_type_str


    auto_ops_text_match = RE_AUTO_OPS_TEAM_SECTION.search(text)
    if auto_ops_text_match:
        auto_ops_text = auto_ops_text_match.group(1)
        data['autoOperationsLead'] = _search_patterns([RE_LEAD_SUPERVISOR], auto_ops_text)
        data['autoOperationsAssistant'] = _search_patterns([RE_ASSISTANT_SUPERVISOR], auto_ops_text)

    heavy_ops_text_match = RE_HEAVY_OPS_TEAM_SECTION.search(text)
    if heavy_ops_text_match:
        heavy_ops_text = heavy_ops_text_match.group(1)
        data['heavyHeavyLead'] = _search_patterns([RE_LEAD_SUPERVISOR], heavy_ops_text)
        data['heavyHeavyAssistant'] = _search_patterns([RE_ASSISTANT_SUPERVISOR], heavy_ops_text)

    data['operationManager'] = _search_patterns(COMPILED_OPERATION_MANAGER_PATTERNS, text)
    
    berth_val = _search_patterns(COMPILED_BERTH_LOCATION_PATTERNS, text)
    if berth_val:
        if berth_val in ['1','2','3']: data['berthLocation'] = f'Berth {berth_val}'
        else: data['berthLocation'] = berth_val # Assumes "Berth X" format if not just number

    data['expectedRate'] = _search_patterns(COMPILED_EXPECTED_RATE_PATTERNS, text)
    data['totalDrivers'] = _search_patterns(COMPILED_TOTAL_DRIVERS_PATTERNS, text)
    data['shiftStart'] = _search_patterns(COMPILED_SHIFT_START_PATTERNS, text)
    data['shiftEnd'] = _search_patterns(COMPILED_SHIFT_END_PATTERNS, text)
    data['breakDuration'] = _search_patterns(COMPILED_BREAK_DURATION_PATTERNS, text)
    data['electricVehicles'] = _search_patterns(COMPILED_ELECTRIC_VEHICLES_PATTERNS, text)
    data['staticCargo'] = _search_patterns(COMPILED_STATIC_CARGO_PATTERNS, text)
    data['cargoType'] = _search_patterns(COMPILED_CARGO_BRAND_TYPE_PATTERNS, text)

    match = RE_ZONE_A_VEHICLES.search(text)
    if match: data['zoneA'] = match.group(1).strip()
    match = RE_ZONE_A_DESC.search(text)
    if match: data['zoneADescription'] = match.group(1).strip()
    match = RE_ZONE_B_VEHICLES.search(text)
    if match: data['zoneB'] = match.group(1).strip()
    match = RE_ZONE_B_DESC.search(text)
    if match: data['zoneBDescription'] = match.group(1).strip()
    match = RE_ZONE_C_VEHICLES.search(text)
    if match: data['zoneC'] = match.group(1).strip()
    match = RE_ZONE_C_DESC.search(text)
    if match: data['zoneCDescription'] = match.group(1).strip()

    match = RE_BRV_TARGET.search(text)
    if match: data['brvTarget'] = match.group(1).strip()
    match = RE_ZEE_TARGET.search(text)
    if match: data['zeeTarget'] = match.group(1).strip()
    match = RE_SOU_TARGET.search(text)
    if match: data['souTarget'] = match.group(1).strip()

    data['numVans'] = _search_patterns(COMPILED_NUM_VANS_PATTERNS, text)
    data['numStationWagons'] = _search_patterns(COMPILED_NUM_STATION_WAGONS_PATTERNS, text)

    for i, pattern in enumerate(COMPILED_VAN_ID_PATTERNS_SPECIFIC):
        match = pattern.search(text)
        if match:
            data[f'vanId{i+1}'] = match.group(1).strip()

    for i, pattern in enumerate(COMPILED_WAGON_ID_PATTERNS_SPECIFIC):
        match = pattern.search(text)
        if match:
            data[f'wagonId{i+1}'] = match.group(1).strip()

    # Convert numeric fields from string to int/float where appropriate
    for key in ['totalAutomobilesDischarge', 'heavyEquipmentDischarge', 'mbCount', 'bmwCount', 'lrCount', 'rrCount', 'audi', 'porsche', 'mini', 'jaguar',
                'brvTarget', 'zeeTarget', 'souTarget', 'totalDrivers', 'breakDuration', 'electricVehicles', 'staticCargo',
                'zoneA', 'zoneB', 'zoneC', 'numVans', 'numStationWagons']:
        if data.get(key) and isinstance(data[key], str) and data[key].isdigit():
            data[key] = int(data[key])
    if data.get('expectedRate') and isinstance(data['expectedRate'], str):
        try: data['expectedRate'] = float(data['expectedRate'])
        except ValueError: pass # Keep as string if not floatable

    return data

@file_processor_bp.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and return file info"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not supported'}), 400
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'file_path': file_path,
        'file_size': os.path.getsize(file_path)
    })

@file_processor_bp.route('/api/extract', methods=['POST'])
def extract_data():
    """Extract data from uploaded file"""
    data_req = request.get_json()
    file_path = data_req.get('file_path')
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'success': False, 'error': f'File not found at path: {file_path}'}), 404
    
    file_extension = file_path.rsplit('.', 1)[-1].lower()
    text = None
    error_message = None

    try:
        if file_extension == 'pdf':
            text, error_message = extract_text_from_pdf(file_path)
        elif file_extension == 'csv':
            text, error_message = extract_data_from_csv(file_path)
        elif file_extension == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            if not text.strip():
                 error_message = "TXT file is empty or contains only whitespace."
        else:
            return jsonify({'success': False, 'error': 'Unsupported file type. Please use PDF, CSV, or TXT files.'}), 400
        
        if error_message:
            return jsonify({'success': False, 'error': error_message}), 500
        if text is None:
             return jsonify({'success': False, 'error': 'Failed to extract text or file is empty.'}), 500

        extracted_data = parse_maritime_data(text)
        
        return jsonify({
            'success': True,
            'extracted_text': text[:1000] + '...' if len(text) > 1000 else text,
            'parsed_data': extracted_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error processing file: {str(e)}'}), 500
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting uploaded file {file_path}: {e}")

@file_processor_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'maritime-file-processor'})
