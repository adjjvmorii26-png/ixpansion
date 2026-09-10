# Identity Protocol

## States
UNBOUND → BOUND → ROTATING → MIGRATED → REVOKED

## Rules
- BIND requires suite of current epoch
- ROTATING requires dual control (INV-07)
- MIGRATED records old→new mapping in testament
- REVOKED is terminal for that key material
