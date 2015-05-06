#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       compile-protobuf
Date Created:   2015-04-22 02:36
Description:

"""
import os
import sys
import subprocess
import xml.etree.ElementTree as et

def compile_protobuf():
    cmd = 'protoc --python_out=protomsg -Iprotobuf protobuf/*.proto'
    pipe = subprocess.PIPE
    p = subprocess.Popen(cmd, shell=True, stdout=pipe, stderr=pipe)
    exitcode = p.wait()
    stdout, stderr = p.communicate()

    if exitcode:
        print stderr
        sys.exit(1)


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

            path = id_path_dict[reqtype]

            path_responses.append('    "{0}": ["{1}", "{2}"],'.format(path, info["file"], info["name"]))

        content = template % "\n".join(path_responses)

        with open(self.f, 'a') as f:
            f.write(content)


    @classmethod
    def gen(cls):
        self = cls()
        self.generate_message_id_dict()
        self.generate_id_message_dict()
        self.generate_path_request_dict()
        self.generate_path_response_dict()


if __name__ == "__main__":
    path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(path)
    compile_protobuf()

    Gen.gen()

