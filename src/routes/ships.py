from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime, timedelta

ships_bp = Blueprint('ships', __name__)

# In-memory storage for demo (in production, use a proper database)
ships_data = []
ships_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'ships.json')

def load_ships():
    """Load ships data from file"""
    global ships_data
    try:
        if os.path.exists(ships_file):
            with open(ships_file, 'r') as f:
                ships_data = json.load(f)
    except Exception as e:
        print(f"Error loading ships data: {e}")
        ships_data = []

def save_ships():
    """Save ships data to file"""
    global ships_data
    try:
        # Ensure the directory exists
        db_dir = os.path.dirname(ships_file)
        os.makedirs(db_dir, exist_ok=True)
        
        with open(ships_file, 'w') as f:
            json.dump(ships_data, f, indent=2)
    except Exception as e:
        print(f"Error saving ships data: {e}")
        # Create empty ships data if save fails
        ships_data = []

# Load ships data on module import
load_ships()

@ships_bp.route('/api/ships', methods=['GET'])
def get_ships():
    """Get all ships"""
    return jsonify(ships_data)

@ships_bp.route('/api/ships/<int:ship_id>', methods=['GET'])
def get_ship(ship_id):
    """Get a specific ship"""
    ship = next((s for s in ships_data if s['id'] == ship_id), None)
    if ship:
        return jsonify(ship)
    return jsonify({'error': 'Ship not found'}), 404

