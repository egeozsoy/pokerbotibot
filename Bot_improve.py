import random
import telegram
import telegram.ext
from telegram.ext import Updater
from telegram.ext import messagehandler
from telegram.ext import CommandHandler
import logging
import time


# s:spade , h:heart,d:diamons,c:clubs


class cards(object):
    def __init__(self, string):
        self.string = string

    def typ(self):
        return str(self.string[0])

    def asstr(self):

        return self.string

    def numeric(self):
        a = self.string[1:]
        return int(self.string[1:])

    def inreverseorder(self):
        return str(self.string[1:]) + str(self.string[0])

    def same_type(self, other):
        return self.typ() == other.typ()

    def __eq__(self, other):
        return self.numeric() == other.numeric()

    def __lt__(self, other):

        try:

            return self.numeric() < other.numeric()
        except:
            print('error')

    def __str__(self):
        out = ''
        if (self.string[0] == 's'):
            out += '\u2660'
        elif (self.string[0] == 'h'):
            out += '\u2764'
        elif (self.string[0] == 'd'):
            out += '\u2663'
        elif (self.string[0] == 'c'):
            out += '\u2666'
        if (int(self.string[1:]) == 11):
            out += 'J'
        elif (int(self.string[1:]) == 12):
            out += 'Q'
        elif (int(self.string[1:]) == 13):
            out += 'K'
        elif (int(self.string[1:]) == 14):
            out += 'A'
        else:
            out += (self.string[1:])

        return out


class deck(object):
    global current_deck

    def reset_deck(self):
        global current_deck
        start_deck = []
        for i in range(0, 4):
            for k in range(2, 15):
                s = ''
                if (i == 0):
                    s = 's'
                elif (i == 1):
                    s = 'h'
                elif (i == 2):
                    s = 'd'
                elif (i == 3):
                    s = 'c'
                tmp_cards = cards(s + str(k))
                start_deck.append(tmp_cards)
                # start_deck.append(s + str(k))
        current_deck = start_deck
        return start_deck

    def dealcard(self):
        global current_deck
        deck = current_deck

        i = random.randrange(0, len(deck))

        # print(i)
        # print(deck[i])

        toreturn = deck[i]

        deck.remove(deck[i])
        current_deck = deck
        # print(deck)
        return toreturn

    def dealhand(self):
        hand = []
        hand.append(self.dealcard())
        hand.append(self.dealcard())
        return hand

    def get_current_deck(self):
        global current_deck
        return current_deck

    def deck_tostring(self, string):
        out = ''
        if (string[0] == 's'):
            out += '\u2660'
        elif (string[0] == 'h'):
            out += '\u2764'
        elif (string[0] == 'd'):
            out += '\u2663'
        elif (string[0] == 'c'):
            out += '\u2666'
        if (int(string[1:]) == 11):
            out += 'J'
        elif (int(string[1:]) == 12):
            out += 'Q'
        elif (int(string[1:]) == 13):
            out += 'K'
        elif (int(string[1:]) == 14):
            out += 'A'
        else:
            out += (string[1:])

        return out


class Player(object):
    # global money_amount
    # global cards
    # global name

    def __init__(self, toname, tomoneyamount, chat_id, cards=[], moneyonthetable=0, folded=False, ):
        # global name, moneyamount
        self.name = toname
        self.money_amount = tomoneyamount
        self.moneyonthetable = moneyonthetable
        self.cards = cards
        self.folded = False
        self.chat_id = chat_id

    def get_name(self):
        # global name
        return self.name

    def get_moneyonthetable(self):
        return self.moneyonthetable

    def get_folded(self):
        return self.folded

    def fold(self):
        self.folded = True

    def unfold(self):
        self.folded = False

    def reset_moneyonthetable(self):
        self.moneyonthetable = 0

    def get_money_amount(self):
        # global money_amount
        return self.money_amount

    def set_money_amount(self, toset):
        # global money_amount
        money_amount = toset

    def subtract_money_amount(self, tosubtract):
        # global money_amount
        self.money_amount -= tosubtract
        self.moneyonthetable += tosubtract

    def newCards(self):
        # global cards
        d = deck()
        d.reset_deck()
        self.cards = d.dealhand()

    def __eq__(self, other):
        return self.name == other.name

    # def cardtostring(self):
    def __str__(self):
        return self.name + ' ' + str(self.money_amount) + ' ' + str(self.cards[0]) + str(self.cards[1])


