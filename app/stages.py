
def init_stages(stages_dict):
    stage_order = list(stages_dict.keys())
    windows = sliding_window(stage_order)
    stage_next = {}
    for k, v in windows:
        stage_next[k] = v
    return stage_order, stage_next


def sliding_window(elements, window_size=2):
    if len(elements) <= window_size:
        return elements
    result = []
    for i in range(len(elements) - window_size + 1):
        result.append(elements[i:i+window_size])
    return result
