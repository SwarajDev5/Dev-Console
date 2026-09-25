import random
import time
import socket
import os
from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'dev-console-secret-key-2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

active_rooms = {}
AVATAR_COLORS = ['#ef4444', '#3b82f6', '#eab308', '#22c55e', '#a855f7', '#ec4899', '#f97316', '#06b6d4']

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

GAMES_CATALOG = [
    {
        'id': 'dev_goal',
        'title': 'DevGoal!',
        'category': 'PARTY ARCADE',
        'subtitle': '2x Mega 3D Stadium Football',
        'playersText': '1-4 Players',
        'badge': '3D STADIUM',
        'thumbnail': '/assets/images/devgoal_cover.jpg',
        'gameplayGif': '/assets/images/devgoal_cover.jpg',
        'description': '2x Mega 3D Stadium with GLTF miniplayer GLB models, animated running/dashing/knockdown states, realistic sky atmosphere, dynamic pitch markings, waving flags, and 240s match timer.'
    },
    {
        'id': 'spacess',
        'title': 'Spacess',
        'category': 'PARTY ARCADE',
        'subtitle': '2D Cosmic Table Tennis (2-6 Players)',
        'playersText': '2-6 Players (Versus)',
        'badge': 'SPACE MULTIPLAYER',
        'thumbnail': '/assets/images/spacess_cover.jpg',
        'gameplayGif': '/assets/images/spacess_cover.jpg',
        'description': 'Deep black VOID space table tennis featuring Alien Spaceship paddles, 6-player multi-column arenas, big solo spaceship auto-balance for 3 players, and plasma ball rally physics.'
    },
    {
        'id': 'ping_pong',
        'title': 'Ping Pong',
        'category': 'PARTY ARCADE',
        'subtitle': 'Classic Table Tennis (1-4 Players)',
        'playersText': '1-4 Players (Singles / Doubles)',
        'badge': 'MOUSE & CONTROLLER',
        'thumbnail': '/assets/images/pingpong_cover.jpg',
        'gameplayGif': '/assets/images/pingpong_cover.jpg',
        'description': 'Classic Table Tennis inspired by 1 2 3 4 Player Games! Direct PC mouse paddle control, spin deflection, authentic wooden table acoustics, 3D ball loft, and smash bursts.'
    }
]

def generate_room_code():
    while True:
        code = str(random.randint(100, 999))
        if code not in active_rooms:
            return code

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/lan-info')
def lan_info():
    ip = get_local_ip()
    return {
        'ip': ip,
        'port': 5000,
        'url': f"http://{ip}:5000",
        'hostname': socket.gethostname()
    }

@app.route('/ping')
def ping():
    return {'status': 'ok', 'lan_ip': get_local_ip(), 'port': 5000}

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    return send_from_directory(assets_dir, filename)

@socketio.on('create_room')
def handle_create_room():
    code = generate_room_code()
    local_ip = get_local_ip()
    join_room(code)
    active_rooms[code] = {
        'code': code,
        'local_ip': local_ip,
        'screen_sid': request.sid,
        'host_sid': None,
        'host_name': 'Admin',
        'players': {},
        'state': 'connecting_lobby',
        'selected_game': 'dev_goal',
        'score': {'red': 0, 'blue': 0},
        'paused': False,
        'timer_frozen': False,
        'start_time': None
    }
    emit('room_created', {
        'code': code,
        'localIp': local_ip,
        'directUrl': f"http://{local_ip}:5000?code={code}",
        'catalog': GAMES_CATALOG,
        'selectedGame': 'dev_goal'
    })

@socketio.on('join_room_req')
def handle_join_room(data):
    code = str(data.get('code', '')).strip()
    name = data.get('name', 'Player').strip()

    if not name:
        emit('error_msg', 'Please enter your name first!')
        return

    if code not in active_rooms:
        emit('error_msg', 'Invalid Room Code!')
        return

    room = active_rooms[code]
    join_room(code)

    is_host = (len(room['players']) == 0) or (room['host_sid'] is None) or (room['host_sid'] == request.sid)
    if is_host:
        room['host_sid'] = request.sid
        room['host_name'] = name

    color = random.choice(AVATAR_COLORS)
    initial = name[0].upper() if name else 'P'

    room['players'][request.sid] = {
        'id': request.sid,
        'name': name,
        'initial': initial,
        'color': color,
        'team': 'middle',
        'isHost': is_host,
        'moveX': 0,
        'moveY': 0,
        'pass': False,
        'shoot': False,
        'dash': False,
        'shootPower': 0.5
    }

    emit('joined_successfully', {
        'isHost': is_host,
        'roomCode': code,
        'name': name,
        'hostName': room['host_name'],
        'selectedGame': room['selected_game'],
        'catalog': GAMES_CATALOG
    })

    _broadcast_room_update(code)