class evaluation(object):
    def __init__(self, hand: list, table: list, value=0):
        self.cards = hand + table
        self.value = value
        self.cards.sort()
        self.transport = 0
        self.third = 0
        self.pair = 0
        self.two_pairs = []
        self.string = ''

    def high_card(self):
        self.string = ('High card' + str(self.cards[-1]))
        self.value = int(self.cards[-1].numeric())
        return self.cards[-1]

    def one_pair(self, other=0):
        b = False
        for i in range(0, len(self.cards) - 1):

            if (self.cards[i].numeric() != other):
                if (self.cards[i] == self.cards[i + 1]):
                    self.string = ('PAIR ' + str(self.cards[i]))
                    b = True
                    self.pair = int(self.cards[i].numeric())
                    if (14 + int(self.cards[i].numeric()) > self.value):
                        self.value = 14 + int(self.cards[i].numeric())
                        b = True

        return b

    def two_pairss(self):
        b = 0
        for i in range(0, len(self.cards) - 1):

            if (self.cards[i] == self.cards[i + 1]):
                self.string = ('PAIR ' + str(self.cards[i]))
                b += 1
                self.two_pairs.append(int(self.cards[i].numeric()))
        if (b > 1):
            self.value = 50 + int(self.two_pairs[-1]) * 10 + int(self.two_pairs[-2])
            return True

        return False

    def three_of_a_kind(self):
        b = False
        for i in range(0, len(self.cards) - 2):
            if (self.cards[i] == self.cards[i + 1] == self.cards[i + 2]):
                self.string = ('Three of a kind ' + str(self.cards[i]))
                b = True
                if (30 + int(self.cards[i].numeric()) > self.value):
                    self.third = int(self.cards[i].numeric())
                    self.value = 300 + int(self.cards[i].numeric())
                    self.transport = int(self.cards[i].numeric())
                    b = True

        return b

    def straigt(self):
        b = False
        for i in range(0, 3):
            if (self.cards[i].numeric() + 1 == self.cards[i + 1].numeric() and self.cards[i + 1].numeric() + 1 ==
                self.cards[i + 2].numeric() and
                            self.cards[i + 2].numeric() + 1 == self.cards[i + 3].numeric() and self.cards[
                    i + 3].numeric() + 1 == self.cards[i + 4].numeric()):
                self.string = ('Straigth')
                self.value = 500 + self.cards[i + 4].numeric()
                b = True
        return b

    def flush(self):
        b = False
        s = []
        d = []
        h = []
        c = []
        main = []
        for i in self.cards:
            if (i.typ() == 's'):
                s.append(i)
                if (len(s) >= 5):
                    main = s
            elif (i.typ() == 'c'):
                c.append(i)
                if (len(c) >= 5):
                    main = c
            elif (i.typ() == 'd'):
                d.append(i)
                if (len(d) >= 5):
                    main = d
            elif (i.typ() == 'h'):
                h.append(i)
                if (len(h) >= 5):
                    main = h
        if (len(main) >= 5):
            b = True
            self.string = ('Flush')
            self.value = 700 + main[-1].numeric() * 5 + main[-2].numeric() * 4 + main[-3].numeric() * 3 + main[
                                                                                                              -4].numeric() * 2 + \
                         main[-5].numeric() * 1
        return b

    def full_house(self):
        if (self.three_of_a_kind()):
            # tmp = self.value
            if (self.one_pair(self.transport)):
                # tmp +=self.transport

                self.value = 2670 + self.third * 10 + self.pair
                self.string = ('Full house ' + str(self.value))
                return True
        return False

    def four_of_a_kind(self):
        for i in range(0, len(self.cards) - 3):
            if (self.cards[i] == self.cards[i + 1] == self.cards[i + 2] == self.cards[i + 3]):
                self.string = ('Four of a kind')
                self.value = 4300 + int(self.cards[i].numeric())

                return True

        return False

    def straigt_flush(self):
        b = False
        s = d = h = c = []
        main = []
        for i in self.cards:
            if (i.typ() == 's'):
                s.append(i)
                if (len(s) >= 5):
                    main = s
            elif (i.typ() == 'c'):
                c.append(i)
                if (len(c) >= 5):
                    main = c
            elif (i.typ() == 'd'):
                d.append(i)
                if (len(d) >= 5):
                    main = d
            elif (i.typ() == 'h'):
                h.append(i)
                if (len(h) >= 5):
                    main = h
        if (len(main) >= 5):
            for i in range(0, 3):
                if (main[i].numeric() + 1 == main[i + 1].numeric() and main[
                        i + 1].numeric() + 1 == main[i + 2].numeric() and
                                main[i + 2].numeric() + 1 == main[i + 3].numeric() and main[
                        i + 3].numeric() + 1 == main[i + 4].numeric()):
                    self.string = ('Straigth_FLush AMAZING ')
                    self.value = 10000 + self.cards[i + 4].numeric()
                    b = True
            return b

        return b

    def evaluate(self):
        self.high_card()
        one_pair = self.one_pair()
        two_pairs = False

        two_pairs = self.two_pairss()
        three = False
        if (one_pair):
            three = self.three_of_a_kind()
        straigt = self.straigt()
        flush = self.flush()
        if (three):
            self.full_house()
        if (three):
            self.four_of_a_kind()
        if (self.straigt() and self.flush()):
            test.straigt_flush()


