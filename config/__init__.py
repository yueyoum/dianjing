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
from config.staff import ConfigStaffRecruit, ConfigStaffNew, ConfigStaffStar, ConfigStaffLevelNew, \
    ConfigStaffEquipmentLevelAddition, ConfigStaffEquipmentQualityAddition, ConfigStaffEquipmentAddition
from config.challenge import ConfigChallengeMatch, ConfigChapter, ConfigChallengeResetCost
from config.unit import ConfigUnitNew, ConfigUnitUnLock, ConfigUnitStepAddition, ConfigUnitLevelAddition, \
    ConfigUnitAddition
from config.item import ConfigItemNew, ConfigItemUse, ConfigItemMerge, ConfigEquipmentNew
from config.skill import ConfigTalentSkill
from config.task import ConfigTaskMain, ConfigTaskDaily, ConfigTaskCondition
from config.club import ConfigClubLevel, ConfigClubFlag
from config.qianban import ConfigQianBan
from config.signin import ConfigSignIn
from config.talent import ConfigTalent
from config.dungeon import ConfigDungeon, ConfigDungeonGrade, ConfigDungeonBuyCost
from config.npc import ConfigNPCFormation
from config.arena import ConfigArenaNPC, ConfigArenaHonorReward, ConfigArenaBuyTimesCost, ConfigArenaMatchReward, \
    ConfigArenaRankReward, ConfigArenaSearchRange, ConfigArenaSearchResetCost, ConfigArenaRankRewardWeekly
from config.tower import ConfigTowerLevel, ConfigTowerResetCost, ConfigTowerSaleGoods, ConfigTowerRankReward
from config.territory import ConfigTerritoryBuilding, ConfigInspireCost, ConfigTerritoryStaffProduct, \
    ConfigTerritoryEvent, ConfigTerritoryStore
