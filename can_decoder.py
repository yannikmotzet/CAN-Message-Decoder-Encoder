import numpy as np

filepath = 'database.txt'
paramater_number = 4


# load the database
#####################################
f = open(filepath)
number_of_signals = len(open(filepath).readlines())

database = np.full((number_of_signals, paramater_number), None)
counter = 0
for line in f:
    database_line = line.split(",")
    # signal name
    database[counter, 0] = database_line[0]
    # bit length
    database[counter, 1] = int(database_line[1])
    # signedness
    database[counter, 2] = database_line[2]
    # factor
    database[counter, 3] = float(database_line[3])
    counter = counter + 1


# input CAN message
#####################################
can_message = input("Input the CAN message: ")
# can_message = "A5, B6, A5, B6, A5, B6, A5, B6"      # for testing purpose
can_message = can_message.split(",")

can_list = []
for message in can_message:
    can_list.append(bin(int(message, 16))[2:].zfill(8))


# decode the CAN message
#####################################
signal_list = [None] * database.shape[0]

byte_index = 0
for i in range(database.shape[0]):          # iterate through database signals
    for j in range(database[i, 1]):         # itarate through length of signal
        if len(can_list[byte_index]) == 0:
            byte_index = byte_index + 1
        if signal_list[i] is None:
            signal_list[i] = can_list[byte_index][-1]
        else:
            signal_list[i] = can_list[byte_index][-1] + signal_list[i]
        # delete last bit
        can_list[byte_index] = can_list[byte_index][:-1]


# print result
#####################################
for i in range(database.shape[0]):
    print(database[i, 0] + ": ")
    print(int(signal_list[i], 2) * database[i, 3])