def tostring(array):
    out = ''

    for p in array:
        out += p.__str__() + '\n'
    return out


global Player_array, starting_money, game
Player_array = []
starting_money = 250
new_player = ''
game = False


def game_prep():
    while (True):
        new_player = input('give')
        if (new_player == 'x'):
            break
    tmp = Player(new_player, starting_money)
    Player_array.append(tmp)


def reset_game():
    global game
    game = False
    for Player in Player_array:
        Player.unfold()
        Player.moneyonthetable = 0

        deck.reset_deck(deck)


# game_prep()
# game(Player_array)






def get_username(str):
    begin = 0
    end = 0
    for letter in range(0, len(str)):
        if (str[letter] == 'u' and str[letter + 1] == 's' and str[letter + 2] == 'e' and str[letter + 3] == 'r' and
                    str[letter + 4] == 'n'):
            begin = letter + 12
    for letter in range(begin, len(str)):
        if (str[letter] == "'"):
            end = letter
    return str[begin:end]


bot = telegram.Bot(token='359154603:AAH0laQqI9iJXwVkRypEwWfklB05vMyfqww')


def start(bot, update):
    print('hi')
    reset_game()
    global Player_array, starting_money
    Player_array = []

    starting_money = 250
    new_player = ''
    bot.sendMessage(chat_id=update.message.chat.id, text=(
        'Received your name'))

    new_player = str(update.message)
    new_player = (get_username(new_player))

    tmp = Player(new_player, starting_money, update.message.chat.id)
    Player_array.append(tmp)
    for a in Player_array:
        print(a.name)


def join(bot, update):
    global Player_array, starting_money
    new_player = str(update.message)
    new_player = (get_username(new_player))
    new_player = str(update.message)
    new_player = (get_username(new_player))
    tmp = Player(new_player, starting_money, update.message.chat.id)

    if tmp in Player_array:
        print("already joined")
        tmp = Player(new_player, starting_money, update.message.chat.id)

    else:
        bot.sendMessage(chat_id=update.message.chat.id, text=(
            'Received your name'))

        Player_array.append(tmp)

    for a in Player_array:
        print(a.name)

def SendToUser(txt , array):
    for p in array:
        bot.sendMessage(chat_id=p.chat_id , text=txt)



