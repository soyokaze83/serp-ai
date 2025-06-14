import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import (
    homogenize_latex_encoding,
    convert_to_unicode,
    type as bibtex_type,
)
import json
from argparse import ArgumentParser
from typing import List, Dict, Any, Optional
from tqdm.auto import tqdm


class Parser:
    """
    Parses BibTeX files into a list of JSON-ready dictionaries
    suitable for Elasticsearch ingestion.
    """

    def __init__(self):
        """Initializes the BibtexParser."""
        self._parser = BibTexParser(common_strings=True)
        self._parser.customization = self._customizations
        self._parser.ignore_nonstandard_types = False
        self._parser.homogenize_fields = True  # Tries to make field names consistent (e.g. "journaltitle" to "journal")

    @staticmethod
    def _customizations(record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies standard customizations to a BibTeX record.
        - Converts month abbreviations to full names.
        - Homogenizes LaTeX encodings.
        - Converts LaTeX characters to Unicode.
        """
        record = bibtex_type(record)
        record = homogenize_latex_encoding(record)
        record = convert_to_unicode(record)
        return record

    def _transform_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms a single parsed BibTeX entry into a desired JSON structure.
        """
        # Make all keys lowercase for consistency in Elasticsearch
        entry_lower = {k.lower(): v for k, v in entry.items()}

        # Concatenate title and abstract
        title = entry_lower.get("title")
        abstract = entry_lower.get("abstract")
        if title and abstract:
            text = title + " " + abstract
            text = text.strip()
        else:
            text = title if title else abstract

        doc_source = {
            "citekey": entry_lower.get("id"),  # 'ID' becomes 'id' after lowercasing
            "entry_type": entry_lower.get("entrytype"),
            "title": title,  # Re-insert title for display
            "abstract": abstract,  # Re-insert abstract for display
            "text": text,  # Concatenated text
            "booktitle": entry_lower.get("booktitle"),
            "journal": entry_lower.get("journal"),
            "year": entry_lower.get("year"),
            "month": entry_lower.get("month"),
            "volume": entry_lower.get("volume"),
            "number": entry_lower.get("number"),  # issue number
            "pages": entry_lower.get("pages"),
            "address": entry_lower.get("address"),
            "publisher": entry_lower.get("publisher"),
            "url": entry_lower.get("url"),
            "doi": entry_lower.get("doi"),
            "keywords": entry_lower.get("keywords"),  # Often a comma-separated string
        }

        # Process authors (list of strings)
        if "author" in entry_lower:
            authors_str = entry_lower["author"].replace("\n", " ").strip()
            doc_source["authors"] = [
                name.strip() for name in authors_str.split(" and ") if name.strip()
            ]
        else:
            doc_source["authors"] = []

        # Process editors (list of strings)
        if "editor" in entry_lower:
            editors_str = entry_lower["editor"].replace("\n", " ").strip()
            doc_source["editors"] = [
                name.strip() for name in editors_str.split(" and ") if name.strip()
            ]
        else:
            doc_source["editors"] = []

        # Convert year to integer if possible
        if "year" in doc_source and isinstance(doc_source["year"], str):
            try:
                doc_source["year"] = int(doc_source["year"])
            except ValueError:
                print(
                    f"Warning: Could not convert year '{doc_source['year']}' to int for entry {doc_source.get('citekey')}"
                )
                # Keep as string, or handle as error by removing or setting to None

        # Split keywords string into a list
        if "keywords" in doc_source and isinstance(doc_source["keywords"], str):
            doc_source["keywords"] = [
                kw.strip() for kw in doc_source["keywords"].split(",") if kw.strip()
            ]
        elif "keywords" not in doc_source:  # Ensure keywords field exists
            doc_source["keywords"] = []

        # Remove fields with None values to keep documents clean
        return {k: v for k, v in doc_source.items() if v is not None}

    def parse_file(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Parses a BibTeX file and returns a list of dictionaries.

        Args:
            filepath: Path to the BibTeX file.

        Returns:
            A list of dictionaries, where each dictionary represents a BibTeX entry.
            Returns an empty list if the file is not found or parsing fails.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as bibtex_file:
                bibtex_string = bibtex_file.read()
        except FileNotFoundError:
            print(f"Error: BibTeX file not found at {filepath}")
            return []
        except Exception as e:
            print(f"Error reading BibTeX file {filepath}: {e}")
            return []

        try:
            print(f"Parsing BibTeX content from {filepath}...")
            bib_database = bibtexparser.loads(bibtex_string, parser=self._parser)
            print(f"Parsed {len(bib_database.entries)} entries.")
        except Exception as e:
            print(f"Error parsing BibTeX content from {filepath}: {e}")
            return []

        elasticsearch_docs = []
        for entry in tqdm(bib_database.entries, desc="Transforming BibTeX entries"):
            transformed_entry = self._transform_entry(entry)
            if transformed_entry.get("citekey"):
                elasticsearch_docs.append(transformed_entry)
            else:
                print(f"Warning: Skipping entry without a citekey")

        return elasticsearch_docs

    def generate_ndjson_for_bulk_api(
        self,
        documents: List[Dict[str, Any]],
        index_name: str,
        output_filepath: Optional[str] = None,
    ) -> List[str]:
        """
        Generates NDJSON lines for Elasticsearch bulk ingestion.

        Args:
            documents: A list of parsed document dictionaries.
            index_name: The name of the Elasticsearch index.
            output_filepath: Optional path to write the NDJSON data to.

        Returns:
            A list of strings, where each pair of strings represents an action and a document.
        """
        ndjson_lines = []
        for doc_source in tqdm(documents, desc="Generating NDJSON lines"):
            action = {"index": {"_index": index_name}}
            # Use citekey as the document ID if it's unique and suitable
            if "citekey" in doc_source and doc_source["citekey"]:
                action["index"]["_id"] = doc_source["citekey"]

            ndjson_lines.append(json.dumps(action))
            ndjson_lines.append(json.dumps(doc_source))

        if output_filepath:
            try:
                with open(output_filepath, "w", encoding="utf-8") as f:
                    for line in tqdm(
                        ndjson_lines, desc=f"Writing to {output_filepath}"
                    ):
                        f.write(line + "\n")
                print(f"NDJSON data successfully written to: {output_filepath}")
            except IOError as e:
                print(f"Error writing NDJSON to file {output_filepath}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while writing NDJSON to file: {e}")

        return ndjson_lines


if __name__ == "__main__":

    argparse = ArgumentParser()
    argparse.add_argument(
        "--bib_path", required=True, help="Path to the input BibTeX file."
    )
    argparse.add_argument("--output_path", help="Path to the output NDJSON file.")
    args = argparse.parse_args()

    bib_parser = Parser()
    parsed_docs = bib_parser.parse_file(args.bib_path)

    if parsed_docs:
        bib_parser.generate_ndjson_for_bulk_api(
            parsed_docs, index_name="serp-ai", output_filepath=args.output_path
        )
    else:
        print("No documents parsed. Exiting.")
