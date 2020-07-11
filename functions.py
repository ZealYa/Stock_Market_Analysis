import re
import xlrd
from os import listdir
from os.path import isfile, join
import numpy as np


def get_stock_list_from_excel_files(excel_files_path, processed_file_path, excel_files_list):
    print("Extracting Stock List from Excel Files. Please Wait...")

    stock_list = ["وتجارت"]

    for excel_file in excel_files_list:
        excel_sheet = xlrd.open_workbook(excel_files_path + "/" + excel_file).sheet_by_index(0)
        work_book = [""] * (excel_sheet.nrows - 3)
        for r in range(3, excel_sheet.nrows):
            work_book[r - 3] = str(excel_sheet.cell_value(r, 0))
        for sn in work_book:
            if sn not in stock_list:
                stock_list.append(sn)

    open(processed_file_path, 'w').close()
    stock_list_file = open(processed_file_path, "w", encoding="utf8")
    for n in range(0, len(stock_list)):
        stock_list_file.write(stock_list[n])
        if n < len(stock_list) - 1:
            stock_list_file.write("\n")
    stock_list_file.close()

    print("Done!")

    return stock_list


def get_stock_list_from_processed_file(processed_file_path):
    print("Loading Stock List. Please Wait...")

    with open(processed_file_path, encoding="utf8") as data:
        stock_list = []
        for line in data:
            line = re.sub(" ", "_", str(line))
            part = line.split()
            stock_list.append(str(part[0]))

    print("Done!")

    return stock_list


def build_preliminary_file(file_name, number_of_stocks):
    prices_file = open(file_name, "w")
    for n in range(0, number_of_stocks):
        prices_file.write("xxx")
        if n < number_of_stocks - 1:
            prices_file.write("\n")
    prices_file.close()


def get_work_book_info(file_name):
    excel_file = xlrd.open_workbook(file_name)
    sheet = excel_file.sheet_by_index(0)
    wb_stock_list = [""] * (sheet.nrows - 3)
    wb_prices = [0] * (sheet.nrows - 3)

    for r in range(3, sheet.nrows):
        wb_stock_list[r - 3] = re.sub(" ", "_", str(sheet.cell_value(r, 0)))
        wb_prices[r - 3] = sheet.cell_value(r, 10)

    return wb_stock_list, wb_prices


def build_prices_file(file_name, name, price):
    line_index = 0
    new_line = [""] * len(name)
    with open(file_name) as data:
        for line in data:
            line = line.rstrip("\n")
            if line == "xxx":
                new_line[line_index] = str(price[line_index])
            else:
                new_line[line_index] = str(line) + "\t" + str(price[line_index])
            line_index += 1

    open(file_name, 'w').close()

    prices_file = open(file_name, "w")
    for n in range(0, len(name)):
        prices_file.write(new_line[n])
        if n < len(name) - 1:
            prices_file.write("\n")
    prices_file.close()


def get_price_list_from_excel_files(stock_list, excel_files_path, price_list_file_path):
    build_preliminary_file(price_list_file_path, len(stock_list))
    excel_files_list = [f for f in listdir(excel_files_path) if isfile(join(excel_files_path, f))]

    print("Generating Prices File. Please Wait...")

    price_list = [[0 for x in range(len(excel_files_list))] for y in range(len(stock_list))]
    last_valid_price = [0 for x in range(len(stock_list))]

    excel_file_index = 0
    for excel_file in excel_files_list:
        current_price = [0] * len(stock_list)
        (wb_stocks, wb_prices) = get_work_book_info(excel_files_path + "/" + excel_file)

        for s in stock_list:
            if s in wb_stocks:
                if wb_prices[wb_stocks.index(s)] != 0:
                    current_price[stock_list.index(s)] = wb_prices[wb_stocks.index(s)]
                    last_valid_price[stock_list.index(s)] = wb_prices[wb_stocks.index(s)]
                elif wb_prices[wb_stocks.index(s)] == 0 and last_valid_price[stock_list.index(s)] != 0:
                    current_price[stock_list.index(s)] = last_valid_price[stock_list.index(s)]
                elif wb_prices[wb_stocks.index(s)] == 0 and last_valid_price[stock_list.index(s)] == 0:
                    current_price[stock_list.index(s)] = 0
            else:
                current_price[stock_list.index(s)] = last_valid_price[stock_list.index(s)]

        temp_stock_index = 0
        for pr in price_list:
            pr[excel_file_index] = current_price[temp_stock_index]
            temp_stock_index += 1
        excel_file_index += 1
        build_prices_file(price_list_file_path, stock_list, current_price)

    print("Done!")

    return price_list


def get_price_list_from_processed_file(processed_file_path, number_of_rows, number_of_columns):
    print("Loading Price List. Please Wait...")

    with open(processed_file_path, encoding="utf8") as data:
        price_list = [[0 for x in range(number_of_columns)] for y in range(number_of_rows)]
        row_index = 0
        for line in data:
            line = re.sub(" ", "_", str(line))
            part = line.split()
            for col_index in range(0, number_of_columns):
                price_list[row_index][col_index] = part[col_index]
            row_index += 1

    print("Done!")

    return price_list


def normalize_features(X, number_of_rows, number_of_columns):
    Z = np.zeros(shape=(number_of_rows, number_of_columns))

    Z[:, 0] = X[:, 0]
    for col in range(1, number_of_columns):
        Z[:, col] = (X[:, col] - np.mean(X, axis=0)[col]) / np.std(X, axis=0, ddof=1)[col]

    return Z


def build_linear_data_set(stock_id, price_list, number_of_rows, number_of_columns):
    X = [[0 for col in range(0, number_of_columns)] for row in range(0, number_of_rows)]
    Y = [0 for row in range(0, number_of_rows)]

    for row in range(0, number_of_rows):
        X[row][0] = 1
        for col in range(1, number_of_columns):
            X[row][col] = int(float(price_list[stock_id][row + col - 1]))

    for row in range(0, number_of_rows):
        Y[row] = int(float(price_list[stock_id][row + number_of_columns - 1]))

    build_test_text_file(X, Y, number_of_rows, number_of_columns)

    X = np.array(X)
    Y = np.array(Y)

    Normal_X = normalize_features(X, number_of_rows, number_of_columns)

    return Normal_X, Y


def build_test_text_file(X, Y, number_of_rows, number_of_columns):
    file_name = "text_files/test.txt"
    open("text_files/test.txt", 'w').close()
    line_index = 0
    new_line = [""] * number_of_rows
    for row in range(0, number_of_rows):
        for col in range(1, number_of_columns):
            new_line[row] = new_line[row] + str(X[row][col]) + ","
        new_line[row] = new_line[row] + str(Y[row])

    file = open(file_name, "w")
    for n in range(0, number_of_rows):
        file.write(new_line[n])
        if n < number_of_rows - 1:
            file.write("\n")
    file.close()


def build_real_linear_data_set(stock_id, price_list, number_of_rows, number_of_columns):
    Y = [0 for row in range(0, number_of_rows)]
    X = [[0 for col in range(0, number_of_columns)] for row in range(0, number_of_rows)]

    for row in range(number_of_columns - 1, number_of_rows):  # number of columns equals number of features + 1
        Y[row] = int(float(price_list[stock_id][row]))

    for row in range(number_of_columns - 1, number_of_rows):
        X[row][0] = 1
        for col in range(1, number_of_columns):
            X[row][col] = int(float(price_list[stock_id][row - number_of_columns + col]))

    return X, Y
