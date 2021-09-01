import pandas as pd
import sys
import time
import pprint as pp
from scipy import stats

from config.calculate import *

def print_dash():
    print()
    print("==============================================================================================================")
    print()

def calc_err(dpmo):
    rv = stats.norm(0, 1)

    if dpmo < 0.3:
        return 100.0

    else:
        sigma = abs(rv.ppf(dpmo/1000000)-1.5)

        if sigma <1.5:
            return round(sigma*50/1.5, 3)

        elif sigma > 6:
            return 100.0

        else:
            return round((sigma-1.5)*(49.9/4.5)+50, 3)

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
            err[3] += s['항목 유일성']
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
                   "항목 유일성 점수":result[3],
                   "데이터 제공 적시성 점수":result[4]}

    return return_dict

def main():
    
    config = pd.read_excel("컬럼정보받기.xlsx", sheet_name='Sheet1').to_numpy().tolist()
    df = pd.read_csv("1.csv")
    score = [{} for i in range(len(config))]
    i = 0
    for con in config:
        data = con[0]
        try:
            column = df.loc[:, data]    
        except:
            print("'컬럼정보받기.xlsx'의 'Sheet 1'에 입력한 '{0}' 컬럼이 '데이터파일.csv'에 존재하지 않음".format(data))

            sys.exit()

        data_type = con[1]
        range_check = con[2]
        form_check = con[5]
        cycle_check = con[6]
        cycle = con[7]
        unique_check = con[8]

        if data_type == '날짜/시간':
            column = pd.to_datetime(column)
           

        r = complete(df.iloc[:, i])      
        score[i].update({"항목 완전성": r})
        if range_check == 'Y' or range_check == 'y':
            if data_type == '날짜/시간':
                min = pd.to_datetime(con[3])
                max = pd.to_datetime(con[4])

            else:
                min = float(con[3])
                max = float(con[4])

            r = range_validate(column, min, max)
            score[i].update({"범위 유효성": r})

        if form_check == 'Y' or form_check == 'y':
            r = form_validate(column)
            score[i].update({"형식 유효성": r})
        
        if cycle_check == 'Y' or cycle_check == 'y':
            if data_type == '날짜/시간':
                cycle = pd.Timedelta(cycle)

            r = cycle_validate(column, cycle)
            score[i].update({"데이터 제공 적시성": r})

        if unique_check == 'Y' or unique_check == 'y':
            r = unique_validate(column)
            score[i].update({"항목 유일성": r})

        i += 1

    result = return_result(score, df.shape[0])
    print("                                         데이터 품질 평가 결과")
    print_dash()
    for item in result.items():
        if item[1] == '평가 안함':
            print("{0}:{1}".format(item[0], item[1]))
                    
        else:
            print("{0}:{1}점".format(item[0], item[1]))
    print_dash()

# def call_func(df , column, filename):
#     print("*주의* 잘못 입력 시 처음부터 다시 시작해야 될 수도 있음")
#     if column == 'all':#모든 데이터 평가
#         score = [{} for i in range(df.shape[1])]
#         for i in range(len(score)):
#             print_dash()       
#             print("평가할 열(column):{0}".format(df.columns[i]))
#             print("평가할 열(column)에 대해 적용할 지표를 입력")
#             print("항목 완전성은 모든 열(column)에 대해 평가")
#             r = complete(df.iloc[:, i])      
#             score[i].update({"항목 완전성": r})

#             while True:
#                 print("1 = 범위 유효성")
#                 print("2 = 형식 유효성")
#                 print("3 = 항목 유일성")
#                 print("4 = 데이터 제공 적시성")
#                 print("N = 다음 열(column)으로")
#                 a = input(":")
#                 if a == "N" or a == "n":
#                     break
                
#                 elif a == '1':
#                     r = range_validate(df.iloc[:, i])
#                     score[i].update({"범위 유효성": r})

