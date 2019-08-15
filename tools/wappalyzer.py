#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json


def parse_value(value):
    value_list = value.split("\\;")
    r = {
        'regexp': value_list[0] if value_list[0] else ".*",
    }

    for value in value_list:
        if value.startswith('confidence:'):
            r['confidence'] = int(value[len('confidence:'):])

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


def parse_script(rule):
    matches = []
    if isinstance(rule['script'], str):
        values = [rule['script']]
    else:
        values = rule['script']

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


def parse_rules():
    curdir = os.path.dirname(__file__)
    with open(os.path.join(curdir, "../apps.json")) as fd:
        c = json.load(fd)

    m = {
        'headers': parse_headers,
        'html': parse_html,
        'meta': parse_meta,
        'script': parse_script,
        'cookies': parse_cookies,
    }

    apps = c['apps']
    for name in apps:
        matches = []
        for key in apps[name]:
            if key not in m:
                continue

            matches.extend(m[key](apps[name]))

        with open(os.path.join(curdir, "../webanalyzer/plugins/wappalyzer/%s.json" % name.lower().replace('/', '_')), 'w') as fd:
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
    parse_rules()
