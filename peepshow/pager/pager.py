from getch import getch # py-getch package
import sys
import colorama
import re
from peepshow.utils import terminal
import shutil

class Line:
    ansi_escape = re.compile(r'\x1b[^m]*m')

    def __init__(self, text):
        self.text = text

    def no_colors(self):
        return self.ansi_escape.sub('', self.text)

    def __len__(self):
        return len(self.no_colors())

    def __str__(self):
        return self.text

    def trim(self, length):
        in_buf = self.text
        out_buf = ''
        out_buf_len = 0
        while in_buf and out_buf_len < length:

            m = self.ansi_escape.match(in_buf)
            if m:
                out_buf += m.group()
                in_buf = in_buf[m.end():]
                continue
            else:
                out_buf += in_buf[0]
                out_buf_len += 1
                in_buf = in_buf[1:]

        return Line(out_buf + colorama.Style.RESET_ALL)

    def __add__(self, other):
        return Line(self.text + str(other))

class Pager:

    def __init__(self, start_page_callback=((lambda: None),), numeric=False):
        self.page_width, self.page_height = shutil.get_terminal_size()
        self.start_page_callback = start_page_callback
        self.numeric = numeric

    def trim_line(self, line):
        elip = Line(colorama.Style.DIM + '...' + colorama.Style.RESET_ALL)
        if len(line) > self.page_width:
            line = line.trim(self.page_width - len(elip)) + elip
            line = line.trim(self.page_width)
        return line

    def print_line(self, line):
        line = self.trim_line(line)
        sys.stdout.write(str(line))
        line_len = len(line)
        last_row_len = line_len % self.page_width
        if not line_len or last_row_len:
            # add extra CR/CRLF if line doesn't cover entire width
            # this does matter under Window and is meaningless under Linus
            print()

    def prompt(self):
        hint = f"Press Q/ESC{['', '/NUMBER'][self.numeric]} to stop or any other key to continue..."
        line = str(self.trim_line(Line(hint)))
        terminal.print_help(line, end='')
        sys.stdout.flush()
        try:
            key = getch()
            ESC = '\x1b'
            CTRL_C = '\x03'
            terminating_keys = [ESC, CTRL_C, 'q', 'Q']
            numbers = [str(x) for x in range(10)]
            if self.numeric:
                terminating_keys += numbers
                if key in numbers:
                    terminal.prefill_input(key)
            interrupted = key in terminating_keys
        except KeyboardInterrupt:
            interrupted = True
        sys.stdout.write('\r' + ' '*(len(line)) + '\r')
        sys.stdout.flush()
        return interrupted

    def execute_start_page_callback(self):
        self.start_page_callback[0](*self.start_page_callback[1:])

    def page(self, lines):
        footer_height = 1 # reserve one line for the prompt
        usable_height = (self.page_height - footer_height)
        self.execute_start_page_callback()

        for line_idx, line in enumerate(lines):
            end_page = (line_idx + 1) % usable_height == 0

            self.print_line(Line(line))

            if end_page:
                if self.prompt():
                    break
                else:
                    self.execute_start_page_callback()
                    terminal.clear()

        sys.stdout.flush()

def page(content):
    p = Pager()
    p.page(content)
