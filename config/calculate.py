import pandas as pd
import datetime
import pprint as pp


def complete(col):
    return len(col)- col.count()

def range_validate(col):#범위
    validation = 0

    print("해당 데이터의 형태가 숫자: Y\n해당 데이터의 형태가 날짜: N")
    a = input(":")
    if a == "y" or a == "Y":
        min = float(input("최솟값:"))
        max = float(input("최댓값:"))
        
        for c in col:
            if c < min or c > max:
                validation += 1

        return validation

    if a == "n" or a == "N":
        print("날짜(시간)의 최대 최소를 입력")
        print("날짜 + 시간일때 YYYY-MM-DD hh:mm:ss의 형태")
        print("날짜일때 YYYY-MM-DD의 형태")
        print("시간일때 hh:mm:ss의 형태")
        
        while True:
            Min = input("최솟값:")
            try:
                if len(Min) == 19:
                    Min = datetime.datetime.strptime(Min, "%Y-%m-%d %H:%M:%S")
                    break
                elif len(Min) == 10:
                    Min = datetime.datetime.strptime(Min, "%Y-%m-%d")
                    break
                elif len(Min) == 8:
                    Min = datetime.datetime.strptime(Min, "%H:%M:%S")
                    break
                else:
                    print("유효한 값으로 다시 입력")
            except:
                print("유효한 형식으로 다시 입력")

        while True:
            Max = input("최댓값:")
            try:
                if len(Max) == 19:
                    Max = datetime.datetime.strptime(Max, "%Y-%m-%d %H:%M:%S")
                    break
                elif len(Max) == 10:
                    Max = datetime.datetime.strptime(Max, "%Y-%m-%d")
                    break
                elif len(Max) == 8:
                    Max = datetime.datetime.strptime(Max, "%H:%M:%S")
                    break
                else:
                    print("유효한 값으로 다시 입력")
            except:
                print("유효한 형식으로 다시 입력")
        
        for c in col:
            if c < Min or c > Max:
                validation += 1

        return validation

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
    lenth_list = []
    lenth_dict = {}

    for c in col:
        lenth = len(str(c))
        if lenth not in lenth_list:
            lenth_list.append(lenth)
            lenth_dict[lenth] = 1
        
        else:
            lenth_dict[lenth] += 1

    Mode = sorted(lenth_dict.items(), key = lambda x: -x[1])
    pp.pprint(Mode)
    
    return len(col)-Mode[0][1]

def cycle_validate(col, cycle):
    validation = 0
    j = 0
    gap = 0

    gap_list = []
    gap_count = {}
    
    if cycle == 'sequence':#순서판단
        for i in range(1, len(col)):
            if col[i-1] >= col[i]:
                validation += 1

        return validation
    
    elif cycle == 'dontknow':#정확한 주기 모를 때 
        for_ave = []

        for i in range(1, len(col)):
            gap = col[i]-col[i-1]
            for_ave.append(gap)

            if gap not in gap_list:
                gap_list.append(col[i]-col[i-1])
                gap_count[gap] = 1
            
            else:
                gap_count[gap] += 1 

        Mode = sorted(gap_count.items(), key = lambda x: -x[1])
        Min = min(gap_list)
        try:
            Ave = sum(for_ave)/len(for_ave)
            return_dict = {"최빈값":Mode[0][0],
                       "최빈값 빈도":Mode[0][1],
                       "최솟값":Min,
                       "평균":Ave}

            return return_dict

        except:
            return_dict = {"최빈값":Mode[0][0],
                        "최빈값 빈도":Mode[0][1],
                        "최솟값":Min,
                        "분포":Mode}

        return return_dict

    else:
        if type(col[0]) == int or type(col[0]) == float or type(col[0]) == str:
            for i in range(1, len(col)):#주기 입력시
                if float(col[j] + (i-j)*cycle) != float(col[i]):
                    validation += 1
                
                else:
                    j = i
        
        else:
            for i in range(1, len(col)):#주기 입력시
                if col[j] + (i-j)*cycle != col[i]:
                    validation += 1
                
                else:
                    j = i
        
        return validation

def unique(col):
    unique_itme = []
    unique_dict = {}

    for c in col:
        if c not in unique_itme:
            unique_itme.append(c)
            unique_dict[str(c)] = 1
        else:
            unique_dict[str(c)] += 1

    Mode = sorted(unique_dict.items(), key = lambda x:-x[1])
    pp.pprint(Mode)
    validation = len(col) - Mode[0][1]

    return validation