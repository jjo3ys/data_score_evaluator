import pandas as pd
import datetime
import pprint as pp


def complete(col):
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

def code_validate(col):
    print("코드의 모든 종류를 입력 공백(spacebar)로 구분")
    Range = input(":").split()
    Range = list(map(float, Range))
    validation = 0
    for c in col:
        if c not in Range:
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

def cycle_validate(col, cycle, perf):
    validation = 0
    exception = 0
    j = 0

    if cycle == 'sequence':#순서판단
        for i in range(1, len(col)):
            if col[i-1] >= col[i]:
                validation += 1

        return validation
    
    else:
        if type(col[0]) == int or type(col[0]) == float:
            c_ans = col[0]
            for i in range(1, len(col)):
                try:
                    if float(c_ans + cycle) != float(col[i]) and float(col[i-1] + cycle) != float(col[i]):
                        validation += 1
                        c_ans = c_ans + cycle
                    else:
                        c_ans = c_ans + cycle

                except TypeError as e:
                    # print("에러났어요", e)
                    exception += 1

            return validation, exception + perf

        else:
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