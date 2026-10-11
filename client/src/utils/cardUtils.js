const valueOrder = {
    '0': 0, '1': 1, '2': 2, '3': 3,
    '4': 4, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9, '10': 10,
    'J': 11, 'Q': 12, 'K': 13
}

const suitOrder = {
    'Diamonds': 1, 'Clubs': 2,
    'Hearts': 3, 'Spades': 4
}

const cardValues = {
    '0': 0, '1': 1, '2': 2, '3': 3,
    '4': 4, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10
}

export function getCardValue(value) {
    return cardValues[value]
}

export function sortCards(cards) {
    return cards.sort((a, b) => {
        if (valueOrder[a.value] === valueOrder[b.value]) {
            return suitOrder[a.suit] - suitOrder[b.suit]
        }
        return valueOrder[a.value] - valueOrder[b.value]
    })
}

export function calculateHandValue(cards) {
    return cards.reduce((sum, card) => sum + getCardValue(card.value), 0)
}