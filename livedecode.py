import sys

weights = {}
start_weight = 10
accept_weight = 7

# custom
dec_colors = {"uart-1":'\x1b[6;30;42m', "uart-2":'\x1b[6;30;43m', 'switch':'\x1b[7m', }

reset_marker = '\x1b[0m'

current_dec = None
text = ""

import atexit
def on_exit():
    print(reset_marker)
    #print(repr(text))
atexit.register(on_exit)


for line in sys.stdin:
    try:
        samp_num, dec, data = line.rstrip().split(' ', 2)
    except:
        print(repr(line))
        raise
    dec = dec.rstrip(':')
    if dec not in weights: weights[dec] = start_weight
    other_decs = [d for d in weights.keys() if d != dec]
    data = data.strip().lower()
    if data in ["stop bit", "start bit"]:
        continue
    if data == "frame error":
        # TODO previous char discard?
        weights[dec] = 0
        # counterweighting to compensate
        for d in other_decs:
            if weights[dec] < start_weight:
                weights[dec] = weights[dec] + 1
    else:
        # successful receipt
        # incrementing weight if not at max
        if weights[dec] < start_weight:
            weights[dec] = weights[dec] + 1
        try:
            data = int(data, 16)
        except ValueError:
            pass # ignoring it for now
    # comparing weights
    if weights[dec] > accept_weight:
        if isinstance(data, int):
            # text to add
            add = ""
            # successful decode
            #line = '{}: {} ({})\n'.format(dec, repr(chr(data)), hex(data))
            if current_dec is None:
                # start of decoding
                add += dec_colors[dec]
                current_dec = dec
            elif dec != current_dec:
                # adding a newline and a white space where decoders change
                add += reset_marker
                add += dec_colors["switch"]
                add += '\n '
                # here, text changes color to other decoder's text
                add += reset_marker
                color = dec_colors[dec]
                if data == ord('\r'):
                    add += color.replace('30', '31')
                    add += 'R'
                    add += reset_marker
                add += color
                current_dec = dec
            if data != ord('\r'):
                add += chr(data) if data <= 127 else repr(chr(data))
            sys.stdout.write(add)
            text += add
        else:
            pass #line = '{}: {}\n'.format(dec, data)
        pass # sys.stdout.write(line)



