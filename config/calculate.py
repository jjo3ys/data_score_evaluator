import pandas as pd
import datetime
import pprint as pp


def complete(col, dtype):
    if dtype == '문자':
        validation = 0
        for c in col:
            if str(c) == 'nan': 
                validation += 1
        
        return validation

    else:
        return len(col)- col.count()

def range_validate(col, min, max):#범위
    validation = 0
    exception = 0

    for c in col:
        try:
            if c < min or c > max:
                validation += 1
            else:
                validation = validation

        except TypeError as e:
            # print(e, c, type(c))
            exception += 1

    return validation, exception

def divde_validate(col, divide):
    validation = 0

    for c in col:
        if str(c) not in divide:
            validation += 1

    return validation

def form_validate(col):
    type_list = []
    type_dict = {}

    for c in col:
        data_type = str(type(c))
        if data_type not in type_list:
            type_list.append(data_type)
            type_dict[data_type] = 1
        
        else:
            type_dict[data_type] += 1

    Mode = sorted(type_dict.items(), key = lambda x: -x[1])

    return len(col)-Mode[0][1]

def cycle_validate(col, cycle, data_type):
    validation = 0
    exception = 0
    j = 0

    if data_type == 'sequence':#순서판단
        for i in range(1, len(col)):
            if col[i-1] >= col[i]:
                validation += 1

        return validation
    
    elif data_type == '숫자':
        c_ans = col[0]
        for i in range(1, len(col)):
            try:
                if float(c_ans + cycle) != float(col[i]) and float(col[i-1] + cycle) != float(col[i]):
                    validation += 1
                    c_ans = c_ans + cycle
                else:
                    c_ans = c_ans + cycle

            except ValueError:
                exception += 1

        return validation, exception


    elif data_type == '날짜/시간':
        c_ans = col[0]
        for i in range(1, len(col)):
            try:
                if c_ans + cycle != col[i] and col[i-1] + cycle != col[i]:
                    validation += 1
                    c_ans = c_ans + cycle
                else:
                    c_ans = c_ans + cycle

            except TypeError as e:
                    exception += 1
        
        return validation, exception

def unique_validate(col):
    unique_itme = []
    unique_dict = {}

    for c in col:
        if c not in unique_itme:
            unique_itme.append(c)
            unique_dict[str(c)] = 1
        else:
            unique_dict[str(c)] += 1

    Mode = sorted(unique_dict.items(), key = lambda x:-x[1])
    validation = len(col) - Mode[0][1]

    return validation