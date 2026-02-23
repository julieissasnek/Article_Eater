import json

def get_cycles(pairs, node_set):
    from collections import defaultdict
    adj = defaultdict(list)
    for s, t, _ in pairs:
        if s in node_set and t in node_set:
            adj[s].append(t)
            
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in node_set}
    
    def dfs(u):
        color[u] = GRAY
        for v in adj.get(u, []):
            if color[v] == GRAY:
                return (u, v)
            if color[v] == WHITE:
                res = dfs(v)
                if res:
                    return res
        color[u] = BLACK
        return None

    for n in node_set:
        if color[n] == WHITE:
            res = dfs(n)
            if res:
                return res
    return None

def main():
    try:
        with open("data/production/realtime_incremental_bn.json", "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    nodes = [str(n) for n in data.get("nodes", []) if n is not None]
    node_set = set(nodes)

    raw_edges = data.get("edges", {})
    pairs = []
    
    # Matching check_web_bn_health.py parsing
    if isinstance(raw_edges, dict):
        for k, e in raw_edges.items():
            if not isinstance(e, dict):
                continue
            s = e.get("source")
            t = e.get("target")
            if s is None or t is None:
                continue
            pairs.append((str(s), str(t), k))
    
    cycles_broken = 0
    while True:
        cycle_edge = get_cycles(pairs, node_set)
        if not cycle_edge:
            break
            
        u, v = cycle_edge
        
        # Find and remove from pairs
        for i, (s, t, k) in enumerate(pairs):
            if s == u and t == v:
                pairs.pop(i)
                if k in data["edges"]:
                    del data["edges"][k]
                cycles_broken += 1
                break

    print(f"Broke {cycles_broken} cycles")
    
    with open("data/production/realtime_incremental_bn.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()
