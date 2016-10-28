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
from config.item import ConfigItemNew, ConfigItemUse, ConfigItemMerge, ConfigEquipmentNew, ConfigEquipmentSpecial, \
    ConfigEquipmentSpecialGenerate, ConfigEquipmentSpecialGrowingProperty, ConfigEquipmentSpecialLevel, \
    ConfigEquipmentSpecialScoreToGrowing
from config.skill import ConfigTalentSkill
from config.task import ConfigTaskMain, ConfigTaskDaily, ConfigTaskCondition
from config.club import ConfigClubLevel, ConfigClubFlag
from config.qianban import ConfigQianBan, ConfigInspire, ConfigInspireLevelAddition, ConfigInspireStepAddition, ConfigInspireAddition
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
from config.purchase import ConfigPurchaseYueka, ConfigPurchaseGoods, ConfigPurchaseFirstReward
from config.activity import ConfigActivityDailyBuy, ConfigActivityNewPlayer
from config.plunder import ConfigBaseStationLevel, ConfigPlunderBuyTimesCost, ConfigPlunderIncome, ConfigPlunderNPC, \
    ConfigPlunderDailyReward
from config.name import ConfigFirstName, ConfigLastName, ConfigName
from config.party import ConfigPartyLevel, ConfigPartyBuyItem

_has_configed = False