updater = Updater(token='359154603:AAH0laQqI9iJXwVkRypEwWfklB05vMyfqww')
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
join_handler = CommandHandler('join', join)
dispatcher.add_handler(join_handler)
global offset
offset = 0
updates = []
while (True):

    if (len(updates) > 0):
        offset = bot.getUpdates()[-1].update_id + 1
        updates = bot.getUpdates(offset=offset)
        for u in updates:
            # offset = bot.getUpdates()[-1].update_id + 1
            if (u.message.text == '/start'):
                start(bot, u)
            elif (u.message.text == '/join'):
                join(bot, u)
            elif (u.message.text == '/game'):
                game = True
    else:
        updates = bot.getUpdates()
        for u in updates:
            # offset = bot.getUpdates()[-1].update_id + 1
            if (u.message.text == '/start'):
                start(bot, u)
            elif (u.message.text == '/join'):
                join(bot, u)
            elif (u.message.text == '/game'):
                game = True
    # print('Game is : ' + str(game))
    #game starts
    while game == True:
        print('here')
        table_array = []
        money_per_person =0
        table_money = 0

        cards_open = 0
        reset_game()
        #cards dealt
        for p in Player_array:
            p.newCards()

        # raise check fold
        while (cards_open <= 4):
            missing_money = True #makes sure everyone has played
            while (missing_money == True):
                missing_money = False
                print("Player array len " + str(len(Player_array)))
                for p in Player_array:

                    if (p.folded == False):
                        print('len + ' + str(len(p.cards)))
                        bot.sendMessage(chat_id=p.chat_id, text=(
                            str(p.cards[0]) + str(p.cards[1])))
                        bot.sendMessage(chat_id=p.chat_id, text=(
                            'Money on the table:' + str(table_money)))
                        bot.sendMessage(chat_id=p.chat_id, text=(
                            'Money per person:' + str(money_per_person)))


                        if (p.get_moneyonthetable() < money_per_person):
                            bot.sendMessage(chat_id=p.chat_id , text= ("You have  " + str(money_per_person - p.get_moneyonthetable()) +
                                                                       ' less money on the table, to continue, make sure to at least check'))

                        while (True):
                            # get information from user

                            input = False
                            inputstr = ''
                            bot.sendMessage(chat_id=p.chat_id, text=(p.get_name() + '  Money: ' + str(
                                p.get_money_amount()) + ' what do you want to do? (example: raise,check,fold)'))
                            print('Getting information from user')
                            while (input == False):
                                if offset == 0:

                                    updates = bot.getUpdates()
                                else:
                                    updates = bot.getUpdates(offset + 1)
                                for a in updates:
                                    offset = a.update_id
                                    print(a.message.text)
                                    if (a.message.chat.id == p.chat_id):
                                        input = True
                                        inputstr = a.message.text
                                    try:
                                        string = str(a.message.text)

                                    except:
                                        print('error')


                            commend = inputstr
                            print(commend)
                            if (commend == 'raise' or commend == 'r' or commend == 'R'):
                                amount = ''
                                input2 = False

                                while (True):
                                    bot.sendMessage(chat_id=p.chat_id, text=(p.get_name() + '  Money: ' + str(
                                        p.get_money_amount()) + 'Give an amount to raise'))
                                    try:
                                        while (input2 == False):
                                            if offset == 0:

                                                updates = bot.getUpdates()
                                            else:
                                                updates = bot.getUpdates(offset + 1)
                                            for a in updates:
                                                offset += a.update_id
                                                print('here3')
                                                print(a.message.text)
                                                if (a.message.chat.id == p.chat_id):
                                                    print('Amount : ' + str(a.message.text))
                                                    input2 = True
                                                try:

                                                    amount = int(a.message.text)



                                                except:
                                                    print('error')
                                                    input == False

                                        break
                                    except:
                                        print("please give a number")
                                print('Amount :' + str(amount))
                                if (p.get_money_amount() >= amount + (money_per_person - p.get_moneyonthetable())):
                                    p.subtract_money_amount(amount + (money_per_person - p.get_moneyonthetable()))
                                    money_per_person += amount
                                    table_money += amount + (amount + (money_per_person - p.get_moneyonthetable()))
                                    SendToUser(str(p.get_name()) + ' has raised ' + str(amount),Player_array)
                                    break
                                else:
                                    print("You cant raise that much")
                            elif (commend == 'check' or commend == 'c' or commend == 'C'):
                                if (p.get_money_amount() >= (money_per_person - p.get_moneyonthetable())):
                                    p.subtract_money_amount(money_per_person - p.get_moneyonthetable())
                                    table_money += money_per_person - p.get_moneyonthetable()
                                    SendToUser(str(p.get_name()) + ' has checked ', Player_array)
                                    break
                                else:
                                    print("you had to all in")
                                    p.set_money_amount(0)
                                    SendToUser(str(p.get_name()) + ' goes all in ', Player_array)
                                    break
                            elif (commend == 'fold' or commend == 'f' or commend == 'F'):
                                p.fold()
                                print("you folded")
                                SendToUser(str(p.get_name()) + ' folds ', Player_array)
                                break
                for p in Player_array:
                    if (p.folded == False):
                        if (p.get_moneyonthetable() < money_per_person):
                            missing_money = True

            print(str(cards_open) + ' cards open')
            if (cards_open == 0):
                table_array.append(deck.dealcard(deck))
                table_array.append(deck.dealcard(deck))
                table_array.append(deck.dealcard(deck))

                cards_open += 3
            else:
                table_array.append(deck.dealcard(deck))
                cards_open += 1
            out = ''

            for card in table_array:
                out += str(card)
            for p in Player_array:
                bot.sendMessage(chat_id=p.chat_id, text='Cards on the table : ' + str(out))

        print(tostring(Player_array))
        tmp = 0
        winner = []
        winnerstring = ''
        # evaluate

        for Player in Player_array:
            if (Player.folded == False):
                test = evaluation(Player.cards, table_array)
                test.evaluate()
                out = (str(Player.name) + ' got ' + test.string)
                for pl in Player_array:
                    bot.sendMessage(chat_id=pl.chat_id, text=str(out))

                # print('Test value is ' + str(test.value))
                if (test.value > tmp):
                    winner = []
                    winner.append(Player)
                    tmp = test.value
                    winnerstring = test.string
                elif (test.value == tmp):
                    winner.append(Player)
        tmp = 0
        # print('Winner length is '+ str(len(winner)))
        if (len(winner) == 1):
            winner[0].money_amount += table_money
            for pl in Player_array:
                bot.sendMessage(chat_id=pl.chat_id, text=str(winner[0].name + ' wins with a ' + winnerstring))
        elif (len(winner) > 1):
            for pl in Player_array:
                bot.sendMessage(chat_id=pl.chat_id, text=str('Many winners this time'))
            tomoney = table_money / len(winner)
            for a in winner:
                print(a.name)
                a.money_amount += tomoney
        for p in Player_array:

            bot.sendMessage(chat_id=p.chat_id,
                        text=(Player_array[0].get_name() + 'To continue playing press c to quit press x'))

        while (True):
            input2 = False
            print('input is' + str(input2))

            while (input2 == False):
                if (len(updates) > 0):
                    offset = bot.getUpdates()[-1].update_id + 1
                    updates = bot.getUpdates(offset=offset)
                    for u in updates:
                        # offset = bot.getUpdates()[-1].update_id + 1
                        if (u.message.text == 'c' or u.message.text == 'C'):
                            game = True
                            input2 = True
                        elif (u.message.text == 'x' or u.message.text == 'X'):
                            game = False
                            input2 = True

                else:
                    updates = bot.getUpdates()
                    for u in updates:
                        # offset = bot.getUpdates()[-1].update_id + 1
                        if (u.message.text == 'c' or u.message.text == 'C'):
                            game = True
                            input2 = True
                        elif (u.message.text == 'x' or u.message.text == 'X'):
                            game = False
                            input2 = True

            break

#money calculation error
