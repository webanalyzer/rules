#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json


def parse_value(value):
    if isinstance(value, str):
        value_list = value.split("\\;")
    else:
        value_list = value

    r = {
        'regexp': value_list[0] if value_list[0] else ".*",
    }

    for value in value_list:
        if value.startswith('confidence:'):
            try:
                r['confidence'] = int(value[len('confidence:'):])
            except ValueError:
                pass

        if value.startswith('version:'):
            version = value[len('version:'):]
            if version.startswith('\\'):
                try:
                    r['version'] = int(version[1:].split('?')[0])
                except ValueError:
                    pass

    return r


def parse_headers(rule):
    matches = []
    for key, value in rule['headers'].items():
        value = parse_value(value)
        match = {
            "search": "headers[%s]" % key.lower(),
            "regexp": value['regexp']
        }

        if 'version' in value:
            match['offset'] = value['version']

        if 'confidence' in value:
            match['certainty'] = value['confidence']

        matches.append(match)

    return matches


def parse_cookies(rule):
    matches = []
    for key, value in rule['cookies'].items():
        value = parse_value(value)
        match = {
            "search": "cookies[%s]" % key,
            "regexp": value["regexp"]
        }

        if 'version' in value:
            match['offset'] = value['version']

        if 'confidence' in value:
            match['certainty'] = value['confidence']

        matches.append(match)

    return matches


def parse_html(rule):
    matches = []
    if isinstance(rule['html'], str):
        values = [rule['html']]
    else:
        values = rule['html']

    for value in values:
        value = parse_value(value)
        match = {
            "regexp": value['regexp']
        }

        if 'version' in value:
            match['offset'] = value['version']

        if 'confidence' in value:
            match['certainty'] = value['confidence']

        matches.append(match)

    return matches


def parse_scripts(rule):
    matches = []
    if isinstance(rule['scripts'], str):
        values = [rule['scripts']]
    else:
        values = rule['scripts']

    for value in values:
        value = parse_value(value)
        match = {
            'search': 'script',
            'regexp': value['regexp']
        }
        if 'version' in value:
            match['offset'] = value['version']

        if 'confidence' in value:
            match['certainty'] = value['confidence']

        matches.append(match)

    return matches


def parse_meta(rule):
    matches = []
    for key, value in rule['meta'].items():
        value = parse_value(value)
        match = {
            "search": "meta[%s]" % key,
            'regexp': value['regexp']
        }

        if 'version' in value:
            match['offset'] = value['version']

        if 'confidence' in value:
            match['certainty'] = value['confidence']

        matches.append(match)

    return matches


def parse_rules(src, dst):
    curdir = os.getcwd()

    with open(src) as fd:
        apps = json.load(fd)

    m = {
        'headers': parse_headers,
        'html': parse_html,
        'meta': parse_meta,
        'scripts': parse_scripts,
        'cookies': parse_cookies,
    }

    for name in apps:
        matches = []
        for key in apps[name]:
            if key not in m:
                continue

            matches.extend(m[key](apps[name]))

        with open(os.path.join(curdir, dst, "%s.json" % name.lower().replace('/', '_')), 'w') as fd:
            data = {
                'name': name,
                'website': apps[name]['website'],
                'matches': matches
            }
            if 'implies' in apps[name]:
                if isinstance(apps[name]['implies'], str):
                    data['implies'] = apps[name]['implies'].split("\\;")[0]
                else:
                    data['implies'] = []
                    for i in apps[name]['implies']:
                        data['implies'].append(i.split("\\;")[0])

            if 'excludes' in apps[name]:
                data['excludes'] = apps[name]['excludes']

            fd.write(json.dumps(data, indent=4))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("[*] Usage: %s src_dir dst_dir" % sys.argv[0])
        sys.exit(-1)

    for i in os.listdir(sys.argv[1]):
        try:
            parse_rules(os.path.join(sys.argv[1], i), sys.argv[2])
        except Exception as e:
            print("parse %s error: %s" % (i, e))
