import sys
from pathlib import Path


def parse_input(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f]

    idx = 0
    while idx < len(lines) and lines[idx] == "":
        idx += 1

    # 1. Kaufbare Moleküle einlesen
    m_count = int(lines[idx])
    idx += 1
    shop = {}
    for _ in range(m_count):
        cost_str, mol = lines[idx].split(" -> ")
        shop[mol.strip()] = int(cost_str.strip())
        idx += 1

    while idx < len(lines) and lines[idx] == "":
        idx += 1

    # 2. Verfügbare Reaktionen einlesen
    r_count = int(lines[idx])
    idx += 1
    reactions = []
    for _ in range(r_count):
        raw = lines[idx]
        lhs_str, rhs_str = raw.split(" -> ")
        lhs = []
        for item in lhs_str.split(", "):
            cnt, mol = item.split(" ")
            lhs.append((mol.strip(), int(cnt.strip())))
        rhs = []
        for item in rhs_str.split(", "):
            cnt, mol = item.split(" ")
            rhs.append((mol.strip(), int(cnt.strip())))
        reactions.append({
            "raw": raw,
            "lhs": lhs,
            "rhs": rhs,
            "lhs_dict": dict(lhs),
            "rhs_dict": dict(rhs),
        })
        idx += 1

    while idx < len(lines) and lines[idx] == "":
        idx += 1

    # 3. Zielmoleküle einlesen
    n_count = int(lines[idx])
    idx += 1
    targets = []
    for _ in range(n_count):
        cnt, mol = lines[idx].split(" ")
        targets.append((mol.strip(), int(cnt.strip())))
        idx += 1

    return shop, reactions, targets


def compute_cost(shop, executed_rxns):
    """Simuliert das Inventar und berechnet die exakten Einkaufskosten."""
    inv = {}
    cost = 0
    for r in executed_rxns:
        for mol, qty in r["lhs"]:
            avail = inv.get(mol, 0)
            if avail >= qty:
                inv[mol] -= qty
            else:
                need = qty - avail
                inv[mol] = 0
                cost += need * shop[mol]
        for mol, qty in r["rhs"]:
            inv[mol] = inv.get(mol, 0) + qty
    return cost


