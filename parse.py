# transaction list
tr = []

# current transaction
t = []

# filter address
addr = 0x22

# read/write keyword shortening
tts = {"write:":'wr', "read:":'rd'}

with open('decoded.txt', 'r') as f:
  line = f.readline()
  while line:
    line = line.strip()
    if not line:
        break # this stops the script at the empty line. use `continue` to go to the next line
    tss, _, _, d = line.split(' ', 3)
    if d == "Start":
        # new transaction
        # saving/discarding the current one
        if t:
            t_addr = t[1]
            if t_addr != addr:
                #print("Filtering transaction for", hex(t[0]), ":", t)
                t = ["start"] # discarding the entire transaction
            else:
                tr.append(t)
                t = ["start"]
    elif d.startswith("Address "):
        _, rw, a = d.split(' ', 2)
        t.append(int(a, 16))
        t.append(tts[rw])
    elif d.startswith("Data"):
        _, rw, dt = d.split(' ', 2)
        t.append(tts[rw])
        t.append(int(dt, 16))
    elif d in ['ACK', 'NACK', 'Stop', 'Start repeat']:
        t.append(d.lower())
    #new line
    line = f.readline()


print("-----------------------")

def myhex(i):
    return '0x'+hex(i)[2:].zfill(2)

def mybin(i):
    return '0b'+bin(i)[2:].zfill(8)

# second parsing

regs = {
    0x00: "CTRL3",
    0x01: "DEV_ID",
    0x02: "SWITCH0",
    0x03: "SWITCH1",
    0x04: "MEASURE",
    0x05: "SLICE",
    0x06: "CTRL0",
    0x07: "CTRL1",
    0x08: "CTRL2",
    0x09: "CTRL3",
    0x0A: "MASK",
    0x0B: "POWER",
    0x0C: "RESET",
    0x0D: "OCPREG",
    0x0E: "MASKA",
    0x0F: "MASKB",
    0x43: "FIFO",
    0x3C: "STATUS0A",
    0x3D: "STATUS1A",
    0x3E: "INTRPT_A",
    0x3F: "INTRPT_B",
    0x40: "STATUS0",
    0x41: "STATUS1",
    0x42: "INTERRPT",
    0x43: "FIFO",
}

# for pretty-printing column width consistency
longest_regn = max(map(len, regs.values()))

# storing the human-readable transaction data

transactions = []

for t in tr:
    addr = t[1]
    reg = t[5]
    t = t[7:]
    if t[0] == 'start repeat':
        t = t[4:]
    op = t[0]
    d = [t[1]]
    t = t[2:]
    for el in t:
        if el in ['ack', 'nack', 'stop', 'rd', 'wr']:
            continue
        d.append(el)
    data = " ".join(list(map(myhex, d)))
    data += ' ({})'.format(" ".join(list(map(mybin, d))))
    reg_str = "{} ({})".format(myhex(reg), regs.get(reg, " ").rjust(longest_regn, ' '))
    transactions.append([addr, myhex(addr), reg, reg_str, op, d, data])

for transaction in transactions:
    # a loop that prints out transactions in a reasonably readable way
    addr, addr_str, reg, reg_str, op, data, data_str = transaction
    print(addr_str, reg_str, op, data)

def tr_as_upy(transaction):
    # print out transactions as MicroPython code
    addr, addr_str, reg, reg_str, op, data, data_str = transaction
    if op == 'rd':
        print('i2c.readfrom_mem({}, {}) # {}: {} {}'.format(hex(addr), hex(reg), op, regs.get(reg, ''), data_str))
    elif op == 'wr':
        #print(data)
        print('resp = i2c.writeinto_mem({}, {}, {}) # {} {}: {}'.format(hex(addr), hex(reg), str(bytes(data)), op, regs.get(reg, ''), data_str))

for transaction in transactions:
    # a loop that prints out transactions as MicroPython code
    tr_as_upy(transaction)
