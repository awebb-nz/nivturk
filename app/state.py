from collections import OrderedDict
import json
import os

InitFile = "app.json"


class AppState:

    __slots__ = ["flask_settings", "directory_settings",
                 "stage_order", "stages"]

    def __init__(self, flask, directory, stage_order, stages):
        self.flask_settings = flask
        self.directory_settings = directory
        self.stage_order = stage_order
        self.stages = stages

    def all_gives(self):
        return [stage.gives for stage in self.stages]

    def get_stage(self, current_stage_name=None):
        if current_stage_name is None:
            first_stage = self.stage_order[0]
            return self.stages[first_stage]
        current_stage_name = current_stage_name.removeprefix("app.")
        return self.stages.get(current_stage_name, None)

    def get_next_stage(self, current_stage):
        return self.stages.get(current_stage.next_stage, None)

    def ensure_directories(self, root_dir):
        for d in self.directory_settings.values():
            maybe_dir = os.path.join(root_dir, d)
            if not os.path.isdir(maybe_dir):
                os.makedirs(maybe_dir)


class Stage:

    __slots__ = ["path", "filepath", "needs", "gives", "next_stage"]

    def __init__(self, path, filepath, needs, gives, next_stage):
        self.path = path
        self.filepath = filepath
        self.needs = needs
        self.gives = gives
        self.next_stage = next_stage

    def check_prerequisites(self, session):
        for need in self.needs:
            if not session.get(need, False):
                return False
        return True


def load_app_state(init_file: str) -> AppState:
    cfg = json.load(open(init_file), object_pairs_hook=OrderedDict)
    print(cfg)
    flask_settings = cfg["flask"]
    directory_settings = cfg["IO"]
    stage_order = cfg["stage_order"]
    next_map = build_next_map(stage_order)
    stages = {}
    for (name, stage) in cfg["stages"].items():
        stage_path = stage.get("path", None)
        stage_filepath = stage.get("filepath", None)
        stage_needs = stage.get("need", None)
        stage_gives = stage.get("gives", None)
        stage_next = next_map.get(name, None)
        stages[name] = Stage(stage_path, stage_filepath, stage_needs,
                             stage_gives, stage_next)
    return AppState(flask_settings, directory_settings, stage_order, stages)


def build_next_map(elements):
    result = {}
    for i in range(len(elements) - 1):
        result[elements[i]] = elements[i+1]
    return result


State = load_app_state(InitFile)
