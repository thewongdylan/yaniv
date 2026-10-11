# yaniv

## Client architecture
```
client/
├── public/
│   └── cards/              # Images of the card faces and backs
├── src/
│   ├── components/         # Reusable UI pieces
│   │   ├── Card.jsx        # Renders a single playing card
│   │   ├── PlayerHand.jsx  # Arranges the user's cards (like a Row/Column layout)
│   │   ├── GameTable.jsx   # The main area showing discard/draw piles
│   │   └── Lobby.jsx       # The screen to create/join a room
│   ├── hooks/
│   │   └── useGameSocket.js # Manages the WebSocket connection to the backend
│   ├── App.jsx             # The main layout that switches between Lobby and GameTable
│   └── main.jsx            # The entry point that mounts the React app
├── index.html              # The static HTML file hosted by GitHub Pages
├── package.json            # Lists your frontend dependencies (React, etc.)
└── vite.config.js          # Configuration for building the static files
```

## Server architecture
```
server/
├── app/
│   ├── game/
│   │   ├── engine.py       # Validates Yaniv rules (e.g., hand value < 5 to call Yaniv)
│   │   ├── deck.py         # Shuffling, dealing, and tracking card states
│   │   └── room_manager.py # Generates 4-letter codes and groups players together
│   ├── database/
│   │   └── db.py           # Handles PostgreSQL connections (e.g., using psycopg2 or asyncpg) to Supabase
│   ├── models.py           # Data structures for Players, Rooms, and Stats
│   └── main.py             # The FastAPI entry point containing the WebSocket routes
├── .env                    # Secret environment variables (database passwords) - NEVER pushed to GitHub
├── .gitignore              # Tells git to ignore .env and cache files
└── requirements.txt        # Tells Render exactly which Python libraries to install
```

## Yaniv game logic
1. Distribute cards, each player to get 5 cards, all start from score 0
2. Turn over top card of deck to become discard pile
3. During player turn, card(s) can be exchanged between hand and deck/discard pile
    
    - The following can be exchanged from hand:
        
        a. Multiple of the same number can be exchanged from hand (min 2, max 5)

        b. Running numbers of the same suit (min 3, max 5), wrapping around not allowed (A/K are upper/lower bounds)
    - Once exchange is complete (pile selected), player turn ends

4. Yaniv can be called once hand total < 7 
    
    - To-do: implement custom yaniv value to be chosen before game start/when creating room
    - To-do: Assaf: Once Yaniv called, check other players' hand totals to determine if other total <= player total -> Assaf (+30)
    - Once Yaniv called, add other players' hand totals to their score

5. Upon round completion, 2s time delay, reset game state, continue
6. Players that reach 200 lose, last player standing wins

    - To-do: implement custom losing value
    - To-do: implement multiples of 50: upon hitting 50/100/150/200, subtract 50 from that player's score

## Exchange logic
- PlayerHand: can select cards (move to selection area)
- PlayerSelection: shows selected cards, upon each select, check if valid selection
    - If valid selection, can exchange, otherwise error
    - Selected cards can be unselected on click (return to hand)