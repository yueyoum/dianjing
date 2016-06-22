# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       __init__
Date Created:   2015-04-23 23:09
Description:

"""

import os
import sys
import json
import zipfile

from config.global_config import GlobalConfig
from config.errormsg import ConfigErrorMessage
from config.staff import ConfigStaffRecruit, ConfigStaffNew, ConfigStaffStar, ConfigStaffLevelNew, ConfigStaffEquipmentLevelAddition, ConfigStaffEquipmentQualityAddition, ConfigStaffEquipmentAddition
from config.challenge import ConfigChallengeMatch, ConfigChapter, ConfigChallengeResetCost
from config.unit import ConfigUnitNew, ConfigUnitUnLock, ConfigUnitStepAddition, ConfigUnitLevelAddition, ConfigUnitAddition
from config.item import ConfigItemNew, ConfigItemUse, ConfigItemMerge, ConfigEquipmentNew
from config.skill import ConfigTalentSkill
from config.task import ConfigTaskMain, ConfigRandomEvent, ConfigTaskDaily, ConfigTaskCondition
from config.club import ConfigClubLevel, ConfigClubFlag
from config.qianban import ConfigQianBan
from config.activity import ConfigActivityCategory
from config.signin import ConfigSignIn
from config.activity_login_reward import ConfigLoginReward
from config.active_value import ConfigActiveFunction, ConfigActiveReward
from config.talent import ConfigTalent
from config.dungeon import ConfigDungeon, ConfigDungeonGrade, ConfigDungeonBuyCost
from config.npc import ConfigNPCFormation
from config.arena import ConfigArenaNPC, ConfigArenaHonorReward, ConfigArenaBuyTimesCost, ConfigArenaMatchReward, ConfigArenaRankReward, ConfigArenaSearchRange
from config.tower import ConfigTowerLevel, ConfigTowerResetCost, ConfigTowerSaleGoods, ConfigTowerRankReward
from config.territory import ConfigTerritoryBuilding, ConfigInspireCost, ConfigTerritoryStaffProduct, ConfigTerritoryEvent, ConfigTerritoryStore
from config.store import ConfigStore, ConfigStoreRefreshCost, ConfigStoreType
from config.vip import ConfigVIP
from config.collection import ConfigCollection
from config.energy import ConfigEnergyBuyCost
from config.formation import ConfigFormationSlot


_has_configed = False


def load_config():
    from django.conf import settings
    from apps.config.models import Config as ModelConfig

    global _has_configed
    if _has_configed:
        return

    _has_configed = True

    if settings.TEST:
        z_file = os.path.join(settings.BASE_DIR, 'config', 'config.zip')
    else:
        c = ModelConfig.get_config()
        if c:
            z_file = c.config.path
        else:
            z_file = os.path.join(settings.BASE_DIR, 'config', 'config.zip')

    z = zipfile.ZipFile(z_file)
    for item in z.namelist():
        content = z.open(item).read()
        if not content:
            continue

        data = json.loads(content)

        if item == 'global_config.json':
            GlobalConfig.initialize(data)
        elif item == 'errormsg.json':
            ConfigErrorMessage.initialize(data)
        elif item == 'item_new.json':
            ConfigItemNew.initialize(data)
        elif item == 'item_use.json':
            ConfigItemUse.initialize(data)
        elif item == 'item_merge.json':
            ConfigItemMerge.initialize(data)
        elif item == 'equipment_new.json':
            ConfigEquipmentNew.initialize(data)

        elif item == 'staff_new.json':
            ConfigStaffNew.initialize(data)
        elif item == 'staff_level_new.json':
            ConfigStaffLevelNew.initialize(data)
        elif item == 'staff_star.json':
            ConfigStaffStar.initialize(data)
        elif item == 'staff_equip_level_addition.json':
            ConfigStaffEquipmentLevelAddition.initialize(data)
        elif item == 'staff_equip_quality_addition.json':
            ConfigStaffEquipmentQualityAddition.initialize(data)
        elif item == 'staff_recruit.json':
            ConfigStaffRecruit.initialize(data)

        elif item == 'challenge_chapter.json':
            ConfigChapter.initialize(data)
        elif item == 'challenge_match.json':
            ConfigChallengeMatch.initialize(data)
        elif item == 'challenge_buy_cost.json':
            ConfigChallengeResetCost.initialize(data)

        elif item == 'unit_new.json':
            ConfigUnitNew.initialize(data)
        elif item == 'unit_unlock.json':
            ConfigUnitUnLock.initialize(data)
        elif item == 'unit_level_addition.json':
            ConfigUnitLevelAddition.initialize(data)
        elif item == 'unit_step_addition.json':
            ConfigUnitStepAddition.initialize(data)

        elif item == 'talent_skill.json':
            ConfigTalentSkill.initialize(data)

        elif item == 'task_condition.json':
            ConfigTaskCondition.initialize(data)
        elif item == 'task_main.json':
            ConfigTaskMain.initialize(data)
        elif item == 'task_daily.json':
            ConfigTaskDaily.initialize(data)
        elif item == 'random_event.json':
            ConfigRandomEvent.initialize(data)

        elif item == 'club_level.json':
            ConfigClubLevel.initialize(data)
        elif item == 'club_flag.json':
            ConfigClubFlag.initialize(data)

        elif item == 'qianban.json':
            ConfigQianBan.initialize(data)

        elif item == 'activity_category.json':
            ConfigActivityCategory.initialize(data)
        elif item == 'activity_signin.json':
            ConfigSignIn.initialize(data)
        elif item == 'activity_login_reward.json':
            ConfigLoginReward.initialize(data)
        elif item == 'active_function.json':
            ConfigActiveFunction.initialize(data)
        elif item == 'active_reward.json':
            ConfigActiveReward.initialize(data)

        elif item == 'talent.json':
            ConfigTalent.initialize(data)
        elif item == 'dungeon.json':
            ConfigDungeon.initialize(data)
        elif item == 'dungeon_grade.json':
            ConfigDungeonGrade.initialize(data)
        elif item == 'dungeon_reset_cost.json':
            ConfigDungeonBuyCost.initialize(data)

        elif item == 'npc_formation.json':
            ConfigNPCFormation.initialize(data)

        elif item == 'arena_npc.json':
            ConfigArenaNPC.initialize(data)
        elif item == 'arena_honor_reward.json':
            ConfigArenaHonorReward.initialize(data)
        elif item == 'arena_rank_reward.json':
            ConfigArenaRankReward.initialize(data)
        elif item == 'arena_match_reward.json':
            ConfigArenaMatchReward.initialize(data)
        elif item == 'arena_buy_times_cost.json':
            ConfigArenaBuyTimesCost.initialize(data)
        elif item == 'arena_search_range.json':
            ConfigArenaSearchRange.initialize(data)

        elif item == 'tower_level.json':
            ConfigTowerLevel.initialize(data)
        elif item == 'tower_reset_cost.json':
            ConfigTowerResetCost.initialize(data)
        elif item == 'tower_sale_goods.json':
            ConfigTowerSaleGoods.initialize(data)
        elif item == 'tower_rank_reward.json':
            ConfigTowerRankReward.initialize(data)

        elif item == 'territory_building.json':
            ConfigTerritoryBuilding.initialize(data)
        elif item == 'territory_inspire_cost.json':
            ConfigInspireCost.initialize(data)
        elif item == 'territory_staff_special_product.json':
            ConfigTerritoryStaffProduct.initialize(data)
        elif item == 'territory_event.json':
            ConfigTerritoryEvent.initialize(data)
        elif item == 'territory_store.json':
            ConfigTerritoryStore.initialize(data)

        elif item == 'store_type.json':
            ConfigStoreType.initialize(data)
        elif item == 'store.json':
            ConfigStore.initialize(data)
        elif item == 'store_refresh_cost.json':
            ConfigStoreRefreshCost.initialize(data)

        elif item == 'vip.json':
            ConfigVIP.initialize(data)

        elif item == 'collection.json':
            ConfigCollection.initialize(data)

        elif item == 'energy_buy_cost.json':
            ConfigEnergyBuyCost.initialize(data)

        elif item == 'formation_slot.json':
            ConfigFormationSlot.initialize(data)

    sys.stderr.write("LOAD CONFIG FROM {0}\n".format(z_file))

