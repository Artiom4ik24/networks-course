import argparse, json, ipaddress, random, itertools, copy
INF = 16


class Router:
    def __init__(self, ip):
        self.ip = ip
        self.neigh_cost = {}
        self.table = {ip: (ip, 0)}

    def add_neighbor(self, neigh_ip, cost=1):
        self.neigh_cost[neigh_ip] = cost
        self.table.setdefault(neigh_ip, (neigh_ip, cost))

    def create_update(self):
        return {dst: metric for dst, (_, metric) in self.table.items()}

    def process_update(self, from_ip, update_dict):
        changed = False
        cost_to_neighbor = self.neigh_cost[from_ip]
        for dest, m in update_dict.items():
            if dest == self.ip:
                continue
            new_metric = min(INF, m + cost_to_neighbor)
            nh, old_metric = self.table.get(dest, (None, INF))
            if new_metric < old_metric:
                self.table[dest] = (from_ip, new_metric)
                changed = True
        return changed

def random_ipv4_pool(n):
    pool=set()
    while len(pool) < n:
        ip = f"198.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
        pool.add(ip)
    return list(pool)

def build_random_as(num_nodes, density=0.4):
    ips = random_ipv4_pool(num_nodes)
    routers = {ip: Router(ip) for ip in ips}
    pairs = list(itertools.combinations(ips, 2))
    random.shuffle(pairs)
    needed = int(len(pairs)*density)
    for a,b in pairs[:needed]:
        cost = random.randint(1,5)
        routers[a].add_neighbor(b, cost)
        routers[b].add_neighbor(a, cost)

    for r in routers.values():
        if not r.neigh_cost:
            tgt = random.choice([x for x in ips if x!=r.ip])
            routers[r.ip].add_neighbor(tgt, 1)
            routers[tgt].add_neighbor(r.ip, 1)
    return routers


def print_table(router_ip, table, prefix=""):
    print(f"{prefix}[Source IP]      [Destination IP]    [Next Hop]       [Metric]")
    for dst, (nh, met) in sorted(table.items()):
        print(f"{prefix}{router_ip:15} {dst:15} {nh:15} {met:7}")


def simulate_rip(routers, max_rounds=100):
    for rnd in range(1, max_rounds + 1):
        changed_any = False
        updates = {ip: r.create_update() for ip,r in routers.items()}

        for ip, r in routers.items():
            for neigh in r.neigh_cost:
                changed_any |= routers[neigh].process_update(ip, updates[ip])

        print(f"\n=== Simulation step {rnd} ===")
        for ip, r in routers.items():
            print(f"\nSimulation step {rnd} of router {ip}")
            print_table(ip, r.table, prefix="")

        if not changed_any:
            return rnd

    return max_rounds

def main():
    parser = argparse.ArgumentParser(description="Console RIP emulator")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--number", type=int, help="случайная сеть из N маршрутизаторов")
    parser.add_argument("--density", type=float, default=0.4,
                        help="плотность рёбер 0..1 (для --random)")
    args = parser.parse_args()
    routers = build_random_as(args.number, args.density)

    rounds = simulate_rip(routers)
    print(f"\nConverged in {rounds} RIP round(s).")
    for ip, r in routers.items():
        print(f"Final state of router {ip} table:")
        print_table(ip, r.table)

if __name__ == "__main__":
    main()
