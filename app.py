#!/usr/bin/env python3

import time
import requests
import xml.etree.ElementTree as ET
import gradio as gr
import json
import re

BASE_URL = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"

# Validate & clean sequence input
def clean_sequence(seq: str) -> str:
    """Clean and validate a single DNA sequence in FASTA or raw format."""

    lines = seq.strip().splitlines()
    if not lines:
        raise ValueError("Input is empty")

    # Count FASTA headers
    header_lines = [line for line in lines if line.startswith(">")]
    if len(header_lines) > 1:
        raise ValueError("Multiple sequences detected. Please submit only one sequence at a time.")

    # Remove all FASTA headers
    sequence_lines = [line.strip() for line in lines if not line.startswith(">")]
    cleaned_seq = ''.join(sequence_lines).replace(" ", "").upper()

    if not cleaned_seq:
        raise ValueError("No sequence data found")

    # IUPAC DNA codes (including ambiguous bases)
    valid_iupac_dna = set("ACGTRYKMSWBDHVN")
    if not set(cleaned_seq).issubset(valid_iupac_dna):
        invalid_chars = set(cleaned_seq) - valid_iupac_dna
        raise ValueError(f"Invalid characters in sequence: {', '.join(invalid_chars)}")

    return cleaned_seq

# Submit to NCBI BLAST
def submit_blast(sequence: str) -> str:
    response = requests.post(BASE_URL, data={
        "CMD": "Put",
        "PROGRAM": "blastn",
        "DATABASE": "nt",
        "QUERY": sequence,
        "FORMAT_TYPE": "XML",
        "HITLIST_SIZE": 10
    })
    response.raise_for_status()
    for line in response.text.splitlines():
        if "RID =" in line:
            return line.split("=", 1)[1].strip()
    raise RuntimeError("RID not found in BLAST response")

# Wait until results are ready
def wait_for_result(rid: str, timeout: int = 180):
    for _ in range(timeout // 5):
        status = requests.get(BASE_URL, params={
            "CMD": "Get",
            "RID": rid,
            "FORMAT_OBJECT": "SearchInfo"
        }).text
        if "Status=READY" in status:
            return
        elif "Status=FAILED" in status or "Status=UNKNOWN" in status:
            raise RuntimeError("BLAST search failed or unknown")
        time.sleep(5)
    raise TimeoutError("BLAST timed out")

# Fetch result XML
def fetch_result(rid: str) -> str:
    result = requests.get(BASE_URL, params={
        "CMD": "Get",
        "RID": rid,
        "FORMAT_TYPE": "XML"
    })
    result.raise_for_status()
    return result.text

# Parse XML
def parse_top_hits(xml_text: str) -> dict:
    root = ET.fromstring(xml_text)
    query_len = int(root.findtext(".//BlastOutput_query-len", "0"))
    hits = root.findall(".//Hit")[:10]

    results = []
    for hit in hits:
        hsp = hit.find(".//Hsp")
        if hsp is None:
            continue
        identity = int(hsp.findtext("Hsp_identity", "0"))
        align_len = int(hsp.findtext("Hsp_align-len", "1"))
        
        # Extract organism_gene from Hit_def
        organism_gene = hit.findtext("Hit_def", "")
        
        # Remove 'PREDICTED: ' if present at the start of description
        if organism_gene.startswith("PREDICTED: "):
            organism_gene = organism_gene[len("PREDICTED: "):].strip()
        organism_gene = organism_gene.split(",")[0].strip()

        # Append results
        results.append({
            "accession": hit.findtext("Hit_accession", ""),
            "length": int(hit.findtext("Hit_len", "0")),
            "evalue": float(hsp.findtext("Hsp_evalue", "1")),
            "identity_percent": round(identity / align_len * 100, 2),
            "description": organism_gene
        })

    return {
        "query_len": query_len,
        "top_hits": results
    }

# Complete pipeline
def blast_lookup(seq: str) -> dict:
    try:
        sequence = clean_sequence(seq)
        if len(sequence) > 3000:
            return {"error": "Sequence too long (max 3000 bp)"}
        rid = submit_blast(sequence)
        wait_for_result(rid)
        xml = fetch_result(rid)
        return parse_top_hits(xml)
    except Exception as e:
        return {"error": str(e)}
        

# Gradio interface
def blast_for_mcp(seq):
    result = blast_lookup(seq)
    return result

demo = gr.Interface(
    fn=blast_for_mcp,
    inputs=gr.Textbox(label="Enter DNA sequence", placeholder="E.g.: >sequence 1\nAGTCTGNYGW"),
    outputs=gr.JSON(label="Top 10 BLAST Hits JSON Output"),
    title="NCBI BLAST DNA Search Tool",
    description="Enter a DNA sequence to get structured BLAST results, or use programmatically for MCP access."
)

# Launch the interface and MCP server
if __name__ == "__main__":
    demo.launch(mcp_server=True)