def solve_instance(shop, reactions, targets):
    # Phase 1: Minimale Herstellkosten und zyklenfreien Rang bestimmen
    min_cost = {mol: float(cost) for mol, cost in shop.items()}
    best_rxn = {mol: None for mol in shop}
    rank = {mol: 0 for mol in shop}

    changed = True
    while changed:
        changed = False
        for r in reactions:
            lhs_dict = r["lhs_dict"]
            rhs_dict = r["rhs_dict"]

            if not all(mol in min_cost for mol, _ in r["lhs"]):
                continue

            raw_lhs_cost = 0.0
            max_lhs_rank = 0
            for mol, qty in r["lhs"]:
                net_qty = qty - rhs_dict.get(mol, 0)
                if net_qty > 0:
                    raw_lhs_cost += net_qty * min_cost[mol]
                else:
                    # Katalysator-Amortisation über mehrere Durchläufe
                    raw_lhs_cost += (qty * min_cost[mol]) / 10.0
                max_lhs_rank = max(max_lhs_rank, rank[mol])

            for prod, p_qty in r["rhs"]:
                if prod in lhs_dict and p_qty <= lhs_dict[prod]:
                    continue
                net_p_qty = p_qty - lhs_dict.get(prod, 0)
                unit_cost = raw_lhs_cost / net_p_qty
                if unit_cost + 1e-9 < min_cost.get(prod, float("inf")):
                    min_cost[prod] = unit_cost
                    best_rxn[prod] = r
                    rank[prod] = max_lhs_rank + 1
                    changed = True

    # Indexiere alle Reaktionen nach ihren Netto-Produkten
    rxns_by_prod = {}
    for r in reactions:
        lhs_dict = r["lhs_dict"]
        for prod, p_qty in r["rhs"]:
            if p_qty > lhs_dict.get(prod, 0):
                rxns_by_prod.setdefault(prod, []).append(r)

    # Phase 2: Rekursive Synthese mit Live-Inventar
    def run_simulation(target_mol, target_qty, cap_mode):
        inv = {}
        executed = []

        def request_molecule(mol, needed, active_stack=frozenset()):
            avail = inv.get(mol, 0)
            if avail >= needed:
                inv[mol] -= needed
                return needed

            reserved = avail
            inv[mol] = 0
            still_needed = needed - reserved

            while still_needed > 0:
                best_choice = best_rxn.get(mol, None)
                best_eff_cost = (
                    shop.get(mol, float("inf")) if best_choice is None else float("inf")
                )

                for cand in rxns_by_prod.get(mol, []):
                    lhs_dict = cand["lhs_dict"]
                    rhs_dict = cand["rhs_dict"]
                    net_gain = rhs_dict[mol] - lhs_dict.get(mol, 0)
                    if net_gain <= 0:
                        continue

                    feasible = True
                    cand_cost = 0.0
                    for r_mol, r_qty in cand["lhs"]:
                        in_inv = inv.get(r_mol, 0)
                        missing = max(0, r_qty - in_inv)
                        if missing > 0:
                            if (
                                r_mol not in min_cost
                                or r_mol in active_stack
                                or r_mol == mol
                            ):
                                feasible = False
                                break
                            if (
                                rank.get(r_mol, 999999) >= rank.get(mol, 999999)
                                and best_rxn.get(mol) != cand
                            ):
                                feasible = False
                                break
                            net_r = r_qty - rhs_dict.get(r_mol, 0)
                            if net_r > 0:
                                cand_cost += missing * min_cost[r_mol]
                            else:
                                cand_cost += (missing * min_cost[r_mol]) / 10.0

                    if not feasible:
                        continue

                    if cap_mode == "all":
                        denom = min(still_needed, net_gain)
                    elif cap_mode == "target":
                        denom = min(still_needed, net_gain) if mol == target_mol else net_gain
                    else:
                        denom = net_gain

                    eff_unit_cost = cand_cost / denom
                    if eff_unit_cost + 1e-9 < best_eff_cost:
                        best_eff_cost = eff_unit_cost
                        best_choice = cand

                # Basisfall: Direkt im Shop kaufen, sobald die übergeordnete Reaktion läuft
                if best_choice is None:
                    return reserved

                next_stack = active_stack | {mol}
                reserved_lhs = {}
                for r_mol, r_qty in best_choice["lhs"]:
                    res = request_molecule(r_mol, r_qty, next_stack)
                    reserved_lhs[r_mol] = res

                # Falls für ein Kauf-Edukt während der Unteraufrufe Nebenprodukte
                # im Inventar entstanden sind, werden diese beim Reaktionsschritt verbraucht
                for r_mol, r_qty in best_choice["lhs"]:
                    deficit = r_qty - reserved_lhs[r_mol]
                    if deficit > 0:
                        use_now = min(deficit, inv.get(r_mol, 0))
                        inv[r_mol] = inv.get(r_mol, 0) - use_now

                executed.append(best_choice)
                for p_mol, p_qty in best_choice["rhs"]:
                    inv[p_mol] = inv.get(p_mol, 0) + p_qty

                take = min(still_needed, inv.get(mol, 0))
                inv[mol] -= take
                still_needed -= take
                reserved += take

            return reserved

        request_molecule(target_mol, target_qty)
        return executed

    paragraphs = []
    for target_mol, target_qty in targets:
        best_exec = None
        best_cost = float("inf")
        for mode in ("all", "target", "none"):
            exec_rxns = run_simulation(target_mol, target_qty, mode)
            cost = compute_cost(shop, exec_rxns)
            if cost < best_cost:
                best_cost = cost
                best_exec = exec_rxns
        paragraphs.append([r["raw"] for r in best_exec])

    return paragraphs


def write_output(filepath, paragraphs):
    # Jeder Ziel-Auftrag als Absatz, getrennt durch eine Leerzeile
    output_text = "\n\n".join("\n".join(lines) for lines in paragraphs) + "\n"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(output_text)


def process_file(input_path, output_path):
    shop, reactions, targets = parse_input(input_path)
    paragraphs = solve_instance(shop, reactions, targets)
    write_output(output_path, paragraphs)


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        # Aufruf für eine einzelne Datei:
        # python solve_level3.py in_level-3_1-small.txt out_level-3_1-small.txt
        in_file = sys.argv[1]
        out_file = sys.argv[2]
        process_file(in_file, out_file)
        print(f"Fertig! Ausgabe gespeichert in: {out_file}")
    elif len(sys.argv) == 2:
        # Aufruf nur mit Input-Datei (erzeugt automatisch passenden Output-Dateinamen)
        in_path = Path(sys.argv[1])
        out_name = in_path.name.replace("in_", "out_", 1)
        if out_name == in_path.name:
            out_name = "out_" + in_path.name
        out_path = in_path.with_name(out_name)
        process_file(in_path, out_path)
        print(f"Fertig! Ausgabe gespeichert in: {out_path}")
    else:
        # Ohne Argumente: Verarbeitet automatisch alle in_level-3_*.txt im aktuellen Ordner
        for in_path in sorted(Path(".").glob("in_level-3_*.txt")):
            out_path = in_path.with_name(in_path.name.replace("in_", "out_", 1))
            process_file(in_path, out_path)
            print(f"Verarbeitet: {in_path.name} -> {out_path.name}")
