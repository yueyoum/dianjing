def parse_protocol_sync_formation_slots(data, policy=None):
    result = []
    for d in data:
        if policy:
            this_policy = policy
        else:
            this_policy = d.policy

        result.append((d.id, d.index, this_policy))

    return result
