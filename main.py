from stockfish import Stockfish
import telebot
import re

token = ''  # Telegram token
bot = telebot.TeleBot("")
chessEngine = Stockfish('C:\\chess\\stockfish-windows-2022-x86-64-avx2.exe', parameters={"Threads": 2, "Ponder": True})
chessEngine.set_depth(10)  # Set the desired search depth

PASSWORD = '1f873h0'
user_ids = {}

def fenPass(fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'):
    regexMatch = re.match(
        '\s*^(((?:[rnbqkpRNBQKP1-8]+\/){7})[rnbqkpRNBQKP1-8]+)\s([b|w])\s([K|Q|k|q|-]{1,4})\s(-|[a-h][1-8])\s(\d+\s\d+)$', fen)
    if regexMatch:
        regexList = regexMatch.groups()
        fen = regexList[0].split("/")
        if len(fen) != 8:
            raise ValueError("expected 8 rows in position part of fen: {0}".format(repr(fen)))

        for fenPart in fen:
            field_sum = 0
            previous_was_digit, previous_was_piece = False, False

            for c in fenPart:
                if c in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    if previous_was_digit:
                        raise ValueError(
                            "two subsequent digits in position part of fen: {0}".format(repr(fen)))
                    field_sum += int(c)
                    previous_was_digit = True
                    previous_was_piece = False
                elif c == "~":
                    if not previous_was_piece:
                        raise ValueError(
                            "~ not after piece in position part of fen: {0}".format(repr(fen)))
                    previous_was_digit, previous_was_piece = False, False
                elif c.lower() in ["p", "n", "b", "r", "q", "k"]:
                    field_sum += 1
                    previous_was_digit = False
                    previous_was_piece = True
                else:
                    raise ValueError(
                        "invalid character in position part of fen: {0}".format(repr(fen)))

            if field_sum != 8:
                raise ValueError(
                    "expected 8 columns per row in position part of fen: {0}".format(repr(fen)))

    else:
        raise ValueError(
            "FEN не верный, введите правильную информацию: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")


def call_stockfish_engine(message):
    chessEngine.set_fen_position(message)
    move = chessEngine.get_best_move()
    return move

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Добро пожаловать на самый лучший бот по шахматам!\n\nВведите пароль, чтобы получить доступ к боту:")

@bot.message_handler(func=lambda message: message.text == PASSWORD)
def handle_password_correct(message):
    user_ids[message.from_user.id] = True
    bot.send_message(message.chat.id, "Пароль верный, приятного использования:")

@bot.message_handler(func=lambda message: message.text != PASSWORD and message.from_user.id not in user_ids)
def handle_password_incorrect(message):
    bot.send_message(message.chat.id, "Доступ отклонен, введите верный пароль:")

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    if message.from_user.id in user_ids:
        try:
            fenPass(message.text)
            move = call_stockfish_engine(message.text)
            bot.send_message(message.chat.id, "Ваш ход(первое значение это текущей фигуры, второе куда нужно переставить фигуру): " + move)
        except ValueError as e:
            print('\nCheck the correctness of the position: ' + str(message.text) + '\n' + str(e))
            move = str(e)
            bot.send_message(message.chat.id, move)
    else:
        bot.send_message(message.chat.id, "Доступ отклонен, введите верный пароль:")

if __name__ == '__main__':
    bot.polling(none_stop=True)
