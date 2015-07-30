# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       __init__
Date Created:   2015-04-23 23:09
Description:

"""

import os
import json
import zipfile
from django.conf import settings

from config.errormsg import ConfigErrorMessage
from config.staff import ConfigStaff, ConfigStaffHot, ConfigStaffRecruit, ConfigStaffLevel
from config.challenge import ConfigChallengeType, ConfigChallengeMatch
from config.unit import ConfigUnit, ConfigPolicy
from config.building import ConfigBuilding
from config.package import ConfigPackage
from config.training import ConfigTraining
from config.npc import ConfigNPC
from config.skill import ConfigSkill
from config.task import ConfigTask
from config.club import ConfigClubLevel


CONFIG = None


class _Config(object):
    pass


def load_config():
    global CONFIG
    if CONFIG is not None:
        return


    attr_dict = {}

    z = zipfile.ZipFile(os.path.join(settings.BASE_DIR, 'config', 'config.zip'))
    for item in z.namelist():

        name, ext = os.path.splitext(item)
        content = z.open(item).read()
        if not content:
            continue

        data = json.loads(content)

        attr_name = name.upper()
        attr_value = {}

        for d in data:
            obj = _Config()
            obj.id = d['pk']
            for k, v in d['fields'].iteritems():
                setattr(obj, k, v)

            attr_value[obj.id] = obj

        attr_dict[attr_name] = attr_value

        # ===
        if attr_name == 'ERRORMSG':
            ConfigErrorMessage.initialize(data)
        elif attr_name == 'STAFF':
            ConfigStaff.initialize(data)
        elif attr_name == 'STAFF_HOT':
            ConfigStaffHot.initialize(data)
        elif attr_name == 'STAFF_RECRUIT':
            ConfigStaffRecruit.initialize(data)
        elif attr_name == 'STAFF_LEVEL':
            ConfigStaffLevel.initialize(data)
        elif attr_name == 'CHALLENGE_TYPE':
            ConfigChallengeType.initialize(data)
        elif attr_name == 'CHALLENGE_MATCH':
            ConfigChallengeMatch.initialize(data)
        elif attr_name == 'UNIT':
            ConfigUnit.initialize(data)
        elif attr_name == 'BUILDING':
            ConfigBuilding.initialize(data)
        elif attr_name == 'PACKAGE':
            ConfigPackage.initialize(data)
        elif attr_name == 'TRAINING':
            ConfigTraining.initialize(data)
        elif attr_name == 'NPC_CLUB':
            ConfigNPC.initialize(data)
        elif attr_name == 'NPC_CLUB_NAME':
            ConfigNPC.initialize_club_names(data)
        elif attr_name == 'NPC_MANAGER_NAME':
            ConfigNPC.initialize_manager_name(data)
        elif attr_name == 'SKILL':
            ConfigSkill.initialize(data)
        elif attr_name == 'POLICY':
            ConfigPolicy.initialize(data)
        elif attr_name == 'TASK':
            ConfigTask.initialize(data)
        elif attr_name == 'CLUB_LEVEL':
            ConfigClubLevel.initialize(data)


    CONFIG = type('CONFIG', (object,), attr_dict)

    print "LOAD CONFIG DONE"

