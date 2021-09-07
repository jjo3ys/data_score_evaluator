import pandas as pd
import sys
import time
import dateutil.parser
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
    exception_count = [0, 0, 0, 0, 0]

    for s in score:
        try:
            err[0] += s['항목 완전성']
            test_count[0] += 1
        except:
            pass

        try:
            err[1] += s['범위 유효성']
            exception_count[1] += s['범위 유효성 예외']
            test_count[1] += 1
        except:
            pass

        try:
            err[2] += s['형식 유효성']
            exception_count[2] += s['형식 유효성 예외']
            test_count[2] += 1
        except:
            pass

        try:
            err[3] += s['항목 유일성']
            exception_count[3] += s['항목 유일성 예외']
            test_count[3] += 1
        except:
            pass

        try:
            err[4] += s['데이터 제공 적시성']
            exception_count[4] += s['데이터 제공 적시성 예외']
            test_count[4] += 1
        except:
            pass

    for i in range(5):
        if test_count[i] == 0:
            result.append('평가 안함')
            continue

        dpmo = err[i]/(test_count[i]*len_data - exception_count[i])*1000000
        
        r = calc_err(dpmo)
        result.append(r)
    # print(err, test_count, exception_count)
    return_dict = {"항목 완전성 점수":result[0],
                   "범위 유효성 점수":result[1],
                   "형식 유효성 점수":result[2],
                   "항목 유일성 점수":result[3],
                   "데이터 제공 적시성 점수":result[4]}

    return return_dict

def main():
    print("파일명을 확장자까지 포함해서 입력\n예) 인천대학교.csv")
    filename = input(":")

    config = pd.read_excel("컬럼정보받기.xlsx", sheet_name='Sheet1')
    config.dropna(axis=0, how='all', inplace=True)
    config = config.to_numpy().tolist()
    
    df = pd.read_csv(filename)

    score = [{} for i in range(len(config))]
    i = 0
    
    for con in config:
        data = con[0]
        try:
            column = df.loc[:, data].to_numpy().tolist()    
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
        cycle_check = con[7]
        cycle = con[8]
        unique_check = con[9]

        if data_type == '날짜/시간':
            for k in range(len(column)):
                try:
                    column[k] = pd.to_datetime(column[k])

                except dateutil.parser.ParserError:
                    continue

        elif data_type == '숫자':
            for k in range(len(column)):
                try:
                    column[k] = float(column[k])

                except ValueError:
                    continue
        
        elif data_type == '문자':
            for k in range(len(column)):
                try:
                    column[k] = float(column[k])

                except ValueError:
                    column[k] = str(column[k])


        perf = complete(df.loc[:, data], data_type)  
        score[i].update({"항목 완전성": perf})

        if range_check == 'Y':
            if data_type == '날짜/시간':
                Min = pd.to_datetime(con[3])
                Max = pd.to_datetime(con[4])

            else:
                Min = float(con[3])
                Max = float(con[4])

            r, e = range_validate(column, Min, Max)
            score[i].update({"범위 유효성": max(r - e, 0),
                             "범위 유효성 예외": e})

        if form_check == 'Y':
            if data_type == '분류':
                divide = con[6].split(',')
                r = divde_validate(column, divide)
                score[i].update({"형식 유효성": max(r - perf, 0),
                                 "형식 유효성 예외": perf})
            
            else:
                r = form_validate(column)
                score[i].update({"형식 유효성": max(r - perf, 0),
                                "형식 유효성 예외": perf})
        
        if cycle_check == 'Y':
            if data_type == '날짜/시간':
                cycle = pd.Timedelta(cycle)
                r, e = cycle_validate(column, cycle, data_type)
                score[i].update({"데이터 제공 적시성": r,
                                 "데이터 제공 적시성 예외": e})

            else:
                r, e = cycle_validate(column, cycle, data_type)
                score[i].update({"데이터 제공 적시성": max(r - perf, 0),
                                 "데이터 제공 적시성 예외": perf + e})

        if unique_check == 'Y':
            r = unique_validate(column)
            score[i].update({"항목 유일성": max(r - perf, 0),
                             "항목 유일성 예외" : perf})
        
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
        a = input("종료 입력시 종료:")
        if a == '종료':
            break
        
main()