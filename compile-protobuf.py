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


def generate_message_id_dict():
    template = """
MESSAGE_TO_ID = {
%s
}"""

    tree = et.ElementTree(file="protobuf/define.xml")
    doc = tree.getroot()

    protocols = doc.findall("namespace/namespace/protocol")

    message_ids = []
    for p in protocols:
        attrib = p.attrib
        message_ids.append('    "{0}": {1},'.format(attrib['name'], attrib['type']))

    content = template % "\n".join(message_ids)

    with open("protomsg/__init__.py", 'w') as f:
        f.write(content)


if __name__ == "__main__":
    path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(path)
    compile_protobuf()
    generate_message_id_dict()

