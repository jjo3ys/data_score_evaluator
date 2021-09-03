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
    print("파일명을 확장자까지 포함해서 입력\n예) 인천대학교.csv")
    filename = input(":")

    config = pd.read_excel("컬럼정보받기.xlsx", sheet_name='Sheet1').to_numpy().tolist()
    df = pd.read_csv(filename)

    score = [{} for i in range(len(config))]
    i = 0

    for con in config:
        data = con[0]
        try:
            column = df.loc[:, data]    
            print("'{0}' 컬럼의 평가가 진행중...{1}/{2}".format(data, i+1, len(config)))
        except:
            print("'컬럼정보받기.xlsx'의 'Sheet 1'에 입력한 '{0}' 컬럼이 '데이터파일.csv'에 존재하지 않음".format(data))
            for i in range(5):
                print("{0}초 후에 프로그램이 종료됩니다.".format(5-i))
                time.sleep(1)
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
    print("                              '{0}'의 데이터 품질 평가 결과".format(filename))
    print_dash()
    for item in result.items():
        if item[1] == '평가 안함':
            print("{0}:{1}".format(item[0], item[1]))
                    
        else:
            print("{0}:{1}점".format(item[0], item[1]))
    print_dash()

    while True:
        a = input("exit 입력시 종료:")
        if a == 'exit' or a == "EXIT":
            break
        
main()