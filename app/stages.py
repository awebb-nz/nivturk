
def init_stages(stages_dict):
    stage_order = list(stages_dict.keys())
    windows = pairs(stage_order)
    stage_next = {}
    for k, v in windows:
        val = {
            'name': v,
            'path': stages_dict[v]["path"]
        }
        stage_next[k] = val
    return stage_order, stage_next


def next_stage(session, current_stage=None):
    if current_stage is None:
        current_stage = session["stages"][0]
    current_stage = current_stage.removeprefix("app.")
    ns = session["next_stage"][current_stage]
    return ns["name"], ns["path"]


def pairs(elements):
    result = []
    for i in range(len(elements) - 1):
        result.append((elements[i], elements[i+1]))
    return result
