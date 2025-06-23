# NCBI BLAST MCP Server

MCP Server and Gradio web application that performs DNA sequence similarity searches using NCBI's BLAST service. It allows the user to input a DNA sequence and get back the top ten sequence matches from the NCBI database, enabling identification of the organism and gene.

This app functions as a **Model Context Protocol (MCP) Server** for integration with AI assistants. 

    Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to LLMs. MCP enables models to interact with the world. Learn more at modelcontextprotocol.io.

Created for the HuggingFace **Gradio Agents & MCP Hackathon 2025** for the mcp-server-track. 
    *Track 1: Extend the capabilities of your favorite LLM by building a Gradio app to accomplish any specific task.*

Code/Demo on HuggingFaceSpaces: [Agents-MCP-Hackathon/ncbi-blast-mcp-server](https://huggingface.co/spaces/Agents-MCP-Hackathon/ncbi-blast-mcp-server)

Demo video with Cursor Desktop: "https://youtu.be/yCpaTvcDeqM"


## Features
- MCP Server for AI assistant integration
- Web interface and programmatic API access
- DNA sequence similarity search using NCBI BLAST
- Submit DNA sequences in FASTA or raw format
- Automatic sequence validation and cleaning
- Returns top 10 hits/matches in JSON format


## Quick Start in Cursor IDE
Clone or download this repository, then run in Cursor terminal:
```
pip install -r requirements.txt
python app.py
```
Open the provided local URL (http://localhost:7860) to access the web interface.

## Web UI Usage

**Input**: Paste your DNA sequence in FASTA format or as raw nucleotides
```
>My sequence
AGTCTGNYRGWACGT
```
or just:
```
AGTCTGNYRGWACGT
```

**Output**: View generated JSON output of top sequence matches


## Programmatic Usage

Query the running server programmatically with Python:

```python
pip install gradio_client
from gradio_client import Client

client = Client("<spacename>/ncbi-blast-mcp-server")
result = client.predict(
		seq="ATGGACACCTACTCCTCTGGAGAAGATTTAGTTATTAAGACACGAAAACCGTATACAATTACCAAGCAACGGGAACGATGGACAGAGGAGGAGCATAA
            TAGGTTTCTAGAAGCCTTAAAACTCTATGGGCGAGCGTGGCAACGTATCGAAGAACATATAGGAACCAAGACTGCTGTGCAGATCAGAAGTCATGCACA
            GAAATTCTTTACAAAGTTGGAGAAGGAAGCTCTTGTGAAAGGAGTTCCAATAAGACAAGCTATTGACATAGAGATTCCTCCTCCGCGCCCTAAAAGGAA
            ACCAAGCAATCCTTATCCTCGAAAGACTGGTGTGGCAACACCTAGTCTGCAGGTGGGAGCAAAGGATGGGAATAATTCATCATCAGTTTCTTCTTCCTG
            CACTGCCACTGGTAAACAAATACTGGACTTGGAAAGAGAACCACTACCTGAGAAACCTGATGGAGATGAAAAGCAAGAAAATGCCAAAGAAAACCAGGA
            TGAGGGAAATTTCTCTGAAGTTTTAACCCTTTTCCAAGAAGCTCCGTGTACGTCCTTGTCTTCAGTGGACAAAGATTCCATTCGAACACTGGCGGCACC",
		api_name="/blast_ui"
)
```
View the top result:

```python
import json

blast_data = json.loads(result[1])

if "error" not in blast_data:
    top_hit = blast_data["top_hits"][0]
    print(f"Organism: {top_hit['description']}")
    print(f"Identity: {top_hit['identity_percent']}%")
```

## Input Requirements
- Single sequence only (no multiple FASTA entries)
- DNA sequence as input
- Maximum length: 3,000 base pairs
- Supports IUPAC DNA codes including ambiguous bases
- Automatically removes headers and whitespace


## Notes
- Uses NCBI's public BLAST service
- Results typically available within 30-180 seconds
- Respects NCBI usage guidelines
- Removes "PREDICTED:" prefixes from descriptions

## Future Work
- Enable multi-sequence inputs
- Enable RNA and DNA search functionality
