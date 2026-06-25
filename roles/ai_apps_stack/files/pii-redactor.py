"""
title: Brazilian PII Redactor
author: arch-corp
version: 0.1
description: Redige CPF, CNPJ e numeros de cartao antes de enviar ao modelo.
"""
import re


class Filter:
    def __init__(self):
        self.patterns = {
            "CPF": re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
            "CNPJ": re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b"),
            "CARD": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
        }

    async def inlet(self, body: dict, __user__: dict | None = None) -> dict:
        for msg in body.get("messages", []):
            for label, pat in self.patterns.items():
                msg["content"] = pat.sub(f"[REDACTED_{label}]", msg["content"])
        return body