@socketio.on('join_fast_req')
def handle_join_fast(data):
    name = data.get('name', 'Player').strip()
    if not name:
        emit('error_msg', 'Please enter your name first!')
        return

    available_codes = list(active_rooms.keys())
    if not available_codes:
        emit('error_msg', 'No active room found on TV screen! Please create one first.')
        return

    selected_code = available_codes[0]
    data['code'] = selected_code
    handle_join_room(data)

@socketio.on('admin_goto_game_select')
def handle_admin_goto_game_select():
    for code, room in active_rooms.items():
        if room['host_sid'] == request.sid or room['screen_sid'] == request.sid:
            room['state'] = 'game_select'
            _broadcast_room_update(code)
            break

@socketio.on('admin_back_state')
def handle_admin_back_state():
    for code, room in active_rooms.items():
        if room['host_sid'] == request.sid or room['screen_sid'] == request.sid:
            if room['state'] == 'side_select':
                room['state'] = 'game_select'
            elif room['state'] == 'game_select':
                room['state'] = 'connecting_lobby'
            _broadcast_room_update(code)
            break

@socketio.on('admin_select_game')
def handle_admin_select_game(data):
    game_id = data.get('gameId')
    for code, room in active_rooms.items():
        if room['host_sid'] == request.sid or room['screen_sid'] == request.sid:
            room['selected_game'] = game_id
            _broadcast_room_update(code)
            break

@socketio.on('admin_confirm_game')
def handle_admin_confirm_game():
    for code, room in active_rooms.items():
        if room['host_sid'] == request.sid or room['screen_sid'] == request.sid:
            if room['state'] == 'connecting_lobby':
                room['state'] = 'game_select'
            elif room['state'] == 'game_select':
                room['state'] = 'side_select'
            _broadcast_room_update(code)
            break

@socketio.on('select_team')
def handle_select_team(data):
    direction = data.get('dir')
    for code, room in active_rooms.items():
        if request.sid in room['players']:
            room['players'][request.sid]['team'] = direction
            _broadcast_room_update(code)
            break

@socketio.on('start_game')
def handle_start_game():
    for code, room in active_rooms.items():
        if room['host_sid'] == request.sid or room['screen_sid'] == request.sid:
            room['state'] = 'playing'
            room['score'] = {'red': 0, 'blue': 0}
            room['paused'] = False
            room['timer_frozen'] = False
            room['start_time'] = time.time()
            
            # Count existing team assignments
            red_count = len([p for p in room['players'].values() if p['team'] == 'left'])
            blue_count = len([p for p in room['players'].values() if p['team'] == 'right'])
            
            unassigned = [p for p in room['players'].values() if p['team'] == 'middle']
            random.shuffle(unassigned)
            
            for p in unassigned:
                if red_count <= blue_count:
                    p['team'] = 'left'
                    red_count += 1
                else:
                    p['team'] = 'right'
                    blue_count += 1

            emit('trigger_match_countdown', {}, to=code)
            _broadcast_room_update(code)
            break

@socketio.on('admin_kick_player')
def handle_admin_kick_player(data):
    player_id = data.get('playerId')
    for code, room in active_rooms.items():
        if (room['host_sid'] == request.sid or room['screen_sid'] == request.sid) and player_id in room['players']:
            del room['players'][player_id]
            emit('kicked_from_room', {}, to=player_id)
            _broadcast_room_update(code)
            break

@socketio.on('admin_toggle_pause')
def handle_admin_toggle_pause(data):
    is_paused = data.get('paused', True)
    for code, room in active_rooms.items():
        if room['host_sid'] == request.sid or room['screen_sid'] == request.sid:
            room['paused'] = is_paused
            emit('pause_state_changed', {'paused': is_paused}, to=code)
            break

