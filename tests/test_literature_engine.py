import unittest

from backend.config import Settings
from backend.engines.literature_engine import (
    parse_arxiv_atom_xml,
    parse_openalex_response,
    parse_pubchem_response,
    search_literature,
)


class TestLiteratureParsersAndOfflineHandling(unittest.TestCase):
    """Uses explicitly labeled test fixtures to verify real OpenAlex, arXiv, and PubChem schema parsers."""

    def test_openalex_parser_fixture(self):
        fixture = {
            "results": [
                {
                    "id": "https://openalex.org/W123",
                    "doi": "https://doi.org/10.1000/test",
                    "title": "Harmonic Analysis in Physics",
                    "publication_date": "2024-05-01",
                    "cited_by_count": 12,
                    "authorships": [{"author": {"display_name": "Dr. A. Sen"}}],
                    "primary_location": {"license": "cc-by"},
                    "abstract_inverted_index": {"Harmonic": [0], "models": [1], "converge.": [2]},
                }
            ]
        }
        parsed = parse_openalex_response(fixture)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["abstract"], "Harmonic models converge.")
        self.assertEqual(parsed[0]["access_scope"], "METADATA_AND_ABSTRACT")
        self.assertEqual(parsed[0]["source_url"], "https://doi.org/10.1000/test")

    def test_arxiv_atom_parser_fixture(self):
        xml_fixture = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <entry>
            <id>http://arxiv.org/abs/2401.12345v1</id>
            <published>2024-01-15T00:00:00Z</published>
            <title>Deterministic ODE Verification</title>
            <summary>Numerical stability benchmark.</summary>
            <author><name>R. Verma</name></author>
          </entry>
        </feed>'''
        parsed = parse_arxiv_atom_xml(xml_fixture)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["external_id"], "2401.12345v1")
        self.assertEqual(parsed[0]["authors"], ["R. Verma"])

    def test_pubchem_parser_fixture(self):
        fixture = {
            "PropertyTable": {
                "Properties": [
                    {
                        "CID": 2244,
                        "MolecularFormula": "C9H8O4",
                        "MolecularWeight": "180.16",
                        "CanonicalSMILES": "CC(=O)OC1=CC=CC=C1C(=O)O",
                        "IUPACName": "2-acetyloxybenzoic acid",
                    }
                ]
            }
        }
        parsed = parse_pubchem_response(fixture, "aspirin")
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["external_id"], "CID:2244")
        self.assertEqual(parsed[0]["source_url"], "https://pubchem.ncbi.nlm.nih.gov/compound/2244")

    def test_offline_returns_honest_not_connected(self):
        res = search_literature("quantum", "openalex", 3, Settings(), timeout_s=1.0)
        self.assertIn(res["status"], {"CONNECTED", "NOT_CONNECTED", "UPSTREAM_ERROR"})
        if res["status"] == "NOT_CONNECTED":
            self.assertEqual(res["count"], 0)
            self.assertEqual(res["results"], [])
            self.assertIn("No fake results", res["blocker"])
