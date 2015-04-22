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
        # info = [(id, file, protocolname, path)]
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

                self.info.append((attr['type'], file_name, attr['name'], path))


    def generate_message_id_dict(self):
        template = """
MESSAGE_TO_ID = {
%s
}"""

        message_ids = []
        for _id, _, _name, _ in self.info:
            message_ids.append('    "{0}": {1},'.format(_name, _id))

        content = template % "\n".join(message_ids)

        with open(self.f, 'w') as f:
            f.write(content)

    def generate_path_message_dict(self):
        template = """
PATH_TO_MESSAGE = {
%s
}"""
        path_messages = []
        for _id, _file, _name, _path in self.info:
            if not _path:
                continue

            path_messages.append('    "{0}": ["{1}", "{2}"],'.format(_path, _file, _name))

        content = template % "\n".join(path_messages)

        with open(self.f, 'a') as f:
            f.write(content)

    @classmethod
    def gen(cls):
        self = cls()
        self.generate_message_id_dict()
        self.generate_path_message_dict()


if __name__ == "__main__":
    path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(path)
    compile_protobuf()

    Gen.gen()

