def merge_intervals(intervals, merge_threshold_s):
    if not intervals: return []
    ints = sorted([list(x) for x in intervals], key=lambda x: x[0])
    merged = [ints[0]]
    for s,e in ints[1:]:
        ls, le = merged[-1]
        if s - le < merge_threshold_s:
            merged[-1][1] = max(le, e)
        else:
            merged.append([s,e])
    return merged
