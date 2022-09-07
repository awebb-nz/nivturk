
def init_stages(stages_dict):
    stage_order = list(stages_dict.keys())
    next_map = build_next_map(stage_order)
    print(f"next_map = {next_map}")
    stage_details = {}
    for stage in stage_order:
        stage_dict = stages_dict[stage]
        val = {
            'name': stage,
            'path': stage_dict["path"],
            'needs': stage_dict.get('needs', []),
            'next': next_map.get(stage, None)
        }
        stage_details[stage] = val
    return stage_order, stage_details


def next_stage(session, current_stage=None):
    details = session["stage_details"]
    if current_stage is None:
        first_stage = session["stages"][0]
        return details[first_stage]
    current_stage = current_stage.removeprefix("app.")
    current_details = details[current_stage]
    stage_next = current_details["next"]
    return details[stage_next] if stage_next else None


def next_stage_path(session, current_stage=None):
    stage_next = next_stage(session, current_stage)
    if stage_next is None:
        return "complete.complete"
    return stage_next["path"]


def build_next_map(elements):
    result = {}
    for i in range(len(elements) - 1):
        result[elements[i]] = elements[i+1]
    return result
