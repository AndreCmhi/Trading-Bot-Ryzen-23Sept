from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_socketio import SocketIO
import state
import engine
import stats_logic
import exchange_logic
from constants import *
from utils import ensure_csrf_token, credentials_valid, get_runtime_settings, load_trades, load_ai_decisions, set_bot_running
import threading
from datetime import datetime

app = Flask(__name__, template_folder=str(TEMPLATE_DIR))
app.secret_key = APP_SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return render_template('index.html', csrf_token=ensure_csrf_token())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        if credentials_valid(user, pw):
            session['authenticated'] = True
            return redirect(url_for('index'))
    return render_template('Login.html')

@app.route('/api/dashboard_snapshot')
def dashboard_snapshot():
    stats = stats_logic.calculate_stats()
    positions = exchange_logic.get_current_positions()
    
    for p in positions:
        symbol = p['symbol']
        leverage = int(float(p.get('leverage', 0) or 1))
        p['roi'] = (float(p['unRealizedProfit']) / (abs(float(p['positionAmt']) * float(p['entryPrice'])) / leverage) * 100) if float(p['entryPrice']) > 0 and leverage > 0 else 0
        p['pnl'] = float(p['unRealizedProfit'])
        # Fetch last 20 klines for sparkline
        try:
            p['sparkline'] = exchange_logic.get_klines(symbol, interval='15m', limit=20)
        except:
            p['sparkline'] = []

    return jsonify({
        'bot_status': {
            'running': state.bot_running,
            'label': 'RUNNING' if state.bot_running else 'STOPPED',
            'reason': state.bot_stop_reason or 'Sistem Berjalan Normal',
            'updated_at': datetime.now().strftime('%H:%M:%S')
        },
        'stats': {
            'total_pnl': stats['total_pnl'],
            'winrate': stats['winrate'],
            'open_trades': len(positions),
            'margin_balance': 0.0,
            'consecutive_losses': 0
        },
        'open_positions': positions,
        'time': datetime.now().strftime('%H:%M:%S')
    })

@app.route('/api/ai_status')
def ai_status():
    decisions = load_ai_decisions()
    return jsonify({
        'provider': 'GROQ / OLLAMA',
        'market_regime': state.market_regime_state['label'],
        'recent_decisions': decisions[-10:]
    })

@app.route('/api/toggle_bot', methods=['POST'])
def toggle_bot():
    payload = request.get_json() or {}
    running = payload.get('running', False)
    set_bot_running(running)
    return jsonify({'status': 'ok', 'bot_running': state.bot_running})

def run_web():
    print(f'>>> DASHBOARD READY AT http://127.0.0.1:{DEFAULT_PORT}')
    socketio.run(app, host=DEFAULT_HOST, port=DEFAULT_PORT, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    state.init_client()
    threading.Thread(target=engine.run_engine_loop, daemon=True).start()
    run_web()