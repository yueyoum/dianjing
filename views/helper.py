def parse_protocol_sync_formation_slots(data):
    result = []
    for d in data:
        result.append((d.id, d.index, d.policy))

    return result
