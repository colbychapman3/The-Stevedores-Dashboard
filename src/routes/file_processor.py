from flask import Blueprint, request, jsonify
import os
import re
import json
from werkzeug.utils import secure_filename
import PyPDF2

file_processor_bp = Blueprint('file_processor', __name__)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_data_from_csv(file_path):
    """Extract data from CSV file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except Exception as e:
        return f"Error reading CSV file: {str(e)}"

def parse_maritime_data(text):
    """Parse maritime-specific data from extracted text"""
    data = {}
    
    # Vessel name patterns
    vessel_patterns = [
        r'vessel\s*name[:\s]+([A-Za-z0-9\s]+)',
        r'ship\s*name[:\s]+([A-Za-z0-9\s]+)',
        r'mv\s+([A-Za-z0-9\s]+)',
        r'm/v\s+([A-Za-z0-9\s]+)',
        r'vessel[:\s]+([A-Za-z0-9\s]+)'
    ]
    
    for pattern in vessel_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['vesselName'] = match.group(1).strip()
            break
    
    # Vessel type patterns
    vessel_type_patterns = [
        r'vessel\s*type[:\s]+([A-Za-z\s-]+)',
        r'ship\s*type[:\s]+([A-Za-z\s-]+)',
        r'type[:\s]+(auto\s*carrier|roro|ro-ro|container|multi-purpose)',
    ]
    
    for pattern in vessel_type_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            vessel_type = match.group(1).strip().lower()
            if 'auto' in vessel_type or 'car' in vessel_type:
                data['vesselType'] = 'Auto Carrier'
            elif 'roro' in vessel_type or 'ro-ro' in vessel_type:
                data['vesselType'] = 'RoRo Vessel'
            elif 'container' in vessel_type:
                data['vesselType'] = 'Container Ship'
            elif 'multi' in vessel_type:
                data['vesselType'] = 'Multi-Purpose'
            break
    
    # Port patterns
    port_patterns = [
        r'port[:\s]+([A-Za-z\s]+)',
        r'destination[:\s]+([A-Za-z\s]+)',
        r'berth[:\s]+([A-Za-z0-9\s]+)',
        r'colonel\s*island',
        r'brunswick',
        r'savannah',
        r'charleston'
    ]
    
    for pattern in port_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if 'colonel' in match.group(0).lower():
                data['port'] = 'Colonel Island'
            else:
                data['port'] = match.group(1).strip() if match.groups() else match.group(0).strip()
            break
    
    # Date patterns
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',
        r'(\d{2}/\d{2}/\d{4})',
        r'(\d{2}-\d{2}-\d{4})',
        r'date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            # Convert to YYYY-MM-DD format
            if '/' in date_str:
                parts = date_str.split('/')
                if len(parts[2]) == 4:  # MM/DD/YYYY
                    data['operationDate'] = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
            elif '-' in date_str and len(date_str.split('-')[0]) == 4:  # YYYY-MM-DD
                data['operationDate'] = date_str
            break
    
    # Company patterns
    company_patterns = [
        r'stevedoring[:\s]+([A-Za-z\s]+)',
        r'company[:\s]+([A-Za-z\s]+)',
        r'aps\s*stevedoring',
        r'ssa\s*marine',
        r'ports\s*america'
    ]
    
    for pattern in company_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if 'aps' in match.group(0).lower():
                data['company'] = 'APS Stevedoring'
            elif 'ssa' in match.group(0).lower():
                data['company'] = 'SSA Marine'
            elif 'ports' in match.group(0).lower():
                data['company'] = 'Ports America'
            else:
                data['company'] = match.group(1).strip() if match.groups() else match.group(0).strip()
            break
    
    # Vehicle count patterns
    vehicle_patterns = [
        r'total\s*vehicles?[:\s]+(\d+)',
        r'automobiles?[:\s]+(\d+)',
        r'cars?[:\s]+(\d+)',
        r'units?[:\s]+(\d+)'
    ]
    
    for pattern in vehicle_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['totalAutomobilesDischarge'] = int(match.group(1))
            break
    
    # Heavy equipment patterns
    heavy_equipment_patterns = [
        r'heavy\s*equipment[:\s]+(\d+)',
        r'hh[:\s]+(\d+)',
        r'high\s*&\s*heavy[:\s]+(\d+)'
    ]
    
    for pattern in heavy_equipment_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['heavyEquipmentDischarge'] = int(match.group(1))
            break
    
    # Brand-specific patterns
    brand_patterns = {
        'MB': r'mercedes[-\s]*benz[:\s]+(\d+)|mb[:\s]+(\d+)',
        'BMW': r'bmw[:\s]+(\d+)',
        'LR': r'land\s*rover[:\s]+(\d+)|lr[:\s]+(\d+)',
        'RR': r'rolls[-\s]*royce[:\s]+(\d+)|rr[:\s]+(\d+)'
    }
    
    for brand, pattern in brand_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            count = match.group(1) or match.group(2) if match.groups() else match.group(0)
            if count and count.isdigit():
                data[f'{brand.lower()}Count'] = int(count)
    
    # Operation type patterns
    operation_patterns = [
        r'operation[:\s]+(discharge|loading|discharge\s*\+\s*loading)',
        r'(discharge\s*only|loading\s*only|discharge\s*and\s*loading)'
    ]
    
    for pattern in operation_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            op_type = match.group(1).lower()
            if 'discharge' in op_type and 'loading' in op_type:
                data['operationType'] = 'Discharge + Loading'
            elif 'discharge' in op_type:
                data['operationType'] = 'Discharge Only'
            elif 'loading' in op_type:
                data['operationType'] = 'Loading Only'
            break
    
    # Team assignment patterns
    # Auto Operations Team
    auto_lead_patterns = [
        r'auto\s*operations?\s*team[:\s]*lead\s*supervisor[:\s]+([A-Za-z\s]+)',
        r'auto\s*operations?[:\s]*lead[:\s]+([A-Za-z\s]+)',
        r'lead\s*supervisor[:\s]+([A-Za-z\s]+)',
        r'colby\s+chapman',
        r'auto.*lead.*([A-Za-z\s]+chapman)',
        r'auto.*([A-Za-z\s]*colby[A-Za-z\s]*)'
    ]
    
    for pattern in auto_lead_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if 'colby' in match.group(0).lower():
                data['autoOperationsLead'] = 'Colby Chapman'
            elif match.groups():
                data['autoOperationsLead'] = match.group(1).strip()
            break
    
    auto_assistant_patterns = [
        r'auto\s*operations?\s*team[:\s]*assistant\s*supervisor[:\s]+([A-Za-z\s]+)',
        r'auto\s*operations?[:\s]*assistant[:\s]+([A-Za-z\s]+)',
        r'assistant\s*supervisor[:\s]+([A-Za-z\s]+)',
        r'cole\s+bailey',
        r'auto.*assistant.*([A-Za-z\s]+bailey)',
        r'auto.*([A-Za-z\s]*cole[A-Za-z\s]*)'
    ]
    
    for pattern in auto_assistant_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if 'cole' in match.group(0).lower():
                data['autoOperationsAssistant'] = 'Cole Bailey'
            elif match.groups():
                data['autoOperationsAssistant'] = match.group(1).strip()
            break
    
    # High & Heavy Team
    heavy_lead_patterns = [
        r'high\s*&?\s*heavy\s*team[:\s]*lead\s*supervisor[:\s]+([A-Za-z\s]+)',
        r'high\s*&?\s*heavy[:\s]*lead[:\s]+([A-Za-z\s]+)',
        r'heavy\s*equipment[:\s]*lead[:\s]+([A-Za-z\s]+)',
        r'spencer\s+wilkins',
        r'heavy.*lead.*([A-Za-z\s]+wilkins)',
        r'heavy.*([A-Za-z\s]*spencer[A-Za-z\s]*)'
    ]
    
    for pattern in heavy_lead_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if 'spencer' in match.group(0).lower():
                data['heavyHeavyLead'] = 'Spencer Wilkins'
            elif match.groups():
                data['heavyHeavyLead'] = match.group(1).strip()
            break
    
    heavy_assistant_patterns = [
        r'high\s*&?\s*heavy\s*team[:\s]*assistant\s*supervisor[:\s]+([A-Za-z\s]+)',
        r'high\s*&?\s*heavy[:\s]*assistant[:\s]+([A-Za-z\s]+)',
        r'heavy\s*equipment[:\s]*assistant[:\s]+([A-Za-z\s]+)',
        r'bruce\s+banner',
        r'heavy.*assistant.*([A-Za-z\s]+banner)',
        r'heavy.*([A-Za-z\s]*bruce[A-Za-z\s]*)'
    ]
    
    for pattern in heavy_assistant_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if 'bruce' in match.group(0).lower():
                data['heavyHeavyAssistant'] = 'Bruce Banner'
            elif match.groups():
                data['heavyHeavyAssistant'] = match.group(1).strip()
            break
    
    # Operation Manager
    manager_patterns = [
        r'operation\s*manager[:\s]+([A-Za-z\s]+)',
        r'manager[:\s]+([A-Za-z\s]+)',
        r'your\s*name[:\s]+([A-Za-z\s]+)',
        r'john\s+smith',
        r'supervisor[:\s]+([A-Za-z\s]+)'
    ]
    
    for pattern in manager_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if 'john' in match.group(0).lower():
                data['operationManager'] = 'John Smith'
            elif match.groups():
                data['operationManager'] = match.group(1).strip()
            break
    
    # Berth location patterns
    berth_patterns = [
        r'berth\s*location[:\s]+([A-Za-z0-9\s]+)',
        r'berth[:\s]+([123])',
        r'berth\s*([123])',
        r'assigned.*berth[:\s]*([123])'
    ]
    
    for pattern in berth_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            berth_num = match.group(1).strip()
            if berth_num in ['1', '2', '3']:
                data['berthLocation'] = f'Berth {berth_num}'
            elif 'berth' in berth_num.lower():
                data['berthLocation'] = berth_num
            break
    
    # Extract all additional operational parameters
    
    # Expected Rate patterns
    rate_patterns = [
        r'expected\s*rate[:\s]+(\d+(?:\.\d+)?)',
        r'rate[:\s]+(\d+(?:\.\d+)?)\s*cars?/hour',
        r'(\d+(?:\.\d+)?)\s*cars?/hour',
        r'processing\s*rate[:\s]+(\d+(?:\.\d+)?)'
    ]
    
    for pattern in rate_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['expectedRate'] = match.group(1).strip()
            break
    
    # Total Drivers patterns
    driver_patterns = [
        r'total\s*drivers?[:\s]+(\d+)',
        r'drivers?[:\s]+(\d+)\s*drivers?',
        r'(\d+)\s*drivers?\s*total'
    ]
    
    for pattern in driver_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['totalDrivers'] = match.group(1).strip()
            break
    
    # Shift time patterns
    shift_start_patterns = [
        r'shift\s*start[:\s]+(\d{1,2}:\d{2}(?:\s*[AP]M)?)',
        r'start\s*time[:\s]+(\d{1,2}:\d{2}(?:\s*[AP]M)?)',
        r'(\d{1,2}:\d{2}\s*AM).*shift',
    ]
    
    for pattern in shift_start_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['shiftStart'] = match.group(1).strip()
            break
    
    shift_end_patterns = [
        r'shift\s*end[:\s]+(\d{1,2}:\d{2}(?:\s*[AP]M)?)',
        r'end\s*time[:\s]+(\d{1,2}:\d{2}(?:\s*[AP]M)?)',
        r'(\d{1,2}:\d{2}\s*PM).*shift',
    ]
    
    for pattern in shift_end_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['shiftEnd'] = match.group(1).strip()
            break
    
    # Break duration patterns
    break_patterns = [
        r'break\s*duration[:\s]+(\d+)',
        r'break[:\s]+(\d+)\s*minutes?',
        r'(\d+)\s*minutes?\s*break',
    ]
    
    for pattern in break_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['breakDuration'] = match.group(1).strip()
            break
    
    # Vehicle ID patterns
    van_id_patterns = [
        r'van\s*1\s*id[:\s]+([A-Za-z0-9]+)',
        r'van\s*2\s*id[:\s]+([A-Za-z0-9]+)',
        r'van\s*3\s*id[:\s]+([A-Za-z0-9]+)',
        r'van\s*4\s*id[:\s]+([A-Za-z0-9]+)',
        r'v(\d+)',
    ]
    
    # Extract individual van IDs
    van_ids = []
    for i, pattern in enumerate(van_id_patterns[:4]):  # First 4 patterns for specific vans
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if i == 0:
                data['van1Id'] = match.group(1).strip()
            elif i == 1:
                data['van2Id'] = match.group(1).strip()
            elif i == 2:
                data['van3Id'] = match.group(1).strip()
            elif i == 3:
                data['van4Id'] = match.group(1).strip()
    
    # Generic van ID extraction
    van_id_matches = re.findall(r'v(\d+)', text, re.IGNORECASE)
    if van_id_matches and len(van_id_matches) >= 4:
        data['van1Id'] = f'V{van_id_matches[0]}'
        data['van2Id'] = f'V{van_id_matches[1]}'
        data['van3Id'] = f'V{van_id_matches[2]}'
        data['van4Id'] = f'V{van_id_matches[3]}'
    
    # Zone allocation patterns
    zone_patterns = [
        r'zone\s*a[:\s]+(\d+)',
        r'zone\s*b[:\s]+(\d+)',
        r'zone\s*c[:\s]+(\d+)',
    ]
    
    for i, pattern in enumerate(zone_patterns):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if i == 0:
                data['zoneA'] = match.group(1).strip()
            elif i == 1:
                data['zoneB'] = match.group(1).strip()
            elif i == 2:
                data['zoneC'] = match.group(1).strip()
    
    # Loading target patterns
    loading_patterns = [
        r'brv\s*terminal[:\s]+(\d+)',
        r'zee\s*compound[:\s]+(\d+)',
        r'sou\s*facility[:\s]+(\d+)',
    ]
    
    for i, pattern in enumerate(loading_patterns):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if i == 0:
                data['brvTarget'] = match.group(1).strip()
            elif i == 1:
                data['zeeTarget'] = match.group(1).strip()
            elif i == 2:
                data['souTarget'] = match.group(1).strip()
    
    # Vehicle brand patterns (additional brands)
    brand_patterns = [
        r'audi[:\s]+(\d+)',
        r'porsche[:\s]+(\d+)',
        r'mini[:\s]+(\d+)',
        r'jaguar[:\s]+(\d+)',
    ]
    
    for i, pattern in enumerate(brand_patterns):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if i == 0:
                data['audi'] = match.group(1).strip()
            elif i == 1:
                data['porsche'] = match.group(1).strip()
            elif i == 2:
                data['mini'] = match.group(1).strip()
            elif i == 3:
                data['jaguar'] = match.group(1).strip()

    # Additional cargo fields
    electric_patterns = [
        r'electric\s*vehicles?[:\s]+(\d+)',
        r'ev[:\s]+(\d+)',
        r'(\d+)\s*electric\s*vehicles?'
    ]
    
    for pattern in electric_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['electricVehicles'] = match.group(1).strip()
            break
    
    static_cargo_patterns = [
        r'static\s*cargo[:\s]+(\d+)',
        r'static\s*cargo\s*units?[:\s]+(\d+)',
        r'(\d+)\s*static\s*cargo'
    ]
    
    for pattern in static_cargo_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['staticCargo'] = match.group(1).strip()
            break
    
    cargo_type_patterns = [
        r'cargo\s*brand[/\s]*type[:\s]+([A-Za-z\s\-]+)',
        r'cargo\s*type[:\s]+([A-Za-z\s\-]+)',
        r'brand[/\s]*type[:\s]+([A-Za-z\s\-]+)'
    ]
    
    for pattern in cargo_type_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['cargoType'] = match.group(1).strip()
            break
    
    # Zone description patterns
    zone_desc_patterns = [
        r'zone\s*a[:\s]*description[:\s]+([A-Za-z\s\-]+)',
        r'zone\s*b[:\s]*description[:\s]+([A-Za-z\s\-]+)',
        r'zone\s*c[:\s]*description[:\s]+([A-Za-z\s\-]+)',
    ]
    
    for i, pattern in enumerate(zone_desc_patterns):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if i == 0:
                data['zoneADescription'] = match.group(1).strip()
            elif i == 1:
                data['zoneBDescription'] = match.group(1).strip()
            elif i == 2:
                data['zoneCDescription'] = match.group(1).strip()
    
    # TICO Transportation vehicle counts
    van_count_patterns = [
        r'number\s*of\s*vans[:\s]+(\d+)',
        r'vans?[:\s]+(\d+)',
        r'(\d+)\s*vans?'
    ]
    
    for pattern in van_count_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['numVans'] = match.group(1).strip()
            break
    
    wagon_count_patterns = [
        r'number\s*of\s*station\s*wagons?[:\s]+(\d+)',
        r'station\s*wagons?[:\s]+(\d+)',
        r'(\d+)\s*station\s*wagons?'
    ]
    
    for pattern in wagon_count_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['numStationWagons'] = match.group(1).strip()
            break
    
    # Individual vehicle ID extraction (up to 15 vans and 15 wagons)
    for i in range(1, 16):
        van_id_pattern = rf'van\s*{i}\s*id[:\s]+([A-Za-z0-9]+)'
        match = re.search(van_id_pattern, text, re.IGNORECASE)
        if match:
            data[f'vanId{i}'] = match.group(1).strip()
    
    for i in range(1, 16):
        wagon_id_pattern = rf'(?:station\s*wagon|wagon)\s*{i}\s*id[:\s]+([A-Za-z0-9]+)'
        match = re.search(wagon_id_pattern, text, re.IGNORECASE)
        if match:
            data[f'wagonId{i}'] = match.group(1).strip()

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
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(os.getcwd(), UPLOAD_FOLDER)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_dir, filename)
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
    data = request.get_json()
    file_path = data.get('file_path')
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Determine file type and extract text
    file_extension = file_path.split('.')[-1].lower()
    
    try:
        if file_extension == 'pdf':
            text = extract_text_from_pdf(file_path)
        elif file_extension == 'csv':
            text = extract_data_from_csv(file_path)
        elif file_extension == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            return jsonify({'error': 'Unsupported file type. Please use PDF, CSV, or TXT files.'}), 400
        
        # Parse maritime-specific data
        extracted_data = parse_maritime_data(text)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'extracted_text': text[:1000] + '...' if len(text) > 1000 else text,  # Truncate for preview
            'parsed_data': extracted_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@file_processor_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'maritime-file-processor'})

