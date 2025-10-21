def merge_intervals(iv, gap=5):
    if not iv: return []
    iv.sort()
    out = [list(iv[0])]
    for a,b in iv[1:]:
        if a - out[-1][1] <= gap: out[-1][1] = max(out[-1][1], b)
        else: out.append([a,b])
    return [tuple(x) for x in out]
