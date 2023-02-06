import pandas as pd
import csv
import numpy as np
import datetime
import dateutil.parser
from scipy import stats



def check_completness(column):
    """
    항목의 결측치 여부를 확인
    :param column: 검사를 진행할 데이터 항목
    :return: 평가받는 항목의 유효한 데이터 수, 오류 개수
    """
    err_count = column.isnull().sum()
    # print("전체", len(column), "개 데이터에서 완전성 위반개수 :", err_count)

    return len(column), err_count



def check_range(d_type, column, range_check, min_val, max_val):
    """
    항목의 범위 유효성 여부를 확인
    :param d_type: 항목의 데이터 타입
    :param column: 검사를 진행할 데이터 항목
    :param min_val: 최솟값
    :param max_val: 최댓값
    :return: 평가받는 항목의 유효한 데이터 수, 오류 개수
    """
    
    if range_check == 'Y':
        err_count = 0
        exc_count = 0
        empty_count = int(column.isnull().sum())
        column = column.values.tolist()

        ### 항목의 데이터 타입이 숫자일때
        if d_type == "숫자":

            for c in column:
                if pd.isna(c):
                    continue

                try:
                    c = float(c)

                except ValueError as e:
                    exc_count += 1
                    continue

                if c < float(min_val) or c > float(max_val):
                    err_count += 1

            return len(column)-empty_count-exc_count, err_count


        ### 항목의 데이터 타입이 날짜/시간 일때
        elif d_type == "날짜/시간":
            for c in column:
                if pd.isna(c):
                    continue

                try:
                    c = pd.to_datetime(str(c))

                except dateutil.parser.ParserError as e:
                    exc_count += 1
                    continue

                if c < pd.to_datetime(str(min_val)) or c > pd.to_datetime(str(max_val)):
                    err_count += 1

            return len(column)-empty_count-exc_count, err_count
            
        else:
            return 0, 0

    else:
        return 0, 0


def check_format(d_type, column, format_check, class_list):
    """
    항목의 형식 유효성을 판단
    :param d_type: 항목의 데이터 타입
    :param column: 검사를 진행할 데이터 항목
    :param format_check: 형식 유효성의 판단 유무
    :param class_list: 분류 목록(데이터 타입이 "분류"인경우)
                       데이터 타입이 분류인 경우 해당 항목의 값이 분류 목록에 없는 경우 형식 유효성 오류로 판단
    :return: 평가받는 항목의 유효한 데이터 수, 오류 개수
    """
    if format_check == 'Y':
        err_count = 0
        empty_count = int(column.isnull().sum())
        column = column.values.tolist()

        ### 데이터 타입이 숫자일 경우
        if d_type == '숫자':
            for c in column:
                if pd.isna(c):
                    continue

                try:
                    c = float(c)

                except ValueError as e:

                    err_count += 1

            return len(column) - empty_count, err_count


        ### 데이터 타입이 날짜/시간일 경우
        elif d_type == '날짜/시간':
            for c in column:
                if pd.isna(c):
                    continue

                try:
                    c = pd.to_datetime(str(c))
                except dateutil.parser.ParserError as e:

                    err_count += 1

            return len(column) - empty_count, err_count


        ### 데이터 타입이 분류일 경우
        elif d_type == '분류':
            class_list = class_list.split(',')
            for c in column:
                if pd.isna(c):
                    continue

                if str(c) not in class_list:
                    err_count += 1

            return len(column) - empty_count, err_count


        ### 데이터 타입이 문자일 경우
        else:
            return len(column) - empty_count, err_count

    else:

        return 0, 0


def check_unique(column, unique_check):
    """
    항목의 값들이 유일한 값이여야 하는 경우 유일성 검사
    :param column: 검사를 진행할 데이터 항목
    :param unique_check: 유일성 유무
    :return: 평가받는 항목의 유효한 데이터 수, 오류 개수
    """
    empty_count = int(column.isnull().sum())

    if unique_check == 'Y':
        column = column.dropna(axis=0)
        unique_num = len(column.unique().tolist())
        err_count = len(column) - unique_num

        return len(column) - empty_count, err_count

    else:
        return 0, 0


