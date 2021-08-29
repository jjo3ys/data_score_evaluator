import pandas as pd
import sys
import time
import pprint as pp
from scipy import stats

from config.calculate import *

def print_dash():
    for i in range(2):
        print("--------------------------------------------------------------------------------------------------------------")

def calc_err(dpmo):
    rv = stats.norm(0, 1)

    if dpmo < 0.3:
        return 100

    else:
        sigma = abs(rv.ppf(dpmo/1000000)-1.5)

        if sigma <1.5:
            return sigma*50/1.5

        elif sigma > 6:
            return 100

        else:
            return (sigma-1.5)*(49.9/4.5)+50

def return_result(score, len_data):
    result = []
    err = [0, 0, 0, 0, 0]
    test_count = [0, 0, 0, 0, 0]

    for s in score:
        try:
            err[0] += s['항목 완전성']
            test_count[0] += 1
        except:
            pass

        try:
            err[1] += s['범위 유효성']
            test_count[1] += 1
        except:
            pass

        try:
            err[2] += s['형식 유효성']
            test_count[2] += 1
        except:
            pass

        try:
            err[3] += s['코드 유효성']
            test_count[3] += 1
        except:
            pass

        try:
            err[4] += s['데이터 제공 적시성']
            test_count[4] += 1
        except:
            pass

    for i in range(5):
        if test_count[i] == 0:
            result.append('평가 안함')
            continue

        dpmo = err[i]/(test_count[i]*len_data)*1000000
        
        r = calc_err(dpmo)
        result.append(r)
    
    return_dict = {"항목 완전성 점수":result[0],
                   "범위 유효성 점수":result[1],
                   "형식 유효성 점수":result[2],
                   "코드 유효성 점수":result[3],
                   "데이터 제공 적시성 점수":result[4]}

    return return_dict

    
def call_func(df , column):
    print("*주의* 잘못 입력 시 처음부터 다시 시작해야 될 수도 있음")
    if column == 'all':#모든 데이터 평가
        score = [{} for i in range(df.shape[1])]
        for i in range(len(df.columns)):
            print_dash()
            print("평가할 열(column):{0}".format(df.columns[i]))
            print("평가할 열(column)에 대해 적용할 지표를 입력")
            print("항목 완전성은 모든 열(column)에 대해 평가")
            r = complete(df.iloc[:, i])
            score[i].update({"항목 완전성": r})
            while True:
                print("1 = 항목 완전성")
                print("2 = 범위 유효성")
                print("3 = 형식 유효성")
                print("4 = 코드 유효성")
                print("5 = 데이터 제공 적시성")
                print("N = 다음 열(column)으로")
                a = input(":")
                if a == "N" or a == "n":
                    break

                elif a == '1':
                    r = range_validate(df.iloc[:, i])
                    score[i].update({"범위 유효성": r})

                elif a == '2':
                    r = form_validate(df.iloc[:, i])
                    score[i].update({"형식 유효성": r})
                    pass

                elif a == '3':
                    r = code_validate(df.iloc[:, i])
                    score[i].update({"코드 유효성":r})

                elif a == '4':
                    print("주기에 대한 적시성을 판단: Y \n순서에 대한 적시성을 판단: N")
                    a = input(":")
                    if a == 'y' or a == 'Y':
                        print("*주의* 데이터의 형태가 날짜일때 N 입력")
                        a = input("주기를 알고 있음 Y/N :")
                        if a == 'y' or a == 'Y':
                            cycle = input("주기:")
                            r = cycle_validate(df.iloc[:, i], float(cycle))
                            score[i].update({"데이터 제공 적시성": r})

                        elif a == "N" or a == "n":
                            result = cycle_validate(df.iloc[:, i], 'dontknow')
                            print("평가할 열(column) {0}의 최빈값, 최빈값 빈도, 최솟값, 평균:".format(df.columns[i]))
                            print(result)

                            while True:
                                print("최빈값, 최솟값, 평균에서 사용할 주기를 입력 혹은 직접 입력")
                                print("*주의* 데이터의 형태가 날짜일때 최빈값, 최솟값, 평균 중 하나를 입력")
                                print("예) 최빈값 사용시 '최빈값' 입력")
                                a = input(":")

                                if a == '최빈값':                                   
                                    r = cycle_validate(df.iloc[:, i], result['최빈값']) 
                                    score[i].update({"데이터 제공 적시성": r})
                                    break

                                elif a == '최솟값':
                                    r = cycle_validate(df.iloc[:, i], result['최솟값'])
                                    score[i].update({"데이터 제공 적시성": r})
                                    break

                                elif a == '평균':
                                    r = cycle_validate(df.iloc[:, i], result['평균']) 
                                    score[i].update({"데이터 제공 적시성": r})
                                    break

                                else:
                                    try:
                                        r = cycle_validate(df.iloc[:, i], float(a)) 
                                        score[i].update({"데이터 제공 적시성": r})
                                        break
                                    
                                    except:
                                        print("올바른 값을 입력")

                    if a == 'n' or a == "N":
                        r = cycle_validate(df.iloc[:, i], 'sequence')
                        score[i].update({"데이터 제공 적시성": r})
    
    else:#선택한 데이터 평가
        j = 0
        score = [{} for i in range(len(column))]
        for i in column:
            print_dash()       
            print("평가할 열(column):{0}".format(df.columns[i]))
            print("평가할 열(column)에 대해 적용할 지표를 입력")
            print("항목 완전성은 모든 열(column)에 대해 평가")
            r = complete(df.iloc[:, i])      
            score[j].update({"항목 완전성": r})

            while True:
                print("1 = 범위 유효성")
                print("2 = 형식 유효성")
                print("3 = 코드 유효성")
                print("4 = 데이터 제공 적시성")
                print("N = 다음 열(column)으로")
                a = input(":")
                if a == "N" or a == "n":
                    break
                
                elif a == '1':
                    r = range_validate(df.iloc[:, i])
                    score[j].update({"범위 유효성": r})

                elif a == '2':
                    r = form_validate(df.iloc[:, i])
                    score[i].update({"형식 유효성": r})

                elif a == '3':
                    r = code_validate(df.iloc[:, i])
                    score[j].update({"코드 유효성": r})

                elif a == '4':
                    print("주기에 대한 적시성을 판단: Y \n순서에 대한 적시성을 판단: N")
                    a = input(":")
                    if a == 'y' or a == 'Y':
                        print("*주의* 데이터의 형태가 날짜일때 N 입력")
                        a = input("주기를 알고 있음 Y/N :")
                        if a == 'y' or a == 'Y':
                            cycle = input("주기:")
                            r = cycle_validate(df.iloc[:, i], float(cycle))
                            score[j].update({"데이터 제공 적시성": r})

                        elif a == "N" or a == "n":
                            result = cycle_validate(df.iloc[:, i], 'dontknow')
                            print("평가할 열(column) {0}의 최빈값, 최빈값 빈도, 최솟값, 평균:".format(df.columns[i]))
                            pp.pprint(result)

                            while True:
                                print("최빈값, 최솟값, 평균에서 사용할 주기를 입력 혹은 직접 입력")
                                print("*주의* 데이터의 형태가 날짜일때 최빈값, 최솟값, 평균 중 하나를 입력")
                                print("예) 최빈값 사용시 '최빈값' 입력")
                                a = input(":")

                                if a == '최빈값':
                                    r = cycle_validate(df.iloc[:, i], result['최빈값']) 
                                    score[j].update({"데이터 제공 적시성": r})
                                    break

                                elif a == '최솟값':
                                    r = cycle_validate(df.iloc[:, i], result['최솟값'])
                                    score[j].update({"데이터 제공 적시성": r})
                                    break

                                elif a == '평균':
                                    r = cycle_validate(df.iloc[:, i], result['평균'])
                                    score[j].update({"데이터 제공 적시성": r})
                                    break

                                else:
                                    try:
                                        r = cycle_validate(df.iloc[:, i], float(a)) 
                                        score[j].update({"데이터 제공 적시성": r})
                                        break
                                    
                                    except:
                                        print("올바른 값을 입력")

                    if a == 'n' or a == "N":
                        r = cycle_validate(df.iloc[:, i], 'sequence')
                        score[j].update({"항목 완전성": r})

            j += 1

    result = return_result(score, df.shape[0])
    pp.pprint(result)    