#                 elif a == '2':
#                     r = form_validate(df.iloc[:, i])
#                     score[i].update({"형식 유효성": r})

#                 elif a == '3':
#                     r = unique(df.iloc[:, i])
#                     score[i].update({"항목 유일성": r})

#                 elif a == '4':
#                     print("주기에 대한 적시성을 판단: Y \n순서에 대한 적시성을 판단: N")
#                     a = input(":")
#                     if a == 'y' or a == 'Y':
#                         print("*주의* 데이터의 형태가 날짜일때 '날짜' 입력")
#                         a = input("주기를 알고 있음 Y/N :")
#                         if a == 'y' or a == 'Y':
#                             cycle = input("주기:")
#                             r = cycle_validate(df.iloc[:, i], float(cycle))
#                             score[i].update({"데이터 제공 적시성": r})

#                         elif a == "N" or a == "n":
#                             result = cycle_validate(df.iloc[:, i], 'dontknow')
#                             print("평가할 열(column) {0}의 최빈값, 최빈값 빈도, 최솟값, 평균 or 분포:".format(df.columns[i]))
#                             pp.pprint(result)

#                             while True:
#                                 print("최빈값, 최솟값, 평균에서 사용할 주기를 입력 혹은 직접 입력")
#                                 print("*주의* 데이터의 형태가 날짜일때 최빈값, 최솟값, 평균 중 하나를 입력")
#                                 print("예) 최빈값 사용시 '최빈값' 입력")
#                                 a = input(":")

#                                 if a == '최빈값':
#                                     r = len(df.iloc[:, i]) - result['최빈값 빈도']
#                                     score[i].update({"데이터 제공 적시성": r})
#                                     break

#                                 elif a == '최솟값':
#                                     r = cycle_validate(df.iloc[:, i], result['최솟값'])
#                                     score[i].update({"데이터 제공 적시성": r})
#                                     break

#                                 elif a == '평균':
#                                     r = cycle_validate(df.iloc[:, i], result['평균'])
#                                     score[i].update({"데이터 제공 적시성": r})
#                                     break

#                                 else:
#                                     try:
#                                         r = cycle_validate(df.iloc[:, i], float(a)) 
#                                         score[i].update({"데이터 제공 적시성": r})
#                                         break
                                    
#                                     except:
#                                         print("올바른 값을 입력")

#                         elif a == "날짜":
#                             col = pd.to_datetime(df.iloc[:, i])
#                             result = cycle_validate(col, 'dontknow')
#                             print("평가할 열(column) {0}의 최빈값, 최빈값 빈도, 최솟값, 평균 or 분포:".format(df.columns[i]))
#                             pp.pprint(result)

#                             while True:
#                                 print("최빈값, 최솟값, 평균 중 하나를 입력")
#                                 print("예) 최빈값 사용시 '최빈값' 입력")
#                                 a = input(":")

#                                 if a == '최빈값':
#                                     r = len(col) - result['최빈값 빈도']
#                                     score[i].update({"데이터 제공 적시성": r})
#                                     break

#                                 elif a == '최솟값':
#                                     r = cycle_validate(col, result['최솟값'])
#                                     score[i].update({"데이터 제공 적시성": r})
#                                     break

#                                 elif a == '평균':
#                                     r = cycle_validate(col, result['평균'])
#                                     score[i].update({"데이터 제공 적시성": r})
#                                     break

#                     if a == 'n' or a == "N":
#                         r = cycle_validate(df.iloc[:, i], 'sequence')
#                         score[i].update({"데이터 제공 적시성": r})
    
#     else:#선택한 데이터 평가
#         j = 0
#         score = [{} for i in range(len(column))]
#         for i in column:
#             print_dash()       
#             print("평가할 열(column):{0}".format(df.columns[i]))
#             print("평가할 열(column)에 대해 적용할 지표를 입력")
#             print("항목 완전성은 모든 열(column)에 대해 평가")
#             r = complete(df.iloc[:, i])      
#             score[j].update({"항목 완전성": r})

