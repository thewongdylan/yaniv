from app.models import Card, GameState, Player
from app.game.deck import generate_deck

def create_new_game(room_code: str) -> GameState:
    deck = generate_deck()
    first_discard = deck.pop()

    return GameState(
        roomCode=room_code,
        deck=deck,
        discardPile=[first_discard],
        previousDiscard=[first_discard],
        currentTurn=0,
        winner=None,
        gameOver=False
    )

### GAME STATE
def add_player_to_game(game: GameState, username:str) -> GameState:
    if username not in game.players:
        hand = [game.deck.pop() for _ in range(5)]
        game.players[username] = Player(username=username, hand_cards=hand)
    return game

def get_player_order(game: GameState) -> list[str]:
    return [username for username, player in game.players.items() if not player.eliminated]

def get_current_player(game: GameState) -> Player:
    player_usernames = get_player_order(game)
    current_index = game.currentTurn % len(player_usernames)
    current_username = player_usernames[current_index]
    return game.players[current_username]

def advance_turn(game: GameState) -> None:
    player_usernames = get_player_order(game)
    next_index = (game.currentTurn + 1) % len(player_usernames)
    game.currentTurn = next_index

### CHECKS
def cards_in_hand(player: Player) -> list[Card]:
    return player.hand_cards + player.selected_cards

def get_hand_value(cards: list[Card]) -> int:
    value_map = {
        '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
        '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 10, 'Q': 10, 'K': 10, '0': 0
    }
    return sum(value_map[card.value] for card in cards)

def is_valid_yaniv_call(cards: list[Card]) -> bool:
    # TO-DO: custom yaniv threshold
    return get_hand_value(cards) <= 7

def is_players_turn(game: GameState, username: str) -> bool:
    player_usernames = get_player_order(game)
    current_index = game.currentTurn % len(player_usernames)
    return player_usernames[current_index] == username

def is_valid_exchange(cards: list[Card]) -> bool:
    # At least 1, at most 5 cards
    if len(cards) < 1 or len(cards) > 5:
        return False

    # A single card is always valid
    if len(cards) == 1:
        return True

    card_order = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
                  '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                  'J': 11, 'Q': 12, 'K': 13}

    non_jokers = [card for card in cards if card.value != '0']

    # Only jokers selected (no non-jokers)
    if not non_jokers: 
        return True

    # Check same (only need to check non-jokers)
    non_joker_values = {card.value for card in non_jokers}
    is_same = len(non_joker_values) == 1
    if is_same:
        return True

    # Running must have at least 3 cards
    if len(cards) < 3:
        return False

    # Running must have same suit among non-jokers
    non_joker_suits = {card.suit for card in non_jokers}
    is_same_suit = len(non_joker_suits) == 1
    if not is_same_suit:
        return False

    non_joker_positions = [card_order[card.value] for card in non_jokers]
    # Duplicate values selected, cannot make up running numbers
    if len(set(non_joker_positions)) != len(non_joker_positions):
        return False

    # Range of selected cards (run length) cannot be span more than number of selected cards with jokers
    min_position = min(non_joker_positions)
    max_position = max(non_joker_positions)
    min_required_run_length = max_position - min_position + 1
    is_running = min_required_run_length <= len(cards)
    return is_running

def get_legal_discard_indices(discard_cards: list[Card]) -> list[int]:
    # Single discard, always legal
    if len(discard_cards) == 1:
        return [0]

    # Same value, can take any
    non_jokers = [card for card in discard_cards if card.value != '0']
    if non_jokers and len({card.value for card in non_jokers}) == 1:
        return list(range(len(discard_cards)))

    # Running, can only take either end
    if len({card.suit for card in non_jokers}) == 1:
        return [0, len(discard_cards) - 1]

    return []

def get_discard_card_index(discard_cards: list[Card], discard_card_id: str) -> int:
    for index, card in enumerate(discard_cards):
        if card.id == discard_card_id:
            return index
    return None