def check_cycle(d_type, column, cycle_check, cycle):
    """
    데이터 제공 적시성 평가
    :param d_type: 항목의 데이터 타입
    :param column: 검사를 진행할 데이터 항목
    :param cycle_check: 데이터 제공 적시성의 판단 유무
    :param cycle: 데이터의 제공 주기
    :return: 평가받는 항목의 유효한 데이터 수, 오류 개수
    """

    if cycle_check == 'Y':
        err_count = 0
        if d_type == '숫자':
            for c in range(len(column)):
                try:
                    column[c] = float(column[c])
                    if column[c] != column[0] + (c * float(cycle)):
                        err_count += 1

                except ValueError as e:
                    # print("주기를 판단할 수 없는 형식입니다.", e)
                    err_count += 1
                    continue

            return len(column), err_count

        ### d_type이 날짜/시간 일때
        else:
            for c in range(len(column)):
                try:
                    column[c] = pd.to_datetime(column[c])
                    if column[c] != column[0] + (c * pd.to_timedelta(cycle)):
                        err_count += 1

                except ValueError as e:
                    # print("주기를 판단할 수 없는 형식입니다.", e)
                    err_count += 1
                    continue

            return len(column), err_count
    else:
        return 0, 0


def get_score(result_list):
    """
    평가 지표별 평가 점수 계산
    :param result_list: 5가지 평가지표에 대한 컬럼별 평가개수, 오류개수 리스트
    :return: 5개의 평가지표 결과
    """

    com_total, com_err = 0, 0
    range_total, range_err = 0, 0
    form_total, form_err = 0, 0
    unique_total, unique_err = 0, 0
    cycle_total, cycle_err = 0, 0

    for i in result_list:
        com_total += i[0]
        com_err += i[1]

        range_total += i[2]
        range_err += i[3]

        form_total += i[4]
        form_err += i[5]

        unique_total += i[6]
        unique_err += i[7]

        cycle_total += i[8]
        cycle_err += i[9]

    ### 평가지표별 총 오류율
    if com_total == 0:
        compliteness_err = 'N/A'
    
    else:
        compliteness_err = com_err/com_total
    
    if range_total == 0:
        range_effectiveness_err = 'N/A'
    
    else:
        range_effectiveness_err = range_err/range_total
    
    if form_total == 0:
        format_validity_err = 'N/A'

    else:
        format_validity_err = form_err/form_total
    
    if unique_total == 0:
        uniqueness_err = 'N/A'

    else:
        uniqueness_err = unique_err/unique_total
    
    if cycle_total == 0:
        periodicity_err = 'N/A'

    else:
        periodicity_err = cycle_err/cycle_total

    err_rate_list ={"항목 완전성":compliteness_err,
                    "범위 유효성":range_effectiveness_err,
                    "형식 유효성":format_validity_err,
                    "항목 유일성":uniqueness_err,
                    "데이터 제공 적시성":periodicity_err}

    rv = stats.norm(0, 1)

    score_list = {}
    for err in err_rate_list.items():
        if err[1] == 'N/A':
            score_list[err[0]] = err[1]
        
        else:
            dpmo = err[1] * 1000000

            if dpmo <= 3.4:
                score_list[err[0]] = 100.0

            elif dpmo > 933192:
                score_list[err[0]] = 0

            else:
                sigma = rv.ppf(1-err[1])+1.5

                if sigma <1.5:
                    score_list[err[0]] = round(sigma*50/1.5, 3)

                elif sigma >= 6:
                    score_list[err[0]] = 100.0

                else:
                    score_list[err[0]] = round((sigma-1.5)*(49.9/4.5)+50, 3)

    return score_list