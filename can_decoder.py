# date: 04.09.2020
# author: Yannik Motzet
# description: script to extract signal values of a CAN datagram

import numpy as np

is_decode = True        # True for decoding, False for encoding
is_decimal = True      # True for dec input/output, False for hex input/output

filepath_database = 'database.txt'
paramater_number = 4        # number of signal parameter in database file

# loads database info in numpy array
def load_database(filepath):
    
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
    f.close()
    return database

# extract signal values from CAN message
def decode_can_message(input_message, is_input_dec, database_filepath):
    
    # transform heximal/decimal to binary
    #####################################
    can_bytes_list = []
    # input in dec
    if is_input_dec:
        can_message = input_message.split(",")
        for message in can_message:
            can_bytes_list.append(bin(int(message))[2:].zfill(8))
    # input in hex
    else:
        can_message = input_message.split(",")
        for message in can_message:
            can_bytes_list.append(bin(int(message, 16))[2:].zfill(8))

    # extract binary values of signals
    #####################################
    # load the database
    database = load_database(database_filepath)

    signal_list_bin = [None] * database.shape[0]

    byte_index = 0
    # iterate through database signals
    for i in range(database.shape[0]): 
        # itarate through length of signal     
        for j in range(database[i, 1]):     
            if len(can_bytes_list[byte_index]) == 0:
                byte_index = byte_index + 1
            if signal_list_bin[i] is None:
                signal_list_bin[i] = can_bytes_list[byte_index][-1]
            else:
                signal_list_bin[i] = can_bytes_list[byte_index][-1] + signal_list_bin[i]
            # delete last bit
            can_bytes_list[byte_index] = can_bytes_list[byte_index][:-1]
    

    # transform binary values to physical values
    #####################################
    signal_list = []

    for i in range(database.shape[0]):
        # unsigned
        if database[i, 2] == "u":
            signal_value = int(signal_list_bin[i], 2) * database[i, 3]
        # unsigned
        elif database[i, 2] == "s":
            # positive sign
            if signal_list_bin[i][0] == "0":
                signal_value = int(signal_list_bin[i], 2) * database[i, 3]
            # negative sign
            elif signal_list_bin[i][0] == "1":
                signal_value = (int(signal_list_bin[i], 2) - 2**len(signal_list_bin[i])) * database[i, 3]
        # signal name + signal value (# format method removes .0 in a value)
        signal_list.append(database[i, 0] + ": " + '{:g}'.format(signal_value))      
    
    return signal_list

def request_signal_values(filepath):
    database = load_database(filepath)

    number_of_signals = database.shape[0]
    signal_values = [None] * number_of_signals

    # asking for signals and storing it
    for i in range(number_of_signals):
        signal_values[i] = input(database[i, 0] +': ')
    
    return signal_values

def encode_can_message(signal_values, is_output_dec, filepath):
    database = load_database(filepath)

    for i in range(len(signal_values)):
        # divide by factor
        signal_values[i] = round(float(signal_values[i]) / float(database[i, 3]))
        # check for negative values and signedness
        if signal_values[i] < 0 and database[i, 2] == "s":      
            signal_values[i] = int(2**database[i, 1]) + signal_values[i]
        # transfer to binary
        signal_values[i] = bin(int(signal_values[i]))[2:].zfill(database[i, 1])

    # push signal bits in bytes
    bytes_list = [None] * 8
    byte_index = 0
    bit_index = 0
    # iterate through database signals
    for i in range(database.shape[0]):   
        # itarate through length of signal   
        for j in range(database[i, 1]):
            # if byte has reached 8 bits go to next byte     
            if bit_index == 8:
                byte_index = byte_index + 1
                bit_index = 0
            bit_index = bit_index + 1

            if bytes_list[byte_index] is None:
                bytes_list[byte_index] = signal_values[i][-1]
            else:
                bytes_list[byte_index] = signal_values[i][-1] + bytes_list[byte_index]
            # delete last bit
            signal_values[i] = signal_values[i][:-1]

    # transfer binary values of bytes to hex/dec
    hex_value_list = []
    for element in bytes_list:
        if is_output_dec:
            hex_value_list.append(int(element, 2))
        else:
            hex_value_list.append(hex(int(element, 2))[2:])  

    return hex_value_list

if __name__ == "__main__":

    # decode CAN message
    if is_decode:
        if is_decimal:
            # can_message_input = "165, 182, 240, 0, 178, 151, 195, 4"    # for testing purpose
            can_message_input = input("Input CAN message (dec): ")
        else:
            # can_message_input = "A5, B6, F0, 00, B2, 97, C3, 04"        # for testing purpose
            can_message_input = input("Input CAN message (hex): ")
    
        # extract signal values from CAN message
        signal_values = decode_can_message(can_message_input, is_decimal, filepath_database)

        # print signal values
        print("-" * (len("Input CAN message (xxx): ") + len(can_message_input)))
        for value in signal_values:
            print(value)

    # encode CAN message
    else:
        signal_values = request_signal_values(filepath_database)
        hex_bytes = encode_can_message(signal_values, is_decimal, filepath_database)
        print("-" * 30)
        print("CAN message: ")
        for byte in hex_bytes[:-1]:
            print(byte, end=', ')
        print(hex_bytes[-1])
