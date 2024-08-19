class PrintColor:
    def get_color_id(color, is_fg):
        # ANSI color codes : https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
        # RGB values : https://g.co/kgs/K5ciwD1

        if color is str:
            color = color.lower()

        if color == 'black':
            return 30 if is_fg else 40
        elif color == 'red':
            return 31 if is_fg else 41
        elif color == 'green':
            return 32 if is_fg else 42
        elif color == 'yellow':
            return 33 if is_fg else 43
        elif color == 'blue':
            return 34 if is_fg else 44
        elif color == 'magenta':
            return 35 if is_fg else 45
        elif color == 'cyan':
            return 36 if is_fg else 46
        elif color == 'white':
            return 37 if is_fg else 47
        elif color == 'gray' or color == 'grey':
            return 90 if is_fg else 100
        elif color == 'bright red':
            return 91 if is_fg else 101
        elif color == 'bright green':
            return 92 if is_fg else 102
        elif color == 'bright yellow':
            return 93 if is_fg else 103
        elif color == 'bright blue':
            return 94 if is_fg else 104
        elif color == 'bright magenta':
            return 95 if is_fg else 105
        elif color == 'bright cyan':
            return 96 if is_fg else 106
        elif color == 'bright white':
            return 97 if is_fg else 107
        elif color == 'pure white':
            return '38;2;255;255;255' if is_fg else '48;2;255;255;255'
        elif color == 'pure red':
            return '38;2;255;0;0' if is_fg else '48;2;255;0;0'
        elif color == 'pure green':
            return '38;2;64;192;64' if is_fg else '48;2;64;192;64'
        elif color == 'pure blue':
            return '38;2;0;0;255' if is_fg else '48;2;0;0;255'

        return 30 if is_fg else 40 # black by default

    def cstr_with_arg(s, fg_color, bold, bg_color=None):
        fg_color_id = PrintColor.get_color_id(fg_color, True)
        bg_color_id = PrintColor.get_color_id(bg_color, False)
        bold_id = 1 if bold else 0

        color = f'{fg_color_id};{bg_color_id}' if bg_color != None else fg_color_id

        return f"\x1b[{bold_id}m\x1b[{color}m{s}\x1b[0m"

    def cstr(s):
        if s == ' 0 ': # empty
            return PrintColor.cstr_with_arg(s=s, fg_color='white', bold=False)
        elif s == ' 1 ': # J
            return PrintColor.cstr_with_arg(s=s, fg_color='pure white', bg_color='bright red', bold=True)
        elif s == ' 2 ': # Z
            return PrintColor.cstr_with_arg(s=s, fg_color='pure white', bg_color='bright blue', bold=True)
        elif s == ' 3 ': # O
            return PrintColor.cstr_with_arg(s=s, fg_color='pure white', bg_color='bright green', bold=True)
        elif s == ' 4 ': # L
            return PrintColor.cstr_with_arg(s=s, fg_color='pure white', bg_color='magenta', bold=True)
        elif s == ' 5 ': # T
            return PrintColor.cstr_with_arg(s=s, fg_color='pure white', bg_color='yellow', bold=True)
        elif s == ' 6 ': # S
            return PrintColor.cstr_with_arg(s=s, fg_color='pure white', bg_color='cyan', bold=True)
        elif s == ' 7 ': # I
            return PrintColor.cstr_with_arg(s=s, fg_color='pure white', bg_color='grey', bold=True)
        elif s == ' 8 ': # I
            return PrintColor.cstr_with_arg(s=s, fg_color='black', bg_color='pure red', bold=True)

        return PrintColor.cstr_with_arg(s=s, fg_color='black', bold=False)

class TetrisInfos:
    def better_game_area(game_area, with_indexes=True):
        colored_game_area = ''
        if with_indexes:
            colored_game_area = '      0  1  2  3  4  5  6  7  8  9\n-----------------------------------\n'

        for x, row in enumerate(game_area):
            if with_indexes:
                colored_game_area += f"{'{:02d}'.format(x)} | "
            for y, tile in enumerate(row):
                colored_game_area += PrintColor.cstr(f' {tile} ')
            colored_game_area += '\n'

        return colored_game_area

    def get_tetromino_form(tetromino_id):
        if tetromino_id == 0:
            return 'empty'
        if tetromino_id == 1:
            return 'J'
        if tetromino_id == 2:
            return 'Z'
        if tetromino_id == 3:
            return 'O'
        if tetromino_id == 4:
            return 'L'
        if tetromino_id == 5:
            return 'T'
        if tetromino_id == 6:
            return 'S'
        if tetromino_id == 7:
            return 'I'
        if tetromino_id == 8:
            return 'Game Over Wall'
        return None

    def get_tetromino_id(tetromino_form):
        if tetromino_form == 'empty':
            return 0
        if tetromino_form == 'J':
            return 1
        if tetromino_form == 'Z':
            return 2
        if tetromino_form == 'O':
            return 3
        if tetromino_form == 'L':
            return 4
        if tetromino_form == 'T':
            return 5
        if tetromino_form == 'S':
            return 6
        if tetromino_form == 'I':
            return 7
        if tetromino_form == 'Game Over Wall':
            return 8
        return -1

    def update_datas(df, time, score, lines, rewards, nb_blocs):
        new_datas = {'Time':time, 'Score':score, 'Lines':lines, 'Rewards':rewards, 'NbBlocUsed':nb_blocs}
        df = df._append(new_datas, ignore_index=True)
        return df
