import time
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

import httpx

from backend.config import Settings


OPENALEX_WORKS_URL = "https://api.openalex.org/works"
ARXIV_API_URL = "https://export.arxiv.org/api/query"
PUBCHEM_BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name"

_last_arxiv_call: float = 0.0
_last_pubchem_call: float = 0.0


def reconstruct_openalex_abstract(inverted_index: Optional[Dict[str, List[int]]]) -> Optional[str]:
    if not inverted_index:
        return None
    positions: List[tuple] = []
    for word, idxs in inverted_index.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort(key=lambda pair: pair[0])
    return " ".join(word for _, word in positions)


def parse_openalex_response(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for item in data.get("results", []):
        authors = [
            a.get("author", {}).get("display_name", "Unknown")
            for a in item.get("authorships", [])
            if a.get("author", {}).get("display_name")
        ]
        doi = item.get("doi")
        oa_id = item.get("id", "")
        primary_loc = item.get("primary_location") or {}
        source_url = doi or primary_loc.get("landing_page_url") or oa_id
        license_str = primary_loc.get("license")
        records.append(
            {
                "provider": "openalex",
                "external_id": doi or oa_id,
                "title": item.get("title") or "Untitled work",
                "authors": authors,
                "published_date": str(item.get("publication_date") or item.get("publication_year") or ""),
                "abstract": reconstruct_openalex_abstract(item.get("abstract_inverted_index")),
                "access_scope": "METADATA_AND_ABSTRACT",
                "source_url": source_url,
                "license": license_str,
                "cited_by_count": item.get("cited_by_count"),
                "raw_metadata": {
                    "openalex_id": oa_id,
                    "doi": doi,
                    "cited_by_count": item.get("cited_by_count"),
                    "type": item.get("type"),
                },
            }
        )
    return records


def parse_arxiv_atom_xml(xml_text: str) -> List[Dict[str, Any]]:
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_text)
    records: List[Dict[str, Any]] = []
    for entry in root.findall("atom:entry", ns):
        entry_id = (entry.findtext("atom:id", default="", namespaces=ns) or "").strip()
        title = " ".join((entry.findtext("atom:title", default="", namespaces=ns) or "").split())
        summary = " ".join((entry.findtext("atom:summary", default="", namespaces=ns) or "").split())
        published = (entry.findtext("atom:published", default="", namespaces=ns) or "").strip()
        authors = [
            (a.findtext("atom:name", default="", namespaces=ns) or "").strip()
            for a in entry.findall("atom:author", ns)
        ]
        authors = [a for a in authors if a]
        if not entry_id:
            continue
        records.append(
            {
                "provider": "arxiv",
                "external_id": entry_id.split("/abs/")[-1],
                "title": title or "Untitled arXiv preprint",
                "authors": authors,
                "published_date": published[:10] if published else "",
                "abstract": summary or None,
                "access_scope": "METADATA_AND_ABSTRACT",
                "source_url": entry_id,
                "license": "arXiv non-exclusive license (see landing page)",
                "raw_metadata": {"atom_id": entry_id, "published": published},
            }
        )
    return records


def parse_pubchem_response(data: Dict[str, Any], query_name: str) -> List[Dict[str, Any]]:
    props = data.get("PropertyTable", {}).get("Properties", [])
    records: List[Dict[str, Any]] = []
    for p in props:
        cid = p.get("CID")
        if cid is None:
            continue
        formula = p.get("MolecularFormula", "N/A")
        weight = p.get("MolecularWeight", "N/A")
        smiles = p.get("CanonicalSMILES") or p.get("ConnectivitySMILES") or "N/A"
        iupac = p.get("IUPACName") or query_name
        records.append(
            {
                "provider": "pubchem",
                "external_id": f"CID:{cid}",
                "title": f"{query_name} ({formula})",
                "authors": ["NIH PubChem"],
                "published_date": "",
                "abstract": f"IUPAC: {iupac} | Formula: {formula} | MW: {weight} g/mol | SMILES: {smiles}",
                "access_scope": "COMPOUND_RECORD",
                "source_url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}",
                "license": "Public Domain (NIH/NLM)",
                "raw_metadata": p,
            }
        )
    return records


def search_literature(
    query: str,
    provider: str,
    limit: int,
    settings: Settings,
    timeout_s: float = 8.0,
) -> Dict[str, Any]:
    global _last_arxiv_call, _last_pubchem_call
    q = query.strip()
    if not q:
        raise ValueError("Search query must not be empty.")
    prov = provider.lower().strip()
    limit = max(1, min(limit, 20))
    headers = {"User-Agent": "ANVESHAN-Research-Lab/1.2 (https://github.com/dhundhwana-arch/ANVESHAN)"}

    try:
        if prov == "openalex":
            params: Dict[str, Any] = {"search": q, "per-page": limit}
            if settings.openalex_email:
                params["mailto"] = settings.openalex_email
            if settings.openalex_api_key:
                params["api_key"] = settings.openalex_api_key
            resp = httpx.get(OPENALEX_WORKS_URL, params=params, headers=headers, timeout=timeout_s)
            resp.raise_for_status()
            results = parse_openalex_response(resp.json())
            return {
                "status": "CONNECTED",
                "provider": "openalex",
                "query": q,
                "count": len(results),
                "results": results,
                "api_docs": "https://help.openalex.org/api/",
            }

        if prov == "arxiv":
            elapsed = time.monotonic() - _last_arxiv_call
            if _last_arxiv_call > 0 and elapsed < 3.0:
                time.sleep(3.0 - elapsed)
            params = {
                "search_query": f"all:{q}",
                "start": 0,
                "max_results": limit,
            }
            resp = httpx.get(ARXIV_API_URL, params=params, headers=headers, timeout=timeout_s)
            _last_arxiv_call = time.monotonic()
            resp.raise_for_status()
            results = parse_arxiv_atom_xml(resp.text)
            return {
                "status": "CONNECTED",
                "provider": "arxiv",
                "query": q,
                "count": len(results),
                "results": results,
                "api_docs": "https://info.arxiv.org/help/api/user-manual.html",
            }

        if prov == "pubchem":
            elapsed = time.monotonic() - _last_pubchem_call
            if _last_pubchem_call > 0 and elapsed < 0.21:
                time.sleep(0.21 - elapsed)
            encoded = urllib.parse.quote(q, safe="")
            url = f"{PUBCHEM_BASE_URL}/{encoded}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,IUPACName/JSON"
            resp = httpx.get(url, headers=headers, timeout=timeout_s)
            _last_pubchem_call = time.monotonic()
            resp.raise_for_status()
            results = parse_pubchem_response(resp.json(), q)
            return {
                "status": "CONNECTED",
                "provider": "pubchem",
                "query": q,
                "count": len(results),
                "results": results,
                "api_docs": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6030920/",
            }

        raise ValueError(f"Unsupported provider '{provider}'. Supported: openalex, arxiv, pubchem.")

    except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError, OSError) as exc:
        return {
            "status": "NOT_CONNECTED",
            "provider": prov,
            "query": q,
            "count": 0,
            "results": [],
            "blocker": f"External network unavailable for {prov}: {type(exc).__name__}. No fake results were generated.",
        }
    except httpx.HTTPStatusError as exc:
        return {
            "status": "UPSTREAM_ERROR",
            "provider": prov,
            "query": q,
            "count": 0,
            "results": [],
            "blocker": f"Upstream {prov} API returned HTTP {exc.response.status_code}.",
        }
