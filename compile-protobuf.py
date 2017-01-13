#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       compile-protobuf
Date Created:   2015-04-22 02:36
Description:

"""
import re
import os
import sys
import subprocess
import xml.etree.ElementTree as et

import arrow

def run_cmd(cmd):
    pipe = subprocess.PIPE
    p = subprocess.Popen(cmd, shell=True, stdout=pipe, stderr=pipe)
    exitcode = p.wait()
    stdout, stderr = p.communicate()

    if exitcode:
        print stderr
        sys.exit(1)


def compile_protobuf():
    cmd = 'protoc --python_out=protomsg -Iprotobuf protobuf/*.proto'
    run_cmd(cmd)


class Gen(object):
    def __init__(self):
        self.f = "protomsg/__init__.py"
        self.info = []

        tree = et.ElementTree(file="protobuf/define.xml")
        doc = tree.getroot()

        protocols = doc.findall("file")
        for p in protocols:
            file_name = p.attrib['name']
            for c in p.getchildren():
                attr = c.attrib
                path = attr.get("command", "")
                if path and not path.startswith("/game/"):
                    raise Exception("Invalid Path: {0}".format(path))

                attr['file'] = file_name
                self.info.append(attr)



    def generate_message_id_dict(self):
        template = """
MESSAGE_TO_ID = {
%s
}
"""

        message_ids = []
        for info in self.info:
            message_ids.append('    "{0}": {1},'.format(info['name'], info['type']))

        content = template % "\n".join(message_ids)

        with open(self.f, 'w') as f:
            f.write(content)

    def generate_id_message_dict(self):
        template = """
ID_TO_MESSAGE = {
%s
}
"""

        id_messages = []
        for info in self.info:
            id_messages.append('    {0}: "{1}",'.format(info['type'], info['name']))

        content = template % "\n".join(id_messages)

        with open(self.f, 'a') as f:
            f.write(content)

    def generate_path_request_dict(self):
        template = """
PATH_TO_REQUEST = {
%s
}
"""
        path_requests = []
        for info in self.info:
            if not info.get("command", ""):
                continue

            path_requests.append('    "{0}": ["{1}", "{2}"],'.format(info["command"], info["file"], info["name"]))

        content = template % "\n".join(path_requests)

        with open(self.f, 'a') as f:
            f.write(content)

    def generate_path_response_dict(self):
        template = """
PATH_TO_RESPONSE = {
%s
}
"""

        id_path_dict = {}
        for info in self.info:
            path = info.get('command', "")
            if not path:
                continue

            id_path_dict[info['type']] = path

        path_responses = []
        for info in self.info:
            reqtype = info.get("reqtype", "")
            if not reqtype:
                continue

            path = id_path_dict.get(reqtype, "")
            if not path:
                continue

            path_responses.append('    "{0}": ["{1}", "{2}"],'.format(path, info["file"], info["name"]))

        content = template % "\n".join(path_responses)

        with open(self.f, 'a') as f:
            f.write(content)

    def gen_python_file(self):
        self.generate_message_id_dict()
        self.generate_id_message_dict()
        self.generate_path_request_dict()
        self.generate_path_response_dict()


    def generate_erl_protocol(self, *should_generates):
        pattern_package = re.compile('^\s*package')
        pattern_import = re.compile('^\s*import')

        content = []

        for s in should_generates:
            with open('protobuf/{0}'.format(s), 'r') as x:
                for line in x.readlines():
                    if pattern_package.search(line) or pattern_import.search(line):
                        continue

                    content.append(line)

        with open('dj_protocol.proto', 'w') as f:
            f.writelines(content)

        cmd = 'protoc-erl -I . -o erlang -strbin -msgprefix Proto dj_protocol.proto'
        run_cmd(cmd)

        os.remove('dj_protocol.proto')


    def generate_erl_protocol_mapping(self):
        template_get_name = """
get_name(%s) ->
    %s;"""

        template_get_id = """
get_id(#'Proto%s'{}) ->
    %s;"""

        template_file = """
-module(%s).
-export([get_name/1,
    get_id/1]).

-include("dj_protocol.hrl").

%s

%s
"""
        get_name = []
        for info in self.info:
            if info.get('socket', '') == '1':
                get_name.append(template_get_name % (info['type'], "'Proto{0}'".format(info['name'])))

        last = template_get_name % ('_', 'undefined')
        last = last[:-1] + '.'
        get_name.append(last)

        get_id = []
        for info in self.info:
            if info.get('socket', '') == '2':
                get_id.append(template_get_id % (info['name'], info['type']))

        get_id[-1] = get_id[-1][:-1] + '.'

        file_name = 'dj_protocol_mapping'
        content = template_file % (
            file_name,
            '\n'.join(get_name),
            '\n'.join(get_id)
        )

        with open('erlang/{0}.erl'.format(file_name), 'w') as f:
            f.write(content)

    # def generate_erl_hrl(self):
    #     split_pattern = re.compile('([A-Z][^A-Z]*)')
    #
    #     def to_macro(name):
    #         splited = split_pattern.split(name)
    #         macro = ['PROTO']
    #         for s in splited:
    #             if s:
    #                 macro.append(s.upper())
    #
    #         return '_'.join(macro)
    #
    #
    #     template = "-define(%s, '%s')."
    #
    #     content = []
    #     for info in self.info:
    #         if info.get('socket', '') == '2':
    #             content.append(template % (to_macro(info['name']), info['name']))
    #
    #     with open('erlang/dj_protocol.hrl', 'w') as f:
    #         f.write('\n'.join(content))


    def gen_erlang_file(self, *should_generates):
        self.generate_erl_protocol(*should_generates)
        self.generate_erl_protocol_mapping()
        # self.generate_erl_hrl()


if __name__ == "__main__":
    path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(path)

    compile_protobuf()

    g = Gen()
    g.gen_python_file()
    g.gen_erlang_file('common.proto', 'party.proto')