def load_config():
    from django.conf import settings
    from apps.config.models import Config as ModelConfig

    global _has_configed
    if _has_configed:
        return

    z_file = os.path.join(settings.BASE_DIR, 'config', 'config.zip')
    if os.environ.get('DIANJING_CONFIG', '') != 'local':
        c = ModelConfig.get_config()
        if c:
            z_file = c.config.path
        else:
            raise Exception("No config in db. Should set env: DIANJING_CONFIG=local")

    z = zipfile.ZipFile(z_file)
    for fname in z.namelist():
        content = z.open(fname).read()
        if not content:
            continue

        data = json.loads(content)

        if fname == 'global_config.json':
            GlobalConfig.initialize(data)
        elif fname == 'errormsg.json':
            ConfigErrorMessage.initialize(data)

        elif fname == 'first_name.json':
            ConfigFirstName.initialize(data)
        elif fname == 'last_name.json':
            ConfigLastName.initialize(data)

        elif fname == 'item_new.json':
            ConfigItemNew.initialize(data)
        elif fname == 'item_use.json':
            ConfigItemUse.initialize(data)
        elif fname == 'item_merge.json':
            ConfigItemMerge.initialize(data)
        elif fname == 'equipment_new.json':
            ConfigEquipmentNew.initialize(data)
        elif fname == 'equipment_special.json':
            ConfigEquipmentSpecial.initialize(data)
        elif fname == 'equipment_special_generate.json':
            ConfigEquipmentSpecialGenerate.initialize(data)
        elif fname == 'equipment_special_growing_property.json':
            ConfigEquipmentSpecialGrowingProperty.initialize(data)
        elif fname == 'equipment_special_level.json':
            ConfigEquipmentSpecialLevel.initialize(data)
        elif fname == 'equipment_special_score_to_growing.json':
            ConfigEquipmentSpecialScoreToGrowing.initialize(data)

        elif fname == 'staff_new.json':
            ConfigStaffNew.initialize(data)
        elif fname == 'staff_level_new.json':
            ConfigStaffLevelNew.initialize(data)
        elif fname == 'staff_star.json':
            ConfigStaffStar.initialize(data)
        elif fname == 'staff_equip_level_addition.json':
            ConfigStaffEquipmentLevelAddition.initialize(data)
        elif fname == 'staff_equip_quality_addition.json':
            ConfigStaffEquipmentQualityAddition.initialize(data)
        elif fname == 'staff_recruit.json':
            ConfigStaffRecruit.initialize(data)

        elif fname == 'challenge_chapter.json':
            ConfigChapter.initialize(data)
        elif fname == 'challenge_match.json':
            ConfigChallengeMatch.initialize(data)
        elif fname == 'challenge_buy_cost.json':
            ConfigChallengeResetCost.initialize(data)

        elif fname == 'unit_new.json':
            ConfigUnitNew.initialize(data)
        elif fname == 'unit_unlock.json':
            ConfigUnitUnLock.initialize(data)
        elif fname == 'unit_level_addition.json':
            ConfigUnitLevelAddition.initialize(data)
        elif fname == 'unit_step_addition.json':
            ConfigUnitStepAddition.initialize(data)

        elif fname == 'talent_skill.json':
            ConfigTalentSkill.initialize(data)

        elif fname == 'task_condition.json':
            ConfigTaskCondition.initialize(data)
        elif fname == 'task_main.json':
            ConfigTaskMain.initialize(data)
        elif fname == 'task_daily.json':
            ConfigTaskDaily.initialize(data)

        elif fname == 'club_level.json':
            ConfigClubLevel.initialize(data)
        elif fname == 'club_flag.json':
            ConfigClubFlag.initialize(data)

        elif fname == 'qianban.json':
            ConfigQianBan.initialize(data)
        elif fname == 'inspire.json':
            ConfigInspire.initialize(data)
        elif fname == 'inspire_level_addition.json':
            ConfigInspireLevelAddition.initialize(data)
        elif fname == 'inspire_step_addition.json':
            ConfigInspireStepAddition.initialize(data)

        elif fname == 'activity_signin.json':
            ConfigSignIn.initialize(data)

        elif fname == 'talent.json':
            ConfigTalent.initialize(data)
        elif fname == 'dungeon.json':
            ConfigDungeon.initialize(data)
        elif fname == 'dungeon_grade.json':
            ConfigDungeonGrade.initialize(data)
        elif fname == 'dungeon_reset_cost.json':
            ConfigDungeonBuyCost.initialize(data)

        elif fname == 'npc_formation.json':
            ConfigNPCFormation.initialize(data)

        elif fname == 'arena_npc.json':
            ConfigArenaNPC.initialize(data)
        elif fname == 'arena_honor_reward.json':
            ConfigArenaHonorReward.initialize(data)
        elif fname == 'arena_rank_reward.json':
            ConfigArenaRankReward.initialize(data)
        elif fname == 'arena_rank_reward_weekly.json':
            ConfigArenaRankRewardWeekly.initialize(data)
        elif fname == 'arena_match_reward.json':
            ConfigArenaMatchReward.initialize(data)
        elif fname == 'arena_buy_times_cost.json':
            ConfigArenaBuyTimesCost.initialize(data)
        elif fname == 'arena_search_range.json':
            ConfigArenaSearchRange.initialize(data)
        elif fname == 'arena_reset_cost.json':
            ConfigArenaSearchResetCost.initialize(data)

        elif fname == 'tower_level.json':
            ConfigTowerLevel.initialize(data)
        elif fname == 'tower_reset_cost.json':
            ConfigTowerResetCost.initialize(data)
        elif fname == 'tower_sale_goods.json':
            ConfigTowerSaleGoods.initialize(data)
        elif fname == 'tower_rank_reward.json':
            ConfigTowerRankReward.initialize(data)

        elif fname == 'territory_building.json':
            ConfigTerritoryBuilding.initialize(data)
        elif fname == 'territory_inspire_cost.json':
            ConfigInspireCost.initialize(data)
        elif fname == 'territory_staff_special_product.json':
            ConfigTerritoryStaffProduct.initialize(data)
        elif fname == 'territory_event.json':
            ConfigTerritoryEvent.initialize(data)
        elif fname == 'territory_store.json':
            ConfigTerritoryStore.initialize(data)

        elif fname == 'store_type.json':
            ConfigStoreType.initialize(data)
        elif fname == 'store.json':
            ConfigStore.initialize(data)
        elif fname == 'store_refresh_cost.json':
            ConfigStoreRefreshCost.initialize(data)

        elif fname == 'vip.json':
            ConfigVIP.initialize(data)

        elif fname == 'collection.json':
            ConfigCollection.initialize(data)

        elif fname == 'energy_buy_cost.json':
            ConfigEnergyBuyCost.initialize(data)

        elif fname == 'formation.json':
            ConfigFormation.initialize(data)
        elif fname == 'formation_slot.json':
            ConfigFormationSlot.initialize(data)

        elif fname == 'welfare_level_reward.json':
            ConfigWelfareLevelReward.initialize(data)
        elif fname == 'welfare_new_player.json':
            ConfigWelfareNewPlayer.initialize(data)
        elif fname == 'welfare_signin.json':
            ConfigWelfareSignIn.initialize(data)

        elif fname == 'broadcast_template.json':
            ConfigBroadcastTemplate.initialize(data)

        elif fname == 'union_level.json':
            ConfigUnionLevel.initialize(data)
        elif fname == 'union_signin.json':
            ConfigUnionSignin.initialize(data)

        elif fname == 'purchase_yueka.json':
            ConfigPurchaseYueka.initialize(data)
        elif fname == 'purchase_goods.json':
            ConfigPurchaseGoods.initialize(data)
        elif fname == 'purchase_first_reward.json':
            ConfigPurchaseFirstReward.initialize(data)

        elif fname == 'activity_daily_buy.json':
            ConfigActivityDailyBuy.initialize(data)
        elif fname == 'activity_new_player.json':
            ConfigActivityNewPlayer.initialize(data)

        elif fname == 'base_station_level.json':
            ConfigBaseStationLevel.initialize(data)
        elif fname == 'plunder_income.json':
            ConfigPlunderIncome.initialize(data)
        elif fname == 'plunder_buy_times_cost.json':
            ConfigPlunderBuyTimesCost.initialize(data)
        elif fname == 'plunder_npc.json':
            ConfigPlunderNPC.initialize(data)
        elif fname == 'plunder_daily_reward.json':
            ConfigPlunderDailyReward.initialize(data)

        elif fname == 'party_level.json':
            ConfigPartyLevel.initialize(data)
        elif fname == 'party_buy_item.json':
            ConfigPartyBuyItem.initialize(data)

    _has_configed = True
    sys.stderr.write("LOAD CONFIG FROM {0}\n".format(z_file))