from config.store import ConfigStore, ConfigStoreRefreshCost, ConfigStoreType
from config.vip import ConfigVIP
from config.collection import ConfigCollection
from config.energy import ConfigEnergyBuyCost
from config.formation import ConfigFormationSlot, ConfigFormation
from config.welfare import ConfigWelfareSignIn, ConfigWelfareLevelReward, ConfigWelfareNewPlayer
from config.template import ConfigBroadcastTemplate
from config.union import ConfigUnionSignin, ConfigUnionLevel
from config.purchase import ConfigPurchaseYueka, ConfigPurchaseGoods
from config.activity import ConfigActivityDailyBuy, ConfigActivityNewPlayer

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
    for name in z.namelist():
        content = z.open(name).read()
        if not content:
            continue

        data = json.loads(content)

        if name == 'global_config.json':
            GlobalConfig.initialize(data)
        elif name == 'errormsg.json':
            ConfigErrorMessage.initialize(data)
        elif name == 'item_new.json':
            ConfigItemNew.initialize(data)
        elif name == 'item_use.json':
            ConfigItemUse.initialize(data)
        elif name == 'item_merge.json':
            ConfigItemMerge.initialize(data)
        elif name == 'equipment_new.json':
            ConfigEquipmentNew.initialize(data)

        elif name == 'staff_new.json':
            ConfigStaffNew.initialize(data)
        elif name == 'staff_level_new.json':
            ConfigStaffLevelNew.initialize(data)
        elif name == 'staff_star.json':
            ConfigStaffStar.initialize(data)
        elif name == 'staff_equip_level_addition.json':
            ConfigStaffEquipmentLevelAddition.initialize(data)
        elif name == 'staff_equip_quality_addition.json':
            ConfigStaffEquipmentQualityAddition.initialize(data)
        elif name == 'staff_recruit.json':
            ConfigStaffRecruit.initialize(data)

        elif name == 'challenge_chapter.json':
            ConfigChapter.initialize(data)
        elif name == 'challenge_match.json':
            ConfigChallengeMatch.initialize(data)
        elif name == 'challenge_buy_cost.json':
            ConfigChallengeResetCost.initialize(data)

        elif name == 'unit_new.json':
            ConfigUnitNew.initialize(data)
        elif name == 'unit_unlock.json':
            ConfigUnitUnLock.initialize(data)
        elif name == 'unit_level_addition.json':
            ConfigUnitLevelAddition.initialize(data)
        elif name == 'unit_step_addition.json':
            ConfigUnitStepAddition.initialize(data)

        elif name == 'talent_skill.json':
            ConfigTalentSkill.initialize(data)

        elif name == 'task_condition.json':
            ConfigTaskCondition.initialize(data)
        elif name == 'task_main.json':
            ConfigTaskMain.initialize(data)
        elif name == 'task_daily.json':
            ConfigTaskDaily.initialize(data)

        elif name == 'club_level.json':
            ConfigClubLevel.initialize(data)
        elif name == 'club_flag.json':
            ConfigClubFlag.initialize(data)

        elif name == 'qianban.json':
            ConfigQianBan.initialize(data)

        elif name == 'activity_signin.json':
            ConfigSignIn.initialize(data)

        elif name == 'talent.json':
            ConfigTalent.initialize(data)
        elif name == 'dungeon.json':
            ConfigDungeon.initialize(data)
        elif name == 'dungeon_grade.json':
            ConfigDungeonGrade.initialize(data)
        elif name == 'dungeon_reset_cost.json':
            ConfigDungeonBuyCost.initialize(data)

        elif name == 'npc_formation.json':
            ConfigNPCFormation.initialize(data)

        elif name == 'arena_npc.json':
            ConfigArenaNPC.initialize(data)
        elif name == 'arena_honor_reward.json':
            ConfigArenaHonorReward.initialize(data)
        elif name == 'arena_rank_reward.json':
            ConfigArenaRankReward.initialize(data)
        elif name == 'arena_rank_reward_weekly.json':
            ConfigArenaRankRewardWeekly.initialize(data)
        elif name == 'arena_match_reward.json':
            ConfigArenaMatchReward.initialize(data)
        elif name == 'arena_buy_times_cost.json':
            ConfigArenaBuyTimesCost.initialize(data)
        elif name == 'arena_search_range.json':
            ConfigArenaSearchRange.initialize(data)
        elif name == 'arena_reset_cost.json':
            ConfigArenaSearchResetCost.initialize(data)

        elif name == 'tower_level.json':
            ConfigTowerLevel.initialize(data)
        elif name == 'tower_reset_cost.json':
            ConfigTowerResetCost.initialize(data)
        elif name == 'tower_sale_goods.json':
            ConfigTowerSaleGoods.initialize(data)
        elif name == 'tower_rank_reward.json':
            ConfigTowerRankReward.initialize(data)

        elif name == 'territory_building.json':
            ConfigTerritoryBuilding.initialize(data)
        elif name == 'territory_inspire_cost.json':
            ConfigInspireCost.initialize(data)
        elif name == 'territory_staff_special_product.json':
            ConfigTerritoryStaffProduct.initialize(data)
        elif name == 'territory_event.json':
            ConfigTerritoryEvent.initialize(data)
        elif name == 'territory_store.json':
            ConfigTerritoryStore.initialize(data)

        elif name == 'store_type.json':
            ConfigStoreType.initialize(data)
        elif name == 'store.json':
            ConfigStore.initialize(data)
        elif name == 'store_refresh_cost.json':
            ConfigStoreRefreshCost.initialize(data)

        elif name == 'vip.json':
            ConfigVIP.initialize(data)

        elif name == 'collection.json':
            ConfigCollection.initialize(data)

        elif name == 'energy_buy_cost.json':
            ConfigEnergyBuyCost.initialize(data)

        elif name == 'formation.json':
            ConfigFormation.initialize(data)
        elif name == 'formation_slot.json':
            ConfigFormationSlot.initialize(data)

        elif name == 'welfare_level_reward.json':
            ConfigWelfareLevelReward.initialize(data)
        elif name == 'welfare_new_player.json':
            ConfigWelfareNewPlayer.initialize(data)
        elif name == 'welfare_signin.json':
            ConfigWelfareSignIn.initialize(data)

        elif name == 'broadcast_template.json':
            ConfigBroadcastTemplate.initialize(data)

        elif name == 'union_level.json':
            ConfigUnionLevel.initialize(data)
        elif name == 'union_signin.json':
            ConfigUnionSignin.initialize(data)

        elif name == 'purchase_yueka.json':
            ConfigPurchaseYueka.initialize(data)
        elif name == 'purchase_goods.json':
            ConfigPurchaseGoods.initialize(data)

        elif name == 'activity_daily_buy.json':
            ConfigActivityDailyBuy.initialize(data)
        elif name == 'activity_new_player.json':
            ConfigActivityNewPlayer.initialize(data)

    sys.stderr.write("LOAD CONFIG FROM {0}\n".format(z_file))
