import ast
import json
import re

from tools.carry_forward_ownership import mapped_literal
from tools.instruction_graphs import ROOT, source, write_artifact


OUTPUT = ROOT / "research/artifacts/cycle20"
FEN = "B5KR/1r5B/6R1/2b1p1p1/2P1k1P1/1p2P2p/1P2P2P/3N1N2 w - - 0 1"
NEXT_TEST = "Inspect one fixed original creator-attributed March14 2021 statement about breaking SalPhaseIon giving the feeling of the phase's name, cross-check its original transcript body and compare only exact authored SalPhaseIon/Cosmic Duality headings and frozen checkpoint wording. Determine whether phase-name semantics provides an object-role constraint rather than a new algorithm or literal-output gate. Do not generate name permutations, decode new text or repeat checkpoint/cover experiments."


def fen_rank_widths(value):
    fields = value.split()
    if len(fields) != 6:
        raise ValueError("Expected six FEN fields")
    ranks = fields[0].split("/")
    if len(ranks) != 8:
        raise ValueError("Expected eight FEN ranks")
    widths = []
    for rank in ranks:
        if not re.fullmatch(r"[1-8KQRBNPkqrbnp]+", rank):
            raise ValueError("Invalid FEN rank symbol")
        width = sum(int(symbol) if symbol.isdigit() else 1 for symbol in rank)
        if width != 8:
            raise ValueError("Invalid FEN rank width")
        widths.append(width)
    return widths


def existing_codebook_domains():
    path = ROOT / "tools/gsmg.py"
    tree = ast.parse(path.read_text())
    matches = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "checkerboard"]
    if len(matches) != 1:
        raise ValueError("Expected one existing codebook function")
    function = matches[0]
    literals = [node.value for node in ast.walk(function) if isinstance(node, ast.Constant) and isinstance(node.value, str)]
    if literals != ["02356789", "fubcdora", "1", "4", "/lethingky", "mvpszjqwx."]:
        raise ValueError("Existing codebook grammar differs from frozen implementation")
    return {
        "source": source(path), "function_line_one_based": function.lineno,
        "single_digit_column_domain": [int(symbol) for symbol in literals[0]],
        "prefixed_row_domains": [list(range(len(literals[4]))), list(range(len(literals[5])))],
        "column_count": 10, "filled_first_row_symbols": 8,
        "eight_filled_symbols_is_not_eight_column_domain": True,
        "static_AST_inspection_only_no_codebook_or_decoder_execution": True,
    }


