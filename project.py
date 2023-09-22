import sys
import csv
import random

class Card:
    def __init__(self, face, suit, value): # On initalisation of class
        if face not in ["ace", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "jack", "queen", "king", "joker", "special"]:
            raise ValueError("Card has incorrect face")
        self.face = face

        if suit not in ["spades", "clubs", "diamonds", "hearts", "joker", "special"]:
            raise ValueError("Card has incorrect suit")
        self.suit = suit

        try:
            self.value = int(value)
        except ValueError:
            sys.exit("Could not parse card value")

    def __str__(self): # Return a string of a human readable version of a card
        return f"{self.face} of {self.suit}" # Note the value of a card is ommitted

class Player:
    def __init__(self, facedown, faceup, hand): # On initalisation of class
        self.facedown = facedown
        self.faceup = faceup
        self.faceup.sort(key=lambda card: card.value) # Sort faceups
        self.hand = hand

    def __str__(self): # Make a string of all cards that a player possesses, dev use only. Otherwise use display function
        h = "|"
        for card in self.hand:
            h = h + " " + str(card) + " |"

        fu = "|"
        for card in self.faceup:
            fu = fu + " " + str(card) + " |"

        fd = "|"
        for card in self.facedown:
            fd = fd + " " + str(card) + " |"

        return f"Hand -> {h}\n Face Up -> {fu}\n Face Down -> {fd}"

    # Check current hand/face ups to see if cards can be played
    def check(self, mode, play_card):
        playable_values = [2, 3] # 2 or 3 can be played on anything

        if play_card.value == 9: # On a 9 you must play a lower or equal card
            for i in range(4, 10):
                playable_values.append(i)

        # INSERT CUSTOM RULES HERE

        else: # Otherwise you must play a higher or equal card
            for i in range(play_card.value, 16):
                playable_values.append(i)

        # Checks the cards you can play from your player with the playable cards list
        match mode:
            case "h": # If playing hand, check hand cards
                for card in self.hand:
                    if card.value in playable_values:
                        return playable_values
                return None
            case "u": # If playing face ups, check face ups
                for card in self.faceup:
                    if card.value in playable_values:
                        return playable_values
                return None
            case "d": # If playing face downs, don't check but still return
                return playable_values
            case _: # If I have made a mistake...
                raise ValueError("Please specify mode to check cards before playing")

    # When a player cannot play, pickup pile
    def pickup(self, pile):
        for card in pile: # Iterate over each card
            self.hand.append(card) # And add to hand

    # Before taking a turn, display all cards and, if they can be played, their values
    def display_playable(self, playable_values, mode):
        playable_cards_values = []
        # If playing hand
        if mode == "h":
            h = "|"
            for card in self.hand:
                if card.value in playable_values: # If card is playable
                    h = h + f" {card.value} : {str(card)} |" # Display value next to card
                    playable_cards_values.append(card.value)
                else: # Otherwise
                    h = h + f" X : {str(card)} |" # Display X next to card

            # Display face ups as normal
            fu = "|"
            for card in self.faceup:
                fu = fu + " " + str(card) + " |"

            # Display face downs as normal
            fd = "|"
            for card in self.facedown:
                fd = fd + " " + "X of X" + " |"

            print(f"Hand -> {h}\n Face Up -> {fu}\n Face Down -> {fd}")

        # If playing face ups
        elif mode == "u":
            fu = "|"
            for card in self.faceup:
                if card.value in playable_values: # If card is playable
                    fu = fu + f" {card.value} : {str(card)} |" # Print its value next to the card
                    playable_cards_values.append(card.value)
                else: # Otherwise
                    fu = fu + f" X : {str(card)} |" # Print an X next to the card

            # Display face downs like normal
            fd = "|"
            for card in self.facedown:
                fd = fd + " " + "X of X" + " |"

            print(f"Face Up -> {fu}\n Face Down -> {fd}")

        # If playing face downs
        elif mode == "d":
            i = 1
            fd = "|"
            for card in self.facedown:
                fd = fd + f" {i} : X of X |" # Display number next to face down, no checking if playable
                playable_cards_values.append(i)
                i += 1

            print(f"Face Down -> {fd}")

        else: # If I have made a mistake
            raise ValueError("Please specify mode to display before playing")

        return playable_cards_values

    def play(self, value, mode):
        played_cards = []
        if mode == "h":
            for card in self.hand:
                if card.value == value:
                    played_cards.append(card)
                    self.hand.remove(card)
        elif mode == "u":
            for card in self.faceup:
                if card.value == value:
                    played_cards.append(card)
                    self.faceup.remove(card)
        elif mode == "d":
            played_cards.append(self.facedown[value - 1])
            self.facedown.pop(value - 1)

        return played_cards

    # While there are cards in the deck, draw until you have 3 cards in your hand
    def draw(self, deck):
        while len(self.hand) < 3 and len(deck) > 0:
            r = random.randint(0, len(deck) - 1) # Pick random card
            self.hand.append(deck[r]) # Add random card to hand
            deck.pop(r) # Remove card from deck

        return deck

    def sort(self):
        # Sort the hand based on card values
        self.hand.sort(key=lambda card: card.value)


