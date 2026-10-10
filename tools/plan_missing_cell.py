#!/usr/bin/env python3
import base64
import json

from tools.analyze_salphaseion import split_segments
from tools.gsmg import ARTIFACTS, SOURCES, extract_grid, spiral_coordinates
from tools.prime_boundary import binary_boundary
from tools.research_common import fingerprint, source_record, write_once_json


OUTPUT = ARTIFACTS / "cycle05"


def missing_cell_matrices():
    image = extract_grid(SOURCES / "gsmg-puzzle.png")
    anomalies = [(row, column) for row in range(14) for column in range(14) if image["colors"][row][column] == "near_white"]
    if len(anomalies) != 1:
        raise ValueError("Expected exactly one source near-white cell")
    hole = anomalies[0]
    prefix = split_segments()["dbbi"]
    binary = binary_boundary()["letters"]
    if len(prefix) != 91 or len(binary) != 104 or len(prefix + binary) != 14 * 14 - 1:
        raise ValueError("Annotated source does not leave exactly one image cell")
    routes = {"row-major": [(row, column) for row in range(14) for column in range(14)], "column-major": [(row, column) for column in range(14) for row in range(14)], "verified-counterclockwise-spiral": list(spiral_coordinates(14))}
    for mapping in ("all-a1-i9", "dbbi-a1-i9-binary-a0-b1"):
        prefix_values = [ord(symbol) - 96 for symbol in prefix]
        binary_values = [ord(symbol) - 96 if mapping == "all-a1-i9" else int(symbol == "b") for symbol in binary]
        values = prefix_values + binary_values
        for route, cells in routes.items():
            matrix = [[0] * 14 for row in range(14)]
            available = [cell for cell in cells if cell != hole]
            for (row, column), value in zip(available, values):
                matrix[row][column] = value
            if len(available) != len(values) or matrix[hole[0]][hole[1]] != 0:
                raise ValueError("Source coverage or zero-hole invariant fails")
            yield {"value_mapping": mapping, "fill_route": route, "near_white_hole_zero_based": list(hole), "hole_route_offset_zero_based": cells.index(hole), "source_symbols": len(values), "total": sum(values)}, matrix


def derive_candidates():
    matrices = []
    lists = {}
    for parameters, matrix in missing_cell_matrices():
        matrices.append({"parameters": parameters, "matrix": matrix})
        rows = list(map(sum, matrix))
        columns = list(map(sum, zip(*matrix)))
        for axis, sums in (("rows", rows), ("columns", columns), ("rows-then-columns", rows + columns), ("columns-then-rows", columns + rows)):
            for reverse in (False, True):
                values = sums[::-1] if reverse else sums
                lists.setdefault(tuple(values), []).append(parameters | {"axis_order": axis, "reverse": reverse})
    forms = []
    passwords = {}
    for sums, provenance in lists.items():
        decimal = "".join(map(str, sums))
        number = int(decimal)
        representations = {"one-byte-totals": bytes(sums), "decimal-concatenation": decimal.encode(), "decimal-comma-list": ",".join(map(str, sums)).encode(), "decimal-minimal-integer-big-endian": number.to_bytes((number.bit_length() + 7) // 8, "big")}
        for representation, material in representations.items():
            parameters = {"provenance": provenance, "unreduced_sums": list(sums), "representation": representation, "integer_leading_zero_policy": "Minimal integer bytes; no invented leading zero"}
            forms.append({"parameters": parameters, "material_base64": base64.b64encode(material).decode()})
            for transform, password in (("raw", material), ("sha256-lowerhex", fingerprint(material).encode()), ("sha256-raw", bytes.fromhex(fingerprint(material)))):
                candidate = passwords.setdefault(fingerprint(password), {"password_hex": password.hex(), "provenance": []})
                candidate["provenance"].append(parameters | {"password_transform": transform})
    return matrices, lists, forms, passwords


def plan():
    matrices, lists, forms, passwords = derive_candidates()
    report = {"id": "C05-NEXT-MISSING-CELL", "status": "UNTESTED", "source_evidence": [source_record(SOURCES / "gsmg-puzzle.png", "Actual near-white cell at zero-based7,4; verified spiral index163"), source_record(SOURCES / "salphaseion.html", "Exact dbbi91 followed by intact104-letter matrixsumlist label"), source_record(SOURCES.parent / "evidence/cycle05/fork-solver__prime_host_delta.cjs", "Secondary tested coverage explicitly prepends/appends zero; inspected, never executed")], "hypothesis": "The195 source symbols occupy196 image cells except the actual anomaly; its zero-filled cell is an omitted slot rather than arbitrary endpoint padding, and matrixsumlist requests axis sums", "invariant": "Place every original symbol once, in preserved order under the stated route, while leaving only the actual anomaly cell zero. Original image/source bytes remain unchanged.", "justification": "Combines exact195=14²−1 length, single near-white anomaly, zeroed-out wording and matrixsumlist. Source-adjacent digit conventions constrain the two value mappings; row/column fills are weaker alternatives to the already verified spiral. This is a construction hypothesis, not a proven instruction.", "search_space": {"value_mappings": 2, "fill_routes": 3, "matrices": len(matrices), "axis_orders": 4, "directions": 2, "distinct_sum_lists": len(lists), "material_representations": 4, "forms": len(forms), "password_transforms": 3, "unique_passwords": len(passwords), "targets": ["phase32-inner", "salphaseion-small", "cosmic-duality"], "kdf_digests": ["md5", "sha256"], "planned_aes_trials": len(passwords) * 6}, "candidate_set_sha256": fingerprint(b"\x00".join(sorted(bytes.fromhex(candidate["password_hex"]) for candidate in passwords.values()))), "estimated_crypto_seconds": round(len(passwords) * 6 / 50000, 4), "throughput_basis": "Planning estimate50000 trials/second from previous finite AES runs; excludes I/O and scoring", "gate": "Recognized independently justified next-stage structure or exact scoped target, with bounded adjacent raw-key gate for small-blob hits", "limits": "Plan only; no AES executed. No arbitrary hole placement, token edits, image mutation, free row/column permutations, key dictionaries or added speech fragments. Fork's reported negative coverage is secondary evidence, not added to local tested totals.", "matrices": matrices, "forms": forms, "passwords": passwords}
    write_once_json(OUTPUT / "next-missing-cell-plan.json", report)
    print(json.dumps({name: value for name, value in report.items() if name not in ("matrices", "forms", "passwords")}, indent=2))
    return report


if __name__ == "__main__":
    plan()
