from flask import Flask, render_template, session, request, jsonify
import os
import hashlib
import time

app = Flask(__name__)
app.secret_key = "verysecurekeythatwenevergetto"
GAMES = {
    'cyber_strike': {'name': 'Cyber Strike 2077', 'genre': 'FPS', 'rating': 4.8, 'players': 45234},
    'fantasy_quest': {'name': 'Fantasy Quest Online', 'genre': 'MMORPG', 'rating': 4.6, 'players': 89341},
    'racing_legends': {'name': 'Racing Legends', 'genre': 'Racing', 'rating': 4.4, 'players': 23145},
    'space_odyssey': {'name': 'Space Odyssey', 'genre': 'Strategy', 'rating': 4.9, 'players': 12453},
}

STORE_ITEMS = {
    'skin_1': {'name': 'Neon Warrior Skin', 'price': 150, 'category': 'cosmetic'},
    'skin_2': {'name': 'Dragon Knight Armor', 'price': 250, 'category': 'cosmetic'},
    'boost_1': {'name': 'XP Boost (24h)', 'price': 100, 'category': 'boost'},
    'boost_2': {'name': 'Loot Multiplier (48h)', 'price': 175, 'category': 'boost'},
}

PREMIUM_SERVICES = {
    'vip_monthly': {
        'name': 'VIP Monthly Subscription',
        'price': 299,
        'bonus_eligible': True,
        'description': 'Access to exclusive servers and premium content',
        'features': ['No Ads', 'Priority Support', 'Exclusive Skins']
    },
    'game_pass': {
        'name': 'Game Pass Ultimate',
        'price': 450,
        'bonus_eligible': True,
        'description': 'Unlimited access to 200+ premium games',
        'features': ['200+ Games', 'Day-1 Releases', 'Cloud Saves']
    },
    'tournament_entry': {
        'name': 'Premium Tournament Entry',
        'price': 500,
        'bonus_eligible': True,
        'description': 'Entry to monthly championship with prizes',
        'features': ['$10K Prize Pool', 'Exclusive Rewards', 'Pro Player Access']
    },
    'admin_access': {
        'name': 'Developer Console Access',
        'price': 999,
        'bonus_eligible': False,
        'description': str(os.getenv('DYN_FLAG','FlagY{test_flag}')),
        'features': ['Debug Tools', 'Advanced Analytics', 'API Access','Cool Flag']
    }
}

def init_session():
    if 'user' not in session:
        session['user'] = 'Guest_' + hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        session['coins'] = 0
        session['level'] = 1
        session['xp'] = 0
        session['inventory'] = []
        session['used_bonus'] = False
        session['achievements'] = []
        session['last_daily_claim'] = None

@app.route('/')
def index():
    init_session()
    return render_template('index.html', 
                         user=session['user'],
                         coins=session['coins'],
                         level=session['level'],
                         xp=session['xp'])

@app.route('/api/games')
def get_games():
    return jsonify({'games': GAMES})

@app.route('/api/store')
def get_store():
    return jsonify({'items': STORE_ITEMS})

@app.route('/api/leaderboard')
def leaderboard():
    # Fake leaderboard data
    leaders = [
        {'rank': 1, 'user': 'ProGamer_X', 'score': 125430, 'level': 87},
        {'rank': 2, 'user': 'NinjaWarrior', 'score': 118920, 'level': 82},
        {'rank': 3, 'user': 'DragonSlayer99', 'score': 112340, 'level': 79},
        {'rank': 4, 'user': 'EliteSniper', 'score': 98750, 'level': 71},
        {'rank': 5, 'user': session.get('user', 'Guest'), 'score': session.get('xp', 0), 'level': session.get('level', 1)},
    ]
    return jsonify({'leaderboard': leaders})

@app.route('/api/profile')
def profile():
    init_session()
    return jsonify({
        'user': session['user'],
        'coins': session['coins'],
        'level': session['level'],
        'xp': session['xp'],
        'inventory': session['inventory'],
        'achievements': session['achievements'],
        'member_since': '2024-01-15'
    })

