
from apps.staff.core import StaffManager
from utils.http import ProtobufResponse

from protomsg.staff_pb2 import StaffTrainingResponse, StaffTrainingGetRewardResponse

def training_start(request):
    req = request._proto
    staff_id = req.staff_id
    training_id = req.training_id

    session = request._game_session
    char_id = session.char_id

    StaffManager(char_id).training_start(staff_id, training_id)

    response = StaffTrainingResponse()
    response.ret = 0
    return ProtobufResponse(response)

def training_get_reward(request):
    req = request._proto
    staff_id = req.staff_id
    training_id = req.training_id

    session = request._game_session
    char_id = session.char_id

    StaffManager(char_id).training_get_reward(staff_id, training_id)

    response = StaffTrainingGetRewardResponse()
    response.ret = 0
    return ProtobufResponse(response)
