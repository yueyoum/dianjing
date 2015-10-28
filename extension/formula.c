
// 技能强度
// params
// base: 技能基础值
// grow: 技能等级增长
// level: 技能等级
float skill_strength(int base_value, int grow, int level)
{
    if(level<=0) return 0;
    return (base_value + grow * level)/100.0f;
}

// 员工经验训练需要花费多少金币
// params
// staff_level: 员工等级
int staff_training_exp_need_gold(int staff_level)
{
    return staff_level * 1000;
}

// 员工直播训练知名度属性加成
// params
// zhimingdu: 知名度属性
int staff_training_broadcast_zhimingdu_addition(int zhimingdu)
{
    return zhimingdu / 10;
}

// 员工直播训练每分钟获得金币收益
// params
// staff_level: 员工等级
// zhimingdu: 知名度属性
// skill_base: 技能基础值
// skill_grow: 技能等级增长
// skill_level: 技能等级 （员工没有直播技能，level为0）
int staff_training_broadcast_reward_gold_per_minute(
        int staff_level,
        int zhimingdu,
        int skill_base,
        int skill_grow,
        int skill_level
        )
{
    int staff_value = staff_level + staff_training_broadcast_zhimingdu_addition(zhimingdu);
    float skill_vaue = 1 + skill_strength(skill_base, skill_grow, skill_level);
    return (int)(staff_value * skill_vaue);
}


// 训练加速需要花费的钻石
// params
// seconds_to_finish: 还需要多少秒才能完成
int training_speedup_need_diamond(int seconds_to_finish)
{
    int minutes = seconds_to_finish / 60;
    int seconds = seconds_to_finish % 60;
    if(seconds>0) ++minutes;

    return minutes * 10;
}

