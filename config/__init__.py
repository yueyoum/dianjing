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


_has_configed = False

def load_config():
    from django.conf import settings

    global _has_configed
    if _has_configed:
        return

    _has_configed = True


    z = zipfile.ZipFile(os.path.join(settings.BASE_DIR, 'config', 'config.zip'))
    for item in z.namelist():
        content = z.open(item).read()
        if not content:
            continue

        data = json.loads(content)


        if item == 'errormsg.json':
            ConfigErrorMessage.initialize(data)
        elif item == 'staff.json':
            ConfigStaff.initialize(data)
        elif item == 'staff_hot.json':
            ConfigStaffHot.initialize(data)
        elif item == 'staff_recruit.json':
            ConfigStaffRecruit.initialize(data)
        elif item == 'staff_level.json':
            ConfigStaffLevel.initialize(data)
        elif item == 'challenge_type.json':
            ConfigChallengeType.initialize(data)
        elif item == 'challenge_match.json':
            ConfigChallengeMatch.initialize(data)
        elif item == 'unit.json':
            ConfigUnit.initialize(data)
        elif item == 'building.json':
            ConfigBuilding.initialize(data)
        elif item == 'package.json':
            ConfigPackage.initialize(data)
        elif item == 'training.json':
            ConfigTraining.initialize(data)
        elif item == 'npc_club.json':
            ConfigNPC.initialize(data)
        elif item == 'npc_club_name.json':
            ConfigNPC.initialize_club_names(data)
        elif item == 'npc_manager_name.json':
            ConfigNPC.initialize_manager_name(data)
        elif item == 'skill.json':
            ConfigSkill.initialize(data)
        elif item == 'policy.json':
            ConfigPolicy.initialize(data)
        elif item == 'task.json':
            ConfigTask.initialize(data)
        elif item == 'club_level.json':
            ConfigClubLevel.initialize(data)

    print "LOAD CONFIG DONE"