@app.route('/api/daily-reward', methods=['POST'])
def daily_reward():
    init_session()
    last_claim = session.get('last_daily_claim')
    current_time = time.time()
    
    if last_claim is not None:
        time_since_last_claim = current_time - last_claim
        hours_since_claim = time_since_last_claim / 3600
        
        if hours_since_claim < 24:
            hours_remaining = 24 - hours_since_claim
            return jsonify({
                'success': False, 
                'message': f'Already claimed today! Come back in {int(hours_remaining)} hours and {int((hours_remaining % 1) * 60)} minutes.'
            })
    
    reward = 50
    session['coins'] += reward
    session['last_daily_claim'] = current_time
    
    return jsonify({
        'success': True, 
        'reward': reward, 
        'new_balance': session['coins']
    })

@app.route('/api/purchase', methods=['POST'])
def purchase():
    init_session()
    data = request.get_json()
    item_id = data.get('item_id')
    
    if item_id not in STORE_ITEMS:
        return jsonify({'success': False, 'message': 'Item not found'})
    
    item = STORE_ITEMS[item_id]
    
    if session['coins'] < item['price']:
        return jsonify({'success': False, 'message': 'Insufficient coins'})
    
    session['coins'] -= item['price']
    session['inventory'].append(item_id)
    
    return jsonify({
        'success': True,
        'message': f"Purchased {item['name']}",
        'new_balance': session['coins']
    })

@app.route('/api/premium/purchase', methods=['POST'])
def purchase_premium():
    init_session()
    data = request.get_json()
    
    cart = data.get('cart', [])
    apply_bonus = data.get('apply_bonus', False)
    
    if apply_bonus and session.get('used_bonus', False):
        return jsonify({'success': False, 'message': 'New user bonus already claimed'})
    
    if not cart:
        return jsonify({'success': False, 'message': 'Cart is empty'})
    
    for item in cart:
        quantity = item.get('quantity', 0)
        
        try:
            if not isinstance(quantity, (int, float)):
                return jsonify({'success': False, 'message': 'Invalid quantity type'})
            if quantity != quantity:
                return jsonify({'success': False, 'message': 'Quantity cannot be NaN'})
            if quantity == float('inf') or quantity == float('-inf'):
                return jsonify({'success': False, 'message': 'Quantity cannot be infinite'})
        except:
            return jsonify({'success': False, 'message': 'Invalid quantity value'})
        
        if quantity <= 0:
            return jsonify({'success': False, 'message': 'Quantity must be greater than zero'})
        if item['service_id'] not in PREMIUM_SERVICES:
            return jsonify({'success': False, 'message': f"Service {item['service_id']} not found"})
    
    bonus_coins = 0
    if apply_bonus:
        for item in cart:
            service = PREMIUM_SERVICES[item['service_id']]
            if service['bonus_eligible']:
                bonus_coins += item['quantity'] * service['price']
    
    total_cost = 0
    for item in cart:
        service = PREMIUM_SERVICES[item['service_id']]
        total_cost += item['quantity'] * service['price']
    
    available_balance = session['coins'] + bonus_coins
    final_balance = available_balance - total_cost
    
    if final_balance < 0:
        return jsonify({
            'success': False,
            'message': f'Insufficient balance. Need {total_cost} coins, you have {session["coins"]} coins' + 
                      (f' (with bonus: {available_balance} coins)' if bonus_coins > 0 else '')
        })
    
    purchased_services = []
    for item in cart:
        service = PREMIUM_SERVICES[item['service_id']]
        purchased_services.append({
            'service': service['name'],
            'description': service['description'],
            'quantity': item['quantity']
        })
    
    session['coins'] = final_balance
    if apply_bonus and bonus_coins > 0:
        session['used_bonus'] = True
    
    return jsonify({
        'success': True,
        'message': 'Premium services activated!',
        'services': purchased_services,
        'new_balance': session['coins'],
        'bonus_applied': bonus_coins
    })

@app.route('/api/achievements')
def achievements():
    all_achievements = [
        {'id': 'first_win', 'name': 'First Victory', 'description': 'Win your first match', 'unlocked': True},
        {'id': 'level_10', 'name': 'Getting Started', 'description': 'Reach level 10', 'unlocked': True},
        {'id': 'collector', 'name': 'Collector', 'description': 'Own 10 items', 'unlocked': False},
        {'id': 'master', 'name': 'Master Player', 'description': 'Reach level 50', 'unlocked': False},
    ]
    return jsonify({'achievements': all_achievements})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