#             while True:
#                 print("1 = 범위 유효성")
#                 print("2 = 형식 유효성")
#                 print("3 = 항목 유일성")
#                 print("4 = 데이터 제공 적시성")
#                 print("N = 다음 열(column)으로")
#                 a = input(":")
#                 if a == "N" or a == "n":
#                     break
                
#                 elif a == '1':
#                     r = range_validate(df.iloc[:, i])
#                     score[j].update({"범위 유효성": r})

#                 elif a == '2':
#                     r = form_validate(df.iloc[:, i])
#                     score[j].update({"형식 유효성": r})

#                 elif a == '3':
#                     r = unique(df.iloc[:, i])
#                     score[j].update({"항목 유일성": r})

#                 elif a == '4':
#                     print("주기에 대한 적시성을 판단: Y \n순서에 대한 적시성을 판단: N")
#                     a = input(":")
#                     if a == 'y' or a == 'Y':
#                         print("*주의* 데이터의 형태가 날짜일때 '날짜' 입력")
#                         a = input("주기를 알고 있음 Y/N :")
#                         if a == 'y' or a == 'Y':
#                             cycle = input("주기:")
#                             r = cycle_validate(df.iloc[:, i], float(cycle))
#                             score[j].update({"데이터 제공 적시성": r})

#                         elif a == "N" or a == "n":
#                             result = cycle_validate(df.iloc[:, i], 'dontknow')
#                             print("평가할 열(column) {0}의 최빈값, 최빈값 빈도, 최솟값, 평균 or 분포:".format(df.columns[i]))
#                             pp.pprint(result)

#                             while True:
#                                 print("최빈값, 최솟값, 평균에서 사용할 주기를 입력 혹은 직접 입력")
#                                 print("*주의* 데이터의 형태가 날짜일때 최빈값, 최솟값, 평균 중 하나를 입력")
#                                 print("예) 최빈값 사용시 '최빈값' 입력")
#                                 a = input(":")

#                                 if a == '최빈값':
#                                     r = len(df.iloc[:, i]) - result['최빈값 빈도']
#                                     score[j].update({"데이터 제공 적시성": r})
#                                     break

#                                 elif a == '최솟값':
#                                     r = cycle_validate(df.iloc[:, i], result['최솟값'])
#                                     score[j].update({"데이터 제공 적시성": r})
#                                     break

#                                 elif a == '평균':
#                                     r = cycle_validate(df.iloc[:, i], result['평균'])
#                                     score[j].update({"데이터 제공 적시성": r})
#                                     break

#                                 else:
#                                     try:
#                                         r = cycle_validate(df.iloc[:, i], float(a)) 
#                                         score[j].update({"데이터 제공 적시성": r})
#                                         break
                                    
#                                     except:
#                                         print("올바른 값을 입력")

#                         elif a == "날짜":
#                             column = pd.to_datetime(df.iloc[:, i])
#                             result = cycle_validate(column, 'dontknow')
#                             print("평가할 열(column) {0}의 최빈값, 최빈값 빈도, 최솟값, 평균 or 분포:".format(df.columns[i]))
#                             pp.pprint(result)

#                             while True:
#                                 print("최빈값, 최솟값, 평균 중 하나를 입력")
#                                 print("예) 최빈값 사용시 '최빈값' 입력")
#                                 a = input(":")

#                                 if a == '최빈값':
#                                     r = len(column) - result['최빈값 빈도']
#                                     score[j].update({"데이터 제공 적시성": r})
#                                     break

#                                 elif a == '최솟값':
#                                     r = cycle_validate(column, result['최솟값'])
#                                     score[j].update({"데이터 제공 적시성": r})
#                                     break

#                                 elif a == '평균':
#                                     r = cycle_validate(column, result['평균'])
#                                     score[j].update({"데이터 제공 적시성": r})
#                                     break