### ACTIONS
def exchange_cards(game: GameState, player: Player, from_pile: str, discard_card_id: str) -> bool:
    # Check player's selected cards
    if not is_valid_exchange(player.selected_cards):
        return False

    if from_pile == "deck":
        if not game.deck:
            return False
        drawn_card = game.deck.pop()
    elif from_pile == "discard":
        if not game.previousDiscard:
            return False
        discard_index = get_discard_card_index(game.previousDiscard, discard_card_id)
        legal_indices = get_legal_discard_indices(game.previousDiscard)
        if discard_index not in legal_indices:
            return False
        drawn_card = game.previousDiscard.pop(discard_index)
        game.discardPile.remove(drawn_card)
    else:
        return False
    
    player.hand_cards.append(drawn_card)
    new_discard = list(player.selected_cards)
    player.selected_cards.clear()
    game.discardPile.extend(new_discard)
    game.previousDiscard = new_discard
    advance_turn(game)

    return True

def select_card(player: Player, card_id: str) -> bool:
    card = next((card for card in player.hand_cards if card.id == card_id), None)
    if card is None:
        return False

    player.hand_cards.remove(card)
    player.selected_cards.append(card)
    return True

def deselect_card(player: Player, card_id: str) -> bool:
    card = next((card for card in player.selected_cards if card.id == card_id), None)
    if card is None:
        return False

    player.selected_cards.remove(card)
    player.hand_cards.append(card)
    return True

def call_yaniv(game: GameState, player: Player) -> bool:
    player_value = get_hand_value(cards_in_hand(player))
    if player_value > game.yanivThreshold:
        return False

    player.has_called_yaniv = True
    settle_round(game, player)
    return True

def settle_round(game: GameState, called_by: Player) -> None:
    opponents = [player for player in game.players.values() if player.username != called_by.username and not player.eliminated]
    caller_value = get_hand_value(cards_in_hand(called_by))

    assaf = any(get_hand_value(cards_in_hand(opponent)) <= caller_value for opponent in opponents)
    if assaf:
        called_by.score += 30
    else:
        for opponent in opponents:
            opponent_value = get_hand_value(cards_in_hand(opponent))
            opponent.score += opponent_value
    
    for player in game.players.values():
        if player.score >= game.losingScore:
            player.eliminated = True

    active_players = [player for player in game.players.values() if not player.eliminated]
    if len(active_players) == 1:
        game.winner = active_players[0].username
        game.gameOver = True
    else:
        game.roundOver = True

def start_next_round(game: GameState) -> None:
    active_players = [player for player in game.players.values() if not player.eliminated]
    game.deck = generate_deck()
    first_discard = game.deck.pop()
    game.discardPile = [first_discard]
    game.previousDiscard = [first_discard]

    for player in active_players:
        player.hand_cards = [game.deck.pop() for _ in range(5)]
        player.selected_cards.clear()
        player.has_called_yaniv = False

    game.roundNumber += 1
    game.roundOver = False
    game.currentTurn = 0

def process_player_action(game: GameState, username: str, action_data: dict) -> bool:
    if game.gameOver:
        return {"ok": False, "message": "Game is over!"}
    if game.roundOver:
        return {"ok": False, "message": "Round is over!"}
    if username not in game.players:
        return {"ok": False, "message": "Player not in game."}
    if not is_players_turn(game, username):
        return {"ok": False, "message": "Not your turn."}
    
    action = action_data.get("action")
    player = game.players.get(username)

    if action == "SELECT":
        card_id = action_data.get("cardId")
        if not select_card(player, card_id):
            return {
                "ok": False,
                "message": "Card not found in hand",
            }
        return {
            "ok": True,
            "message": f"{username} selected {card_id}",
        }

    if action == "DESELECT":
        card_id = action_data.get("cardId")
        if not deselect_card(player, card_id):
            return {
                "ok": False,
                "message": "Card not found in selected cards",
            }
        return {
            "ok": True,
            "message": f"{username} deselected {card_id}",
        }

    if action == "EXCHANGE":
        if player.selected_cards == []:
            return {
                "ok": False,
                "message": "No cards selected to exchange",
            }
        from_pile = action_data.get("fromPile")
        discard_card_id = action_data.get("discardCardId")
        if not exchange_cards(game, player, from_pile, discard_card_id):
            return {
                "ok": False,
                "message": f"Failed to exchange cards from {from_pile}.",
            }
        return {
            "ok": True,
            "message": f"{username} exchanged cards from {from_pile}.",
        }

    if action == "YANIV":
        if call_yaniv(game, player):
            return {
                "ok": True,
                "message": f"{username} called Yaniv",
            }
        return {
            "ok": False,
            "message": "Invalid Yaniv call",
        }

    return {
        "ok": False,
        "message": "Unknown action",
    }

    