def main():

    print_dash()
    print("*주의* 평가할 excel은 확장자가 csv 혹은 xlsx 이어야 하고,\nmain.py와 같은 폴더(경로)내에 1.csv 혹은 1.xlsx 으로 저장되어 있어야 함")
    print_dash()
    print("파일 불러오는 중...")
    while True:
        try:
            df = pd.read_csv("1.csv")
            print("파일 불러오기 성공")
            break

        except:
            pass

        try:
            df = pd.read_excel("1.xlsx")
            print("파일 불러오기 성공")
            break

        except:
            print("파일 불러오기 실패")
            print("*주의* 평가할 excel은 확장자가 csv 혹은 xlsx 이어야 하고,\nmain.py와 같은 폴더(경로)내에 1.csv 혹은 1.xlsx 으로 저장되어 있어야 함")
            for i in range(5):
                print("{0}초 후 창이 꺼집니다.".format(5-i))
                time.sleep(1)

            sys.exit()
        
    print("불러온 파일의 컬럼 개수:", df.shape[1])
    print_dash()
    print("평가할 열(column)의 순번(index)를 입력, 전부 평가할 시 Y입력")
    print("잘못 입력시 잘못 입력한 순번(index)를 다시 입력")
    print("평가할 열(column의 입력이 끝났으면 N입력")
    print_dash()
    
    column = []
 
    while True:
        a = input(":")
        if a == "Y" or a == "y":
            print("모든 열(column)을 평가Y/N?")
            a = input(":")

            if a == "Y" or a == "y":
                call_func(df , 'all')
                break
            
            elif a == "N" or a == "n":
                continue
            
        elif a == "N" or a == "n":
            print("평가할 열(column)의 개수:{0}".format(len(column)))
            print("계속 입력 시 Y, 끝났을 시 N입력")
            a = input(":")

            if a == "Y" or a == "y":
                print("계속 입력")
                continue

            elif a == "N" or a == "n":
                column.sort()
                call_func(df , column)
                break

            else:
                print("Y/N을 입력")

        else:
            try:
                if int(a)-1 not in column:
                    column.append(int(a)-1)
                    print("{0}번째 열(column) 추가:{1}".format(a, df.columns[int(a)-1]))

                elif int(a)-1 in column:
                    column.remove(int(a)-1)
                    print("{0}번째 열(column)이 평가할 항목에서 삭제:{1}".format(a, df.columns[int(a)-1]))

            except:
                print("유효한 숫자를 입력하거나 N을 입력")
main()