def main():
    # Ensure correct command line argument counts
    if len(sys.argv) != 3:
        sys.exit("USAGE: python shed.py [NO. PLAYERS] [DECK FILE]")

    # Ensure correct number of players
    try:
        num_players = int(sys.argv[1])
    except ValueError:
        sys.exit("[NO. PLAYERS] must be an integer")
    if num_players not in range(1,7):
        sys.exit("[NO. PLAYERS] must be between 1 and 6 inclusive")
    print(f"Preparing game for {num_players} players...")

    # Ensure command line argument is a csvfile
    try:
        file_name = sys.argv[2].split(".")
    except ValueError:
        sys.exit("Not a CSV file")
    if file_name[1] != "csv":
        sys.exit("Not a CSV file")
    print(f"Loading deck from {sys.argv[2]}...")

    # Load deck from command line argument
    deck = load_deck(sys.argv[2])

    # Assign players cards from deck
    players, deck = load_players(deck, num_players)
    print(f"Assigned {9 * num_players} cards to {num_players} players")

    for i in range(len(players)):
        print(f"Player {i + 1}/{num_players}:\n {str(players[i])}")

    print("Cards remaining in deck:")

    for j in range(len(deck)):
        print(f"| {deck[j]} ", end="")

    print("|")

    play_game(deck, players, num_players)


def play_game(deck, players, num_players):
    round = 0
    winners = []
    pile = []

    while True:
        if len(pile) != 0: # If there is a pile
            top_card = pile[len(pile) - 1] # Find card on top of pile

            play_card = parse_pile(pile) # Find card to play on including special cards

        else: # If there is no pile
            top_card = Card("special", "special", 2)
            play_card = Card("special", "special", 2)

        player_no = round % num_players # Determine which player is going to play next

        if player_no not in winners: # Assuming player has not already won
            players[player_no].sort()

            print(f"Player {player_no} - your turn!")

            if top_card == play_card: # If top card is play card, only show one
                print(f"Card to play on is: {str(play_card)}")
            else: # If top card is NOT play card so show both for consistency
                print(f"Last card played was: {str(top_card)} | Card to play on is: {str(play_card)}")

            mode = set_mode(players, player_no) # Determine which part of a players cards to play from

            playable_values = players[player_no].check(mode, play_card) # Check if any cards can be played, or if face downs return all values

            if playable_values is None: # If cannot play with current mode cards
                print(f"Player {player_no}, you cannot play any of your cards and have picked up the pile")
                players[player_no].pickup(pile) # Pick up pile
                pile = [] # Reset pile
            else: # If can play
                playable_cards_values = players[player_no].display_playable(playable_values, mode) # Display cards to play
                while True:
                    try:
                        value = int(input("Input Value Of Card To Play: "))
                    except ValueError:
                        pass
                    else:
                        if value in playable_cards_values:
                            break

                cards_played = players[player_no].play(value, mode)

                if mode == "d":
                    if cards_played[0].value in playable_values:
                        pile.append(cards_played[0])
                        if cards_played[0].value == 8: # 8 Skips next person, this also covers multiple skips
                            round += 1
                        elif cards_played[0].value == 10: # 10 Burns pile and gives another turn
                            pile = []
                            round -= 1
                    else:
                        pile.append(cards_played[0])
                        print(f"Player {player_no}, your face down could not be played and you have picked up the pile")
                        players[player_no].pickup(pile) # Pick up pile
                        pile = [] # Reset pile
                else:
                    for card in cards_played:
                        pile.append(card)
                        if card.value == 8: # 8 Skips next person, this also covers multiple skips
                            round += 1

                    if value == 10: # 10 Burns pile and gives another turn
                            pile = []
                            round -= 1

                if len(deck) != 0:
                    deck = players[player_no].draw(deck)

                if mode == "d" and len(players[player_no].facedown) == 0:
                    winners = win(player_no, winners, num_players)

        if check_4_burn(pile):
            pile = []

        round += 1 # Move onto next player