def report():
    preceding = ROOT / "research/artifacts/cycle20/carry-forward-ownership.json"
    frozen = json.loads(preceding.read_text())
    if frozen["id"] != "C20-CARRY-FORWARD-OWNERSHIP" or "as wide as the first one seen" not in frozen["next_test"]:
        raise ValueError("Unexpected frozen width-reference task")
    source_domain_path = ROOT / "research/artifacts/cycle19/first-piece-domain-v2.json"
    domain = json.loads(source_domain_path.read_text())
    frame_path = ROOT / "research/artifacts/cycle15/frame-object-audit.json"
    frame = json.loads(frame_path.read_text())
    branch_path = ROOT / "research/artifacts/cycle12/source-join-preflight-v2.json"
    branches = json.loads(branch_path.read_text())["source_paragraph_roles"]
    clue = branches["checkerboard_width_clue"]
    path = ROOT / "research/artifacts/phase32.txt"
    payload = path.read_bytes()
    start, end = clue["byte_span_zero_based_half_open"]
    if payload[start:end] != b"as wide as the first one seen" or clue["belongs_to_paragraph_index_zero_based"] != 4:
        raise ValueError("Unexpected original width-reference bytes")
    fen_anchor = mapped_literal(ROOT / "research/sources/phase2.html", FEN, "EARLIER_FEN_BOARD_WIDTH_NOT_A_RECOMPUTED_MOVE")
    chess_widths = fen_rank_widths(FEN)
    codebook = existing_codebook_domains()
    asset_count = len(domain["page_inventory"]["pages"][0]["body_image_references"])
    if asset_count != 8:
        raise ValueError("Unexpected frozen later-page asset count")
    objects = [
        {"object": "original14x14 grid", "width_kind": "grid_cell_columns", "known_width": 14, "codebook_width_equal": False, "earlier_than_current_clue_in_known_pipeline": True, "authored_first_one_antecedent_assignment": False, "limitation": "Grid width14 is known; width type and shared operand are not assigned"},
        {"object": "earlier eight-image page", "width_kind": "asset_count_not_authored_spatial_width", "known_width": None, "asset_count": asset_count, "codebook_width_equal": None, "earlier_than_current_clue_in_known_pipeline": True, "authored_first_one_antecedent_assignment": False, "limitation": "Eight references do not define one authored board or column domain"},
        {"object": "earlier FEN chess board", "width_kind": "chess_files_per_rank", "known_width": chess_widths[0], "rank_widths": chess_widths, "codebook_width_equal": False, "earlier_than_current_clue_in_known_pipeline": True, "authored_first_one_antecedent_assignment": False, "limitation": "Eight files differ from current10-column codebook; first row's eight filled symbols is another type"},
        {"object": "current decimal checkerboard", "width_kind": "codebook_digit_column_domain", "known_width": codebook["column_count"], "codebook_width_equal": True, "earlier_than_current_clue_in_known_pipeline": False, "authored_first_one_antecedent_assignment": False, "limitation": "Self-width equality is tautological; current implementation is not an earlier primary antecedent"},
    ]
    evidence = [source(item) for item in (preceding, source_domain_path, frame_path, branch_path, path, ROOT / "research/sources/phase2.html", ROOT / "tools/gsmg.py")]
    locations = ["research/artifacts/phase32.txt:9", "research/sources/phase2.html:39", "tools/gsmg.py:272", "research/artifacts/cycle19/first-piece-domain-v2.json", "research/artifacts/cycle15/frame-object-audit.json", "research/artifacts/cycle12/source-join-preflight-v2.json"]
    hypotheses = [
        {"id": "C20-WIDTH-EQUAL-DOMAIN", "hypothesis": "As wide as first one seen requires the current codebook to have exactly the same column-domain width as the original grid or earlier chess board", "assumptions": ["Wide means column-domain size", "First one names one of those two earlier boards", "The existing decoded codebook is the intended current object"], "confidence": "HIGH observed10-versus14/8 difference; LOW literal equality reading", "contradictions": ["Known widths are14,8 and10, not equal", "Original phrase names no board or metric", "A decoded-output implementation cannot silently replace source-authored geometry"]},
        {"id": "C20-WIDTH-REFERENCE-TYPE", "hypothesis": "The width clause is a board/source analogy or a different width metric rather than literal equality of column domains", "assumptions": ["As wide may refer to a different object/representation", "A source-authored antecedent remains to be identified"], "confidence": "MEDIUM type distinction; UNKNOWN intended source or metric", "contradictions": ["The comparative wording may be operative", "No alternative metric is directly specified", "Asset-count or populated-symbol equality is not a column-width equality"]},
    ]
    hypotheses = [entry | {
        "status": "INCONCLUSIVE", "source_evidence": evidence, "source_locations": locations,
        "operation_order": ["reuse exact width-clue span", "type four fixed source objects", "compare only known widths without reconstructing anything"],
        "input": "Frozen original grid/page, primary FEN and static existing codebook domains",
        "output": "One typed width-reference interpretation with antecedent/metric unresolved",
        "next_test": NEXT_TEST,
    } for entry in hypotheses]
    return {
        "id": "C20-BOARD-WIDTH-REFERENCE", "date": "2026-10-01", "status": "INCONCLUSIVE",
        "hypothesis": "The explicit first-one-seen width reference supplies an authored earlier-board binding for the current construction",
        "source_evidence": evidence, "source_locations": locations,
        "assumptions": ["Only four already documented object types are compared", "Component counts, occupied symbols, pixels and column domains are not interchangeable", "No FEN move, grid traversal, codec or alphabet is reconstructed"],
        "operation_order": ["validate frozen width task", "verify exact original width-clue bytes", "reuse existing image/page/frame ownership", "validate original FEN rank widths without a move", "inspect existing codebook AST domains without executing it", "compare four typed objects and two readings"],
        "input": "One exact primary phrase, fixed earlier source objects and preserved codebook implementation",
        "output": "Typed width compatibility table, original source spans and two unresolved referent hypotheses",
        "confidence": "HIGH byte/width/type properties; UNKNOWN authored first-one antecedent",
        "width_clue_reused": {"source": source(branch_path), "original_source": source(path), **clue},
        "fen_anchor": fen_anchor, "codebook_domains": codebook, "typed_objects": objects,
        "source_frame_reused": {"source": source(frame_path), "no_new_grid_or_frame_extraction": True, "existing_report_id": frame["id"]},
        "no_fixed_object_has_all_of_earlier_status_type_width_and_authored_antecedent": True,
        "hypotheses": hypotheses,
        "result": "Original width clause belongs to alphabet-clue paragraph4. Four fixed objects separate14 grid columns, eight later-page assets without board width, eight chess files and current10-column decimal codebook. Its first row has eight filled symbols but ten possible columns; these are not the same type. Literal same-column-domain equality with grid/chess fails narrowly; no antecedent, alternate metric or new construction is assigned. Existing codebook/decode remains untouched.",
        "contradictions": ["No primary antecedent assignment names an earlier board", "Equal component counts do not establish equal width metrics", "The known decoded codebook is secondary implementation evidence, not independent author intent"],
        "next_test": NEXT_TEST,
        "search_space": {"original_width_clauses": 1, "fixed_typed_objects": 4, "FEN_ranks_validated": 8, "existing_codebook_functions_statically_inspected": 1, "declared_width_readings": 2, "new_board_variants": 0},
        "new_cryptographic_trials": 0, "new_trial_inputs": 0,
    }


def main():
    document = report()
    write_artifact(OUTPUT / "board-width-reference.json", (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"status": document["status"], "fixed_objects": 4, "grid_columns": 14, "chess_files": 8, "codebook_columns": 10, "authored_antecedent": False, "new_board_variants": 0}, indent=2))


if __name__ == "__main__":
    main()