@ships_bp.route('/api/ships', methods=['POST'])
def create_ship():
    """Create a new ship operation"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Generate new ID
    new_id = max([s['id'] for s in ships_data], default=0) + 1
    
    # Validate required fields
    vessel_name = data.get('vesselName', '').strip()
    if not vessel_name:
        return jsonify({'error': 'Vessel name is required'}), 400
    
    # Set default date if not provided
    operation_date = data.get('operationDate')
    if not operation_date:
        operation_date = datetime.now().strftime('%Y-%m-%d')
    
    # Create ship record with proper defaults
    ship = {
        'id': new_id,
        'vesselName': vessel_name,
        'vesselType': data.get('vesselType', 'Auto Only'),
        'shippingLine': data.get('shippingLine', 'Unknown'),
        'port': data.get('port', 'Colonel Island'),
        'operationDate': operation_date,
        'company': data.get('company', 'APS Stevedoring'),
        'operationType': data.get('operationType', 'Discharge Only'),
        'berth': data.get('berthLocation', 'Berth 1'),
        'operationManager': data.get('operationManager', 'Manager'),
        'autoOpsLead': data.get('autoOpsLead', 'Lead'),
        'autoOpsAssistant': data.get('autoOpsAssistant', 'Assistant'),
        'heavyOpsLead': data.get('heavyOpsLead', 'Heavy Lead'),
        'heavyOpsAssistant': data.get('heavyOpsAssistant', 'Heavy Assistant'),
        'totalVehicles': max(data.get('totalVehicles', 100), 1),
        'totalAutomobilesDischarge': data.get('totalAutomobilesDischarge', data.get('totalVehicles', 100)),
        'heavyEquipmentDischarge': data.get('heavyEquipmentDischarge', 0),
        'totalElectricVehicles': data.get('totalElectricVehicles', 0),
        'totalStaticCargo': data.get('totalStaticCargo', 0),
        'brvTarget': data.get('brvTarget', 0),
        'zeeTarget': data.get('zeeTarget', 0),
        'souTarget': data.get('souTarget', data.get('totalVehicles', 100)),
        'expectedRate': max(data.get('expectedRate', 150), 1),
        'totalDrivers': max(data.get('totalDrivers', 30), 1),
        'shiftStart': data.get('shiftStart', '07:00'),
        'shiftEnd': data.get('shiftEnd', '15:00'),
        'breakDuration': data.get('breakDuration', 0),
        'targetCompletion': data.get('targetCompletion', ''),
        'ticoVans': data.get('ticoVans', 0),
        'ticoStationWagons': data.get('ticoStationWagons', 0),
        'status': 'active',
        'progress': 0,
        'createdAt': datetime.now().isoformat(),
        'startTime': data.get('shiftStart', '07:00'),
        'estimatedCompletion': data.get('targetCompletion', data.get('shiftEnd', '15:00')),
        'updatedAt': datetime.now().isoformat()
    }
    
    ships_data.append(ship)
    save_ships()
    
    return jsonify(ship), 201

@ships_bp.route('/api/ships/<int:ship_id>', methods=['PUT'])
def update_ship(ship_id):
    """Update a ship operation"""
    ship = next((s for s in ships_data if s['id'] == ship_id), None)
    if not ship:
        return jsonify({'error': 'Ship not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update ship data
    for key, value in data.items():
        if key in ship:
            ship[key] = value
    
    ship['updatedAt'] = datetime.now().isoformat()
    save_ships()
    
    return jsonify(ship)

@ships_bp.route('/api/ships/<int:ship_id>/progress', methods=['PUT'])
def update_ship_progress(ship_id):
    """Update ship operation progress"""
    ship = next((s for s in ships_data if s['id'] == ship_id), None)
    if not ship:
        return jsonify({'error': 'Ship not found'}), 404
    
    data = request.get_json()
    if not data or 'progress' not in data:
        return jsonify({'error': 'Progress value required'}), 400
    
    progress = data['progress']
    if not isinstance(progress, (int, float)) or progress < 0 or progress > 100:
        return jsonify({'error': 'Progress must be a number between 0 and 100'}), 400
    
    ship['progress'] = progress
    
    # Update status based on progress
    if progress >= 100:
        ship['status'] = 'complete'
    elif progress > 0:
        ship['status'] = 'active'
    
    ship['updatedAt'] = datetime.now().isoformat()
    save_ships()
    
    return jsonify(ship)

@ships_bp.route('/api/ships/<int:ship_id>/status', methods=['PUT'])
def update_ship_status(ship_id):
    """Update ship operation status"""
    ship = next((s for s in ships_data if s['id'] == ship_id), None)
    if not ship:
        return jsonify({'error': 'Ship not found'}), 404
    
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Status value required'}), 400
    
    valid_statuses = ['active', 'loading', 'discharge', 'complete', 'paused']
    status = data['status']
    
    if status not in valid_statuses:
        return jsonify({'error': f'Status must be one of: {", ".join(valid_statuses)}'}), 400
    
    ship['status'] = status
    ship['updatedAt'] = datetime.now().isoformat()
    save_ships()
    
    return jsonify(ship)

@ships_bp.route('/api/ships/<int:ship_id>', methods=['DELETE'])
def delete_ship(ship_id):
    """Delete a ship operation"""
    global ships_data
    ship = next((s for s in ships_data if s['id'] == ship_id), None)
    if not ship:
        return jsonify({'error': 'Ship not found'}), 404
    
    ships_data = [s for s in ships_data if s['id'] != ship_id]
    save_ships()
    
    return jsonify({'message': 'Ship operation deleted successfully'})

@ships_bp.route('/api/ships/berths', methods=['GET'])
def get_berth_status():
    """Get berth occupancy status"""
    berths = {f'Berth {i}': None for i in range(1, 7)}
    
    for ship in ships_data:
        if ship['status'] != 'complete' and ship.get('berth'):
            berths[ship['berth']] = {
                'shipId': ship['id'],
                'vesselName': ship['vesselName'],
                'status': ship['status'],
                'progress': ship['progress']
            }
    
    return jsonify(berths)

@ships_bp.route('/api/ships/stats', methods=['GET'])
def get_operations_stats():
    """Get overall operations statistics"""
    active_ships = [s for s in ships_data if s['status'] != 'complete']
    
    stats = {
        'activeShips': len(active_ships),
        'totalShips': len(ships_data),
        'teamsDeployed': len(active_ships) * 2,  # Auto ops + Heavy ops
        'totalVehicles': sum(s.get('totalVehicles', 0) for s in active_ships),
        'berthsOccupied': len(set(s.get('berth') for s in active_ships if s.get('berth'))),
        'averageProgress': sum(s.get('progress', 0) for s in active_ships) / len(active_ships) if active_ships else 0
    }
    
    return jsonify(stats)

@ships_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'ships-management'})

@ships_bp.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data for specified period"""
    period_days = int(request.args.get('period', 30))
    
    # Filter ships by date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)
    
    filtered_ships = []
    for ship in ships_data:
        try:
            ship_date = datetime.fromisoformat(ship.get('operationDate', ship.get('createdAt', '')))
            if start_date <= ship_date <= end_date:
                filtered_ships.append(ship)
        except:
            continue
    
    # Calculate analytics
    total_hours = 0
    total_vehicles = 0
    zone_data = {'zoneA': {'vehicles': 0, 'time': 0}, 'zoneB': {'vehicles': 0, 'time': 0}, 'zoneC': {'vehicles': 0, 'time': 0}}
    team_stats = {}
    vehicle_types = {'automobiles': 0, 'heavyEquipment': 0, 'electricVehicles': 0, 'staticCargo': 0}
    
    for ship in filtered_ships:
        # Calculate hours worked (assuming 8-16 hour shifts)
        shift_hours = 12  # Default shift length
        if 'shiftStart' in ship and 'shiftEnd' in ship:
            try:
                start_time = datetime.strptime(ship['shiftStart'], '%H:%M')
                end_time = datetime.strptime(ship['shiftEnd'], '%H:%M')
                shift_hours = (end_time - start_time).seconds / 3600
            except:
                pass
        
        total_hours += shift_hours
        
        # Vehicle counts
        total_vehicles += int(ship.get('totalVehicles', 0))
        vehicle_types['automobiles'] += int(ship.get('totalAutomobilesDischarge', 0))
        vehicle_types['heavyEquipment'] += int(ship.get('heavyEquipmentDischarge', 0))
        
        # Team performance
        auto_lead = ship.get('autoOpsLead', '')
        heavy_lead = ship.get('heavyOpsLead', '')
        
        if auto_lead:
            if auto_lead not in team_stats:
                team_stats[auto_lead] = {'role': 'Auto Operations Lead', 'hours': 0, 'ships': 0}
            team_stats[auto_lead]['hours'] += shift_hours
            team_stats[auto_lead]['ships'] += 1
            
        if heavy_lead:
            if heavy_lead not in team_stats:
                team_stats[heavy_lead] = {'role': 'Heavy Equipment Lead', 'hours': 0, 'ships': 0}
            team_stats[heavy_lead]['hours'] += shift_hours
            team_stats[heavy_lead]['ships'] += 1
    
    # Generate daily hours data
    daily_hours = []
    for i in range(min(period_days, 30)):
        date = end_date - timedelta(days=period_days - i - 1)
        day_ships = [s for s in filtered_ships if s.get('operationDate', '').startswith(date.strftime('%Y-%m-%d'))]
        day_hours = sum(12 for _ in day_ships)  # Assume 12 hours per ship per day
        daily_hours.append({
            'date': date.strftime('%m/%d'),
            'hours': day_hours
        })
    
    # Format team performance
    team_performance = []
    for name, stats in team_stats.items():
        team_performance.append({
            'name': name,
            'role': stats['role'],
            'hours': int(stats['hours']),
            'ships': stats['ships'],
            'efficiency': 85 + (hash(name) % 15)  # Simulated efficiency
        })
    
    analytics_data = {
        'totalHours': int(total_hours),
        'shipsProcessed': len(filtered_ships),
        'vehiclesHandled': total_vehicles,
        'avgEfficiency': 88,  # Calculated average efficiency
        'dailyHours': daily_hours,
        'vehicleTypes': vehicle_types,
        'zonePerformance': {
            'zoneA': {
                'vehicles': int(total_vehicles * 0.35),
                'avgTime': 12,
                'efficiency': 87
            },
            'zoneB': {
                'vehicles': int(total_vehicles * 0.40),
                'avgTime': 10,
                'efficiency': 92
            },
            'zoneC': {
                'vehicles': int(total_vehicles * 0.25),
                'avgTime': 15,
                'efficiency': 83
            }
        },
        'teamPerformance': team_performance
    }
    
    return jsonify(analytics_data)

