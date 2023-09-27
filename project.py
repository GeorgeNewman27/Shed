import sys
import csv
import random

class Card:
    def __init__(self, face, suit, value): # On initalisation of class
        if face not in ["ace", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "jack", "queen", "king", "joker", "rules", "social", "special"]:
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
        self.hand.sort(key=lambda card: card.value)

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
    def check(self, mode, play_card, top_card):
        playable_values = []

        if play_card.value == 9: # On a 9 you must play a lower or equal card
            for i in range(4, 10):
                playable_values.append(i)

        elif play_card.value >= 20 or play_card.value == 7:
            for i in range(4, 16):
                playable_values.append(i)

        else: # Otherwise you must play a higher or equal card
            for i in range(play_card.value, 16):
                playable_values.append(i)

        if top_card.value == 21: # If on rules card
            playable_values = [i for i in playable_values if i not in [2, 3, 7, 20, 21]]
        else:
            playable_values += [2, 3, 7, 20, 21] # 2, 3 and 7 can be played on anything. All above 20 are specials.


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
        cards_to_remove = []
        if mode == "h":
            num_of_value = len([i for i in self.hand if i.value == value])
            if num_of_value > 1:
                num_of_cards = get_number_of_cards(num_of_value, value)
            else:
                num_of_cards = 1

            j = 0

            # Find cards matching critetia
            for card in self.hand:
                if card.value == value and j < num_of_cards:
                    played_cards.append(card) # Add to played cards
                    cards_to_remove.append(card) # Add to cards to remove
                    j += 1

            # Remove the cards from the original hand list
            for card in cards_to_remove:
                self.hand.remove(card)

            # Check to see if hand overflow may apply
            if len(self.hand) == 0:
                cards_to_remove = []
                num_face_up = len([i for i in self.faceup if i.value == value])

                # If there are value matches, get user input for number to play
                if num_face_up > 0:
                    while True:
                        try:
                            num_of_cards = int(input(f"You have {num_face_up} cards of value {value} to play in your face ups to! How many would you like to play? "))
                        except ValueError:
                            print(f"You must input an integer between 0 and {num_face_up}.")
                        else:
                            if 0 <= num_of_cards <= num_face_up:
                                break
                            else:
                                print(f"You can only play between 0 and {num_face_up} cards from your face ups.")

                    j = 0

                    # Find cards matching critetia
                    for card in self.faceup:
                        if card.value == value and j < num_of_cards:
                            played_cards.append(card) # Add to played cards
                            cards_to_remove.append(card) # Add to cards to remove
                            j += 1

                    # Remove the cards from the original hand list
                    for card in cards_to_remove:
                        self.faceup.remove(card)

        elif mode == "u":
            num_of_value = len([i for i in self.faceup if i.value == value])
            if num_of_value > 1:
                num_of_cards = get_number_of_cards(num_of_value, value)
            else:
                num_of_cards = 1

            j = 0

            # Find cards matching critetia
            for card in self.faceup:
                if card.value == value and j < num_of_cards:
                    played_cards.append(card) # Add to played cards
                    cards_to_remove.append(card) # Add to cards to remove
                    j += 1

            # Remove the cards from the original hand list
            for card in cards_to_remove:
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
    if num_players < 4:
        sys.exit("[NO. PLAYERS] must be at least 4")

    deck_count = int((num_players - 1) / 6) + 1

    print(f"Preparing game for {num_players} players with {deck_count} decks...")

    # Ensure command line argument is a csvfile
    try:
        file_name = sys.argv[2].split(".")
    except ValueError:
        sys.exit("Not a CSV file")
    if file_name[1] != "csv":
        sys.exit("Not a CSV file")
    print(f"Loading deck from {sys.argv[2]}...")

    # Load deck from command line argument
    deck = load_deck(sys.argv[2], deck_count)

    # Assign players cards from deck
    players, deck = load_players(deck, num_players)
    #print(f"Assigned {9 * num_players} cards to {num_players} players")

    #for i in range(len(players)):
        #print(f"Player {i}/{num_players - 1}:\n {str(players[i])}")

    #print(f"{len(deck)} cards remaining in deck:")

    #for j in range(len(deck)):
        #print(f"| {deck[j]} ", end="")

    print("|\n")

    play_game(deck, players, num_players)


