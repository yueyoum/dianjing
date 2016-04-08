
from core.abstract import AbstractUnit

from protomsg.unit_pb2 import UnitNotify


class Unit(AbstractUnit):
    def __init__(self, data):
        super(Unit, self).__init__()
        self.id = data.id
        self.oid = data.oid
        self.step = data.step
        self.lv = data.lv

    def calculate(self):
        self.hp = 0
        self.hp_percent = 0.0
        self.attack = 0
        self.attack_percent = 0.0
        self.defense = 0
        self.defense_percent = 0.0
        self.attack_speed = 0
        self.attack_speed_percent = 0.0
        self.attack_distance = 0
        self.attack_distance_percent = 0.0
        self.move_speed = 0
        self.move_speed_percent = 0.0
        self.hit_rate = 0.0
        self.dodge_rate = 0.0
        self.crit_rate = 0.0
        self.crit_multi = 0.0
        self.crit_anti_rate = 0.0
        self.append_attack_terran = 0.0
        self.append_attack_protoss = 0.0
        self.append_attack_zerg = 0.0
        self.append_attacked_by_terran = 0.0
        self.append_attacked_by_protoss = 0.0
        self.append_attacked_by_zerg = 0.0
        self.final_hurt_append = 0
        self.final_hurt_reduce = 0

    def step_up(self, oid):
        pass

    def level_up(self, oid):
        pass

    def notify(self):
        notify = UnitNotify()
        pass
