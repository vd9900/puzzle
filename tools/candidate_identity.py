from tools.research_common import fingerprint


DOMAIN = b"gsmg-candidate-identity\x00"
POLICY = "SHA256(gsmg-candidate-identity NUL || password); untagged SHA256(password) is computed only in memory for legacy no-repeat comparisons. This prevents a raw-material identifier from displaying its SHA256-lowerhex password variant"


def tagged_identity(password):
    return fingerprint(DOMAIN + password)


def previously_tested(password, identifiers):
    return fingerprint(password) in identifiers or tagged_identity(password) in identifiers
