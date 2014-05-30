#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from decimal import Decimal
from datetime import date, datetime

from pandas import DataFrame, date_range, tslib, concat


def fix_type(value):
    if type(value) is str:
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin1')
    elif type(value) is tslib.Timestamp:
        try:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime(1900, 01, 01, 00, 00, 00).strftime()
    elif type(value) is date or type(value) is datetime:
        try:
            return value.strftime("%Y-%m-%d")
        except ValueError:
            return datetime(1900, 01, 01).strftime()
    elif type(value) is Decimal:
        return float(value)
    return value


def fix_render(_l):
    return dict(map(lambda (k, v): (k, fix_type(v)), _l.iteritems()))


def df_generate(df, value, str_field):
    s = str_field.split('__')
    field = s[1]
    try:
        operator = s[2]
    except:
        operator = "is"

    try:
        t = s[3]
        if t == "int" and operator not in ["in", "notin", "between"]:
            value = int(value)
    except:
        t = "str"

    if t == "date":
        try:
            mark = s[4].replace(":", "%")
        except:
            mark = "%Y-%m-%d"
    elif t == "datetime":
        mark = "%Y-%m-%d %H:%M:%S"

    if operator == "gte":
        return u"{} >= {}".format(field, value)
    elif operator == "lte":
        return u"{} <= {}".format(field, value)
    elif operator == "is":
        if t == 'int':
            return u"{} == {}".format(field, value)
        return u"{} == '{}'".format(field, value)
    elif operator == "in":
        if t == 'int':
            return u"{} in {}".format(field,
                                      [int(i) for i in value.split(',')])
        return u"{} in {}".format(field, [i for i in value.split(',')])
    elif operator == "notin":
        if t == 'int':
            return u"{} not in {}".format([int(i) for i in value.split(',')],
                                          field)
        return u"{} not in {}".format([i for i in value.split(',')], field)
    elif operator == "between":
        _range = []
        between = value.split(":")

        if t == "date":
            _range = [i.strftime(mark)
                      for i in date_range(between[0], between[1]).tolist()]
        elif t == "datetime":
            _range = [i.strftime(mark)
                      for i in
                      date_range(between[0], between[1], freq="S").tolist()]
        elif t == "int":
            _range = [i for i in xrange(int(between[0]), int(between[1]) + 1)]

        return u"{} in {}".format(field, _range)


def DataFrameSearchColumn(df, colName, value, operator='like'):
    ndf = DataFrame()
    for idx, record in df[colName].iteritems():
        check = True
        if operator == 'like' and value in str(record):
            check = True

        if operator == 'regex' and re.search(value, str(record)):
            check = True

        if check:
            ndf = concat([df[df[colName] == record], ndf], ignore_index=True)

    return ndf