def play_game(deck, players, num_players):
    play_direction = 1
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

            playable_values = players[player_no].check(mode, play_card, top_card) # Check if any cards can be played, or if face downs return all values

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
                    print(f"Your face down was a {str(cards_played[0])} on a {str(play_card)}.")
                    if cards_played[0].value in playable_values:
                        print(f"Player {player_no}, your face down has been played to the pile")
                        pile.append(cards_played[0])
                        if cards_played[0].value == 8: # 8 Skips next person, this also covers multiple skips
                            round = skip_turn(winners, round, num_players, play_direction)
                            print(f"\nPlayer {round % num_players}, you got your turn skipped by Player {player_no}")

                        elif cards_played[0].value == 20: # Social reverses play direction
                            play_direction += 1

                        elif cards_played[0].value == 10: # 10 Burns pile and gives another turn
                            pile = []
                            print(f"Player {player_no}, your performed a 10 burn and get another turn")
                            if play_direction % 2 == 1:
                                round -= 1
                            else:
                                round += 1
                    else:
                        pile.append(cards_played[0])
                        print(f"Player {player_no}, your face down could not be played and you have picked up the pile")
                        players[player_no].pickup(pile) # Pick up pile
                        pile = [] # Reset pile
                else:
                    for card in cards_played:
                        pile.append(card)
                        if card.value == 8: # 8 Skips next person, this also covers multiple skips
                            round = skip_turn(winners, round, num_players, play_direction)
                            print(f"\nPlayer {round % num_players}, you got your turn skipped by Player {player_no}")

                        elif card.value == 20 : # Social reverses play direction
                            play_direction += 1

                    if value == 10: # 10 Burns pile and gives another turn
                            pile = []
                            print(f"Player {player_no}, your performed a 10 burn and get another turn")
                            if play_direction % 2 == 1:
                                round -= 1
                            else:
                                round += 1

                if len(deck) != 0:
                    deck = players[player_no].draw(deck)

                if len(players[player_no].facedown) == 0 and len(players[player_no].faceup) == 0 and len(players[player_no].hand) == 0:
                    winners = win(player_no, winners, num_players)

        if stack_burn(pile): # Burn pile if 4 consecutive cards
            pile = []

        print() # Print newline for text readability

        # Move onto next player
        if play_direction % 2 == 1:
            round += 1
        else:
            round -= 1

# Check pile for card to be played on
def parse_pile(pile):
    i = 1
    while True: # Loop down the cards in pile
        # Try system to prevent IndexError when all cards in pile obey special rules and are not returned
        try:
            card = pile[len(pile) - i]
        except IndexError:
            return pile[len(pile) - 1]

        if card.value in [3, 7, 20, 21]: # 3s are invisible and can be played on anything
            i += 1

        # INSERT CUSTOM RULES HERE

        else: # If card is not special, return it
            return card

# Used when a player has multiple cards in their hand or face ups
def get_number_of_cards(num_of_value, value):
    while True:
        try:
            num_of_cards = int(input(f"You have {num_of_value} cards of value {value} to play. How many would you like to play? "))
        except ValueError:
            print(f"You must input an integer between 1 and {num_of_cards}.")
        else:
            if 1 <= num_of_cards <= num_of_value:
                return num_of_cards
            else:
                print(f"You can only play between 1 and {num_of_cards} cards.")

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
def stack_burn(pile):
    if len(pile) >= 4:
        last_4_values = [card.value for card in pile[-4:]]
        if all(value == last_4_values[0] for value in last_4_values):
            print("A stack burn has been performed")
            return True
    return False

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
            text = f"{len(winners)}th..."

    print(f"Congratulations player {player_no}, you came {text}")
    k = input(f"Press ENTER to continue...")
    return winners

def final_standings(winners): # Output the winners array to show final scores
    for i in range(len(winners)):
        print(f"In position {i + 1} is Player {winners[i]}")

    sys.exit("Thanks for playing! Made by George Newman.")


def load_deck(file_name, deck_count):
    # Check that the file exists
    try:
        file = open(file_name, "r")
    except KeyError:
        sys.exit("File does not exist")

    # Prepare to read csv
    reader = csv.DictReader(file)
    deck = []
    cards_loaded = 0

    # Read csv
    for row in reader:
        deck.append(Card(row["face"], row["suit"], row["value"]))
        cards_loaded += 1

    for _ in range(deck_count - 1):
        deck += deck

    print(f"{cards_loaded} Cards Loaded")
    print(f"{54 * deck_count} Base Cards Loaded")
    print(f"{cards_loaded - (54 * deck_count)} Special Cards Loaded")

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

def skip_turn(winners, round, num_players, play_direction):
    while True:
        if play_direction % 2 == 1:
            round += 1
            if round % num_players not in winners:
                return round
        else:
            round -= 1
            if round % num_players not in winners:
                return round


if __name__ == "__main__":
    main()
