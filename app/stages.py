from enum import Enum


def init_stages(stages_dict):
    def build_next_map(elements):
        result = {}
        for i in range(len(elements) - 1):
            result[elements[i]] = elements[i+1]
        return result
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
            'gives': stage_dict.get('gives', None),
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
        return {"type": Redirect.Complete}
    return {"type": Redirect.Other, "url": stage_next["path"]}


def meets_prerequisites(session, current_stage):
    details = session["stage_details"]
    current_stage = current_stage.removeprefix("app.")
    needs = details[current_stage]["needs"]
    for need in needs:
        if not session.get(need, False):
            return False
    return True


def check_repeat_visit(session, current_stage):
    details = session["stage_details"]
    current_stage = current_stage.removeprefix("app.")
    gives = details[current_stage]["gives"]
    return session.get(gives, None) if gives else None


def check_general_conditions(session):
    if "workerId" not in session:
        return {"type": Redirect.Error, "errno": 1000}
    elif "is_bot" in session:
        return {"type": Redirect.Error, "errno": 1005}
    elif "complete" in session:
        return {"type": Redirect.Complete}
    return None


Redirect = Enum("Redirect", ['Complete', 'Error', 'Other'])
