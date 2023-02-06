import pandas as pd
import numpy as np
from func.evaluator import *
import sys
import time

import warnings

def print_dash():
    print()
    print("==============================================================================================================")
    print()

def data_loader(file_name):

    try:
        df = pd.read_csv(file_name, encoding='cp949')
        
        return df, 0
    
    except UnicodeDecodeError:
        df = pd.read_csv(file_name, encoding='utf-8')

        return df, 0
        
    except FileNotFoundError as e:
        print()
        print("====  해당 파일이 존재하지 않습니다. ==== \n")
        print()
        print("파일명 :", file_name)
        print()

        return None, 1
    
    

def config_loader(file_name):
    if '.xlsx' in file_name:
        try:
            df = pd.read_excel(file_name, sheet_name="Sheet1", index_col=0)
            df.dropna(axis=0, how='all', inplace=True)
                    
            return df, 0

        except FileNotFoundError as e:
            print()
            print("====  해당 파일이 존재하지 않습니다. ==== \n")
            print()
            print("파일명 :", file_name)
            print()

            return None, 1
    
    elif '.csv' in file_name:
        try:
            df = pd.read_csv(file_name, index_col=0, encoding='cp949')
            df.dropna(axis=0, how='all', inplace=True)
                    
            return df, 0
        
        except UnicodeDecodeError:
            df = pd.read_csv(file_name, index_col=0, encoding='utf-8')
            df.dropna(axis=0, how='all', inplace=True)
                    
            return df, 0
            
        except FileNotFoundError as e:
            print()
            print("====  해당 파일이 존재하지 않습니다. ==== \n")
            print()
            print("파일명 :", file_name)
            print()

            return None, 1

def makecsv(file_name, index):
    header = ['항목별 속성', '범위 유효성 유무', '최솟값', '최댓값', '형식 유효성 유무', '분류 목록', '주기 유무', '주기', '유일성 유무']

    csv_list = [['문자', 'N', '', '', 'Y', '', 'N', '', 'N'] for i in range(len(index))]

    df = pd.DataFrame(csv_list, index=index, columns=header)
    df.to_csv('컬럼정보받기_{0}'.format(file_name), sep=',', encoding='cp949')

def main():
    """
    메인페이지를 실행하고 실행에 필요한 파일들을 입력받음
    :return:
    """
    while True:
        print("파일명을 확장자까지 포함해서 입력\n예) 인천대학교.csv")
        file_name = input(":")
        try:
            df, return_code = data_loader(file_name)
        except TypeError:
            print("====     파일명을 올바르게 입력     ====")
            print()
            continue
        
        if return_code == 1:
            print("====     파일명을 올바르게 입력     ====")
            print()
        
        else: 
            break
  

    data_columns = df.columns.tolist()

    while True:
        print("컬럼정보받기_{0} 파일을 생성하시겠습니까? Y/N".format(file_name))
        ans = input(":")

        if ans == 'Y' or ans == 'y':
            print("\n컬럼정보받기_{0} 파일을 생성중입니다.".format(file_name))
            makecsv(file_name, data_columns)
            print_dash()
            print("같은 폴더 내에 생성된 컬럼정보받기_{0} 파일을\n 확인하여 설정을 변경하시기 바랍니다.".format(file_name))
            print_dash()
            break
    
        elif ans == 'N' or ans == 'n':
            break

    while True:
        print("컬럼별 정보를 받는 파일명을 확장자까지 포함해서 입력\n예) 컬럼정보받기_기업A.csv")
        config_name = input(":")
        try:
            data_info, return_code = config_loader(config_name)
        except TypeError:
            print("====     파일명을 올바르게 입력     ====")
            print()
            continue

        if return_code == 1:
            print("====     파일명을 올바르게 입력     ====")
            print()

        else:
            break

    InfoTable_columns = data_info.index.values.tolist()

    

    if data_columns != InfoTable_columns:

        print("=======  두 파일의 항목(컬럼)명이 일치하지 않습니다.. =======")
        print("<", str(file_name), ">", "파일의 항목명 & <{0}> 의 항목명이 일치하는지 확인해주세요.".format(config_name))
        for s in range(5):
            print("{0}초 후에 프로그램이 종료됩니다.".format(5 - s))
            time.sleep(1)
        sys.exit()


    result_list = []
    for i in range(len(data_columns)):

        col_name = data_columns[i]
        column = df.loc[:, col_name]

        print("="*30, col_name, "컬럼", "="*30)

        d_type = data_info.loc[col_name, '항목별 속성']
        range_check = data_info.loc[col_name, '범위 유효성 유무']
        min_val = data_info.loc[col_name, '최솟값']
        max_val = data_info.loc[col_name, '최댓값']
        format_check = data_info.loc[col_name, '형식 유효성 유무']
        class_list = data_info.loc[col_name, "분류 목록"]
        cycle_check = data_info.loc[col_name, '주기 유무']
        cycle = data_info.loc[col_name, '주기']
        unique_check = data_info.loc[col_name, '유일성 유무']


        com_total, com_err = check_completness(column)
        range_total, range_err = check_range(d_type, column, range_check, min_val, max_val)
        form_total, form_err = check_format(d_type, column, format_check, class_list)
        unique_total, unique_err = check_unique(column, unique_check)
        cycle_total, cycle_err = check_cycle(d_type, column, cycle_check, cycle)


        result_list.append([com_total, com_err,
                            range_total, range_err,
                            form_total, form_err,
                            unique_total, unique_err,
                            cycle_total, cycle_err])

    score = get_score(result_list)
    print()
    print()
    print()
    print("                              '{0}'의 데이터 품질 평가 결과".format(file_name))
    print_dash()
    for item in score.items():
        if item[1] == 'N/A':
            print("{0}:{1}".format(item[0], item[1]))
                    
        else:
            print("{0}:{1}점".format(item[0], item[1]))
    print_dash()

    return 0


warnings.filterwarnings('ignore')
while True:
    return_code = main()
    if return_code == 1:
        continue
    else:
        pass

    a = input("다른 기업에 대해 품질평가를 진행할 시 enter 입력\n프로그램 종료 시 '종료' 입력:")
    if a == '종료':
        break
    print_dash()