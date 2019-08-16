#! /usr/bin/env python
# -*- coding: utf-8 -*-

# https://github.com/se55i0n/Webfinger/raw/master/lib/web.db

import re
import json
import sqlite3

re_body_pattern = re.compile(r'body\s*=+\s*\"(.*)\"')
re_title_pattern = re.compile(r'title\s*=+\s*\"(.*)\"')
re_header_pattern = re.compile(r'header\s*=+\s*\"(.*)\"')


def gen_rule(rule):
    re_result = re_body_pattern.findall(rule)
    if re_result:
        return {
            "search": "body",
            "text": re_result[0]
        }
    re_result = re_header_pattern.findall(rule)
    if re_result:
        return {
            "search": "headers",
            "text": re_result[0]
        }
    re_result = re_title_pattern.findall(rule)
    if re_result:
        return {
            "search": "title",
            "regexp": re_result[0]
        }


conn = sqlite3.connect('web.db')
cur = conn.cursor()
result = cur.execute("select * from fofa")

all_rules = {}
for i in result:
    name = i[1].strip()
    r = i[2].strip()

    x = {
        "name": name,
        "author": "fofa",
        "version": "0.1.0",
        "matches": [],
    }
    if not r.strip():
        continue

    if '||' not in r and '&&' not in r:
        # 只有一个
        rule = gen_rule(r.strip())
        if not rule:
            continue

        x['matches'].append(rule)

    elif '||' in r and '&&' not in r:
        spliter = r.split('||')
        for i in spliter:
            rule = gen_rule(i.strip())
            if not rule:
                continue

            x['matches'].append(rule)

    elif '&&' in r and '||' not in r:
        spliter = r.split('&&')
        invalid = False

        for i in spliter:
            rule = gen_rule(i.strip())
            if not rule:
                invalid = True
                break

            x['matches'].append(rule)

        if invalid:
            continue

        x['condition'] = ''
        for i in range(len(spliter) - 1):
            x['condition'] += str(i) + ' and '

        x['condition'] += str(len(spliter) - 1)

    else:
        xb = []
        invalid = False
        for i in r.split('&&'):
            ib = []
            for j in i.split('||'):
                j = j.strip()
                if j.startswith('('):
                    ib.append('(0')
                    d = j[1:]
                elif j.endswith(')'):
                    ib.append('0)')
                    d = j[:-1]
                else:
                    ib.append('0')
                    d = j

                rule = gen_rule(d)

                if not rule:
                    invalid = True
                    break

                x['matches'].append(rule)

            if invalid:
                break

            xb.append(' or '.join(ib))

        if invalid:
            continue

        condition = list(' and '.join(xb))

        index = 0
        for i, v in enumerate(condition):
            if v == '0':
                condition[i] = str(index)
                index += 1

        x['condition'] = ''.join(condition)

    if not x['matches']:
        continue

    with open('rules/fofa/{}.json'.format(x['name'].replace('/', '_')), 'w') as fd:
        json.dump(x, fp=fd, indent=4)
