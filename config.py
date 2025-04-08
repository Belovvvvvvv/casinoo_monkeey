import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('7847197165:AAGEzYCC1GmMVoxhM804vPXs5LyNPuneCeU')
CRYPTO_BOT_TOKEN = os.getenv('365885:AAkJPy2Gr5d0sIUAGWm1HokYfpOoGGwnlyD')

GAME_SETTINGS = {
    'bowling': {
        'min_bet': 10,
        'win_multiplier': 3, 
        'win_condition': lambda score: score >= 4
    },
    'darts': {
        'min_bet': 5,
        'win_amount': 5, 
        'win_condition': lambda score: score == 6
    },
    'cube': {
        'min_bet': 1,
        'win_multiplier': 1.6,
        'win_condition': lambda score: score >= 4
    }
} 