#                     if a == 'n' or a == "N":
#                         r = cycle_validate(df.iloc[:, i], 'sequence')
#                         score[j].update({"데이터 제공 적시성": r})

#             j += 1

#     result = return_result(score, df.shape[0])
#     print("                                『{0}』파일에 대한 데이터 품질 평가".format(filename))
#     print_dash()
#     for item in result.items():
#         if item[1] == '평가 안함':
#             print("{0}:{1}".format(item[0], item[1]))
                    
#         else:
#             print("{0}:{1}점".format(item[0], item[1]))
#     print_dash()


# def main1():

#     print_dash()
#     print("평가할 파일이름을 확장자를 포함해서 입력\nex)인천대학교.csv")
#     print("*주의* 확장자가 csv와 xlsx인 파일만 지원하며 __main__.py 와 같은 폴더(경로)내에 저잗되어 있어야 함")
#     print_dash()

#     filename = input(":")
#     print("파일 불러오는 중...")

#     if ".csv" in filename :    
#         try:
#             df = pd.read_csv(filename)
#             print("파일 불러오기 성공")
            

#         except:
#             print("파일 불러오기 실패")            
#             print("*주의* 확장자가 csv와 xlsx인 파일만 지원하며 __main__.py 와 같은 폴더(경로)내에 저잗되어 있어야 함")
#             for i in range(5):
#                 print("{0}초 후 창이 꺼집니다.".format(5-i))
#                 time.sleep(1)

#             sys.exit()
    
#     elif ".xlsx" in filename :    
#         try:
#             df = pd.read_excel(filename)
#             print("파일 불러오기 성공")
            

#         except:
#             print("파일 불러오기 실패")            
#             print("*주의* 확장자가 csv와 xlsx인 파일만 지원하며 __main__.py 와 같은 폴더(경로)내에 저잗되어 있어야 함")
#             for i in range(5):
#                 print("{0}초 후 창이 꺼집니다.".format(5-i))
#                 time.sleep(1)

#             sys.exit()
    
#     else:
#         print("입력한 파일이 __main__.py와 같은 폴더(경로) 내에 없거나 파일 이름을 잘못 입력함")
#         main()
        
#     print("불러온 파일의 컬럼 개수:", df.shape[1])
#     print_dash()
#     print("평가할 열(column)의 순번(index)를 입력, 전부 평가할 시 Y입력")
#     print("잘못 입력시 잘못 입력한 순번(index)를 다시 입력")
#     print("평가할 열(column의 입력이 끝났으면 N입력")
#     print_dash()
    
#     column = []
 
#     while True:
#         a = input(":")
#         if a == "Y" or a == "y":
#             print("모든 열(column)을 평가Y/N?")
#             a = input(":")

#             if a == "Y" or a == "y":
#                 call_func(df , 'all', filename)
#                 break
            
#             elif a == "N" or a == "n":
#                 continue
            
#         elif a == "N" or a == "n":
#             print("평가할 열(column)의 개수:{0}".format(len(column)))
#             print("계속 입력 시 Y, 끝났을 시 N입력")
#             a = input(":")

#             if a == "Y" or a == "y":
#                 print("계속 입력")
#                 continue

#             elif a == "N" or a == "n":
#                 column.sort()
#                 call_func(df , column, filename)
#                 break

#             else:
#                 print("Y/N을 입력")

#         else:
#             try:
#                 if int(a)-1 not in column:
#                     column.append(int(a)-1)
#                     print("{0}번째 열(column) 추가:{1}".format(a, df.columns[int(a)-1]))

#                 elif int(a)-1 in column:
#                     column.remove(int(a)-1)
#                     print("{0}번째 열(column)이 평가할 항목에서 삭제:{1}".format(a, df.columns[int(a)-1]))

#             except:
#                 print("유효한 숫자를 입력하거나 N을 입력")
main()