# Check pile for card to be played on
def parse_pile(pile):
    i = 1
    while True: # Loop down the cards in pile
        if pile[len(pile) - i].value == 3: # 3s are invisible and can be played on anything
            i += 1
        # INSERT CUSTOM RULES HERE
        else: # If card is not special, return it
            return pile[len(pile) - i]


# Determine where a player will play cards from
def set_mode(players, player_no):
        if len(players[player_no].hand) > 0:
            return "h"
        elif len(players[player_no].faceup) > 0:
            return "u"
        elif len(players[player_no].facedown) > 0:
            return "d"
        else:
            raise ValueError("Could Not Assign Mode")

# If 4 cards of the same value are played simultaniously, burn the pile
def check_4_burn(pile):
    if len(pile) >= 4:
        i = 1
        value_to_check = pile[len(pile) - i].value # Find value of top card to check for
        while i <= 4:
            i += 1
            if pile[len(pile) - i] != value_to_check: # If values are not equal
                return False

        return True # If 4 consecutive valeus are equal
    return False # If there are not 4 cards in a pile


# Determine winners
def win(player_no, winners, num_players):
    winners.append(player_no)
    # If only one player remains
    if len(winners) == num_players - 1:
        final_standings(winners)

    # Customise text based on how many people won before
    match len(winners):
        case 1:
            text = "1st!"
        case 2:
            text = "2nd."
        case 3:
            text = "3rd."
        case _:
            text = f"{winners}th..."

    print(f"Congratulations player {player_no}, you came {text}")
    k = input(f"Press any key to continue...")
    return winners

def final_standings(winners): # Output the winners array to show final scores
    for i in range(len(winners)):
        print(f"Position {i + 1}: Player {winners[i]}")

    sys.exit("Thanks for playing! Made by George Newman.")


def load_deck(file_name):
    # Check that the file exists
    try:
        file = open(file_name, "r")
    except FileNotFoundError:
        sys.exit("File does not exist")

    # Prepare to read csv
    reader = csv.DictReader(file)
    deck = []
    cards_loaded = 0

    # Read csv
    for row in reader:
        deck.append(Card(row["face"], row["suit"], row["value"]))
        cards_loaded += 1

    # Check minimum requirements
    if cards_loaded < 54:
       sys.exit("File does not match minimum deck requirements")

    print("54 Base Cards Loaded")
    # print(f"{cards_loaded - 54} Custom Cards Loaded")

    return deck

def load_players(deck, num_players):
    players = []

    # For each player, assign an empty list
    for i in range(num_players):
        hand = []
        facedown = []
        faceup = []

        # For each list, assign a random Card from the deck and hence remove card from the deck
        for j in range(3):
            r = random.randint(0, len(deck) - 1)
            facedown.append(deck[r])
            deck.pop(r)
            r = random.randint(0, len(deck) - 1)
            faceup.append(deck[r])
            deck.pop(r)
            r = random.randint(0, len(deck) - 1)
            hand.append(deck[r])
            deck.pop(r)

        # Append new lists to player list using Player class
        players.append(Player(facedown, faceup, hand))

    return players, deck


if __name__ == "__main__":
    main()
