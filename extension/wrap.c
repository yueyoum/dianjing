#include <Python.h>

#include "formula.c"

// 经验训练花费金币
static PyObject* wrap_staff_training_exp_need_gold(PyObject* self, PyObject* args)
{
    int staff_level;

    int result;

    if(!PyArg_ParseTuple(args, "i:staff_training_exp_need_gold", &staff_level))
        return NULL;

    result = staff_training_exp_need_gold(staff_level);
    return Py_BuildValue("i", result);
}

// 直播训练每分钟获得金币
static PyObject* wrap_staff_training_broadcast_reward_gold_per_minute(PyObject* self, PyObject* args)
{
    int staff_level;
    int zhimingdu;
    int skill_base;
    int skill_grow;
    int skill_level;

    int result;

    if(!PyArg_ParseTuple(args, "iiiii:staff_training_broadcast_reward_gold_per_minute",
        &staff_level, &zhimingdu, &skill_base, &skill_grow, &skill_level
    ))
        return NULL;

    result = staff_training_broadcast_reward_gold_per_minute(
        staff_level, zhimingdu, skill_base, skill_grow, skill_level
    );

    return Py_BuildValue("i", result);
}

// 训练加速所需钻石
static PyObject* wrap_training_speedup_need_diamond(PyObject* self, PyObject* args)
{
    int seconds;

    int result;

    if(!PyArg_ParseTuple(args, "i:training_speedup_need_diamond", &seconds))
        return NULL;

    result = training_speedup_need_diamond(seconds);
    return Py_BuildValue("i", result);
}


static PyMethodDef Methods[] = {
    {"staff_training_exp_need_gold", wrap_staff_training_exp_need_gold, METH_VARARGS, ""},
    {"staff_training_broadcast_reward_gold_per_minute", wrap_staff_training_broadcast_reward_gold_per_minute, METH_VARARGS, ""},
    {"training_speedup_need_diamond", wrap_training_speedup_need_diamond, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initformula(void)
{
    Py_InitModule("formula", Methods);
}