@socketio.on('admin_setting_action')
def handle_admin_setting_action(data):
    action = data.get('action')
    for code, room in active_rooms.items():
        if room['host_sid'] == request.sid or room['screen_sid'] == request.sid:
            if action == 'leave':
                room['state'] = 'connecting_lobby'
                room['paused'] = False
                room['score'] = {'red': 0, 'blue': 0}
            elif action == 'change_game':
                room['state'] = 'game_select'
                room['paused'] = False
                room['score'] = {'red': 0, 'blue': 0}
            elif action == 'restart':
                room['score'] = {'red': 0, 'blue': 0}
                room['paused'] = False
                room['state'] = 'playing'
                emit('restart_match_signal', {}, to=code)
                emit('trigger_match_countdown', {}, to=code)
            elif action == 'randomize':
                room['score'] = {'red': 0, 'blue': 0}
                room['paused'] = False
                room['state'] = 'playing'
                plist = list(room['players'].values())
                random.shuffle(plist)
                for i, p in enumerate(plist):
                    p['team'] = 'left' if i % 2 == 0 else 'right'
                emit('restart_match_signal', {}, to=code)
                emit('trigger_match_countdown', {}, to=code)
            elif action == 'toggle_freeze_timer':
                room['timer_frozen'] = not room.get('timer_frozen', False)
                emit('timer_freeze_changed', {'frozen': room['timer_frozen']}, to=code)

            _broadcast_room_update(code)
            break

@socketio.on('controller_input')
def handle_controller_input(data):
    for code, room in active_rooms.items():
        if request.sid in room['players']:
            p = room['players'][request.sid]
            p['moveX'] = data.get('moveX', 0)
            p['moveY'] = data.get('moveY', 0)
            p['pass'] = data.get('pass', False)
            p['shoot'] = data.get('shoot', False)
            p['dash'] = data.get('dash', False)
            p['shootPower'] = data.get('shootPower', 0.5)
            p['isChargingShot'] = data.get('isChargingShot', False)
            
            emit('player_move', {
                'id': request.sid,
                'moveX': p['moveX'],
                'moveY': p['moveY'],
                'pass': p['pass'],
                'shoot': p['shoot'],
                'dash': p['dash'],
                'shootPower': p['shootPower'],
                'isChargingShot': p['isChargingShot'],
                'normX': data.get('normX', None),
                'normY': data.get('normY', None),
                'swingForce': data.get('swingForce', 1.0),
                'isTouchDrag': data.get('isTouchDrag', False)
            }, to=room['screen_sid'])
            break

@socketio.on('goal_scored')
def handle_goal_scored(data):
    team = data.get('team')
    for code, room in active_rooms.items():
        if room['screen_sid'] == request.sid:
            if team in room['score']:
                room['score'][team] += 1
            _broadcast_room_update(code)
            break

@socketio.on('match_over_leave')
def handle_match_over_leave():
    for code, room in active_rooms.items():
        if room['screen_sid'] == request.sid or room['host_sid'] == request.sid:
            room['state'] = 'connecting_lobby'
            room['paused'] = False
            room['score'] = {'red': 0, 'blue': 0}
            _broadcast_room_update(code)
            break

@socketio.on('disconnect')
def handle_disconnect():
    for code, room in list(active_rooms.items()):
        if request.sid == room.get('screen_sid') or request.sid == room.get('host_sid'):
            emit('room_closed', {'reason': 'TV Screen or Host Admin disconnected.'}, to=code)
            del active_rooms[code]
            break
        elif request.sid in room['players']:
            del room['players'][request.sid]
            _broadcast_room_update(code)
            break

def _broadcast_room_update(code):
    if code in active_rooms:
        room = active_rooms[code]
        emit('update_players', {
            'players': list(room['players'].values()),
            'hostName': room['host_name'],
            'hostSid': room['host_sid'],
            'state': room['state'],
            'selectedGame': room['selected_game'],
            'score': room['score'],
            'paused': room['paused'],
            'timerFrozen': room.get('timer_frozen', False),
            'localIp': room['local_ip'],
            'directUrl': f"http://{room['local_ip']}:5000?code={code}",
            'catalog': GAMES_CATALOG
        }, to=code)

if __name__ == '__main__':
    print(f"[Dev Console Server] Running on http://0.0.0.0:5000 (Local IP: {get_local_ip()})")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)