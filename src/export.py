from pathlib import Path

# muuttaa references.json-tiedoston viitteet bibtex-muotoon
# ja kirjoittaa ne tiedostoon references.bib

# references bibtex-muotoon
def to_bibtex(reference):
    authors = " and ".join(reference["author"])

    return (
        f"@{reference['type']}{{{reference['key']},\n"
        f"  author = {{{authors}}},\n"
        f"  title = {{{reference['title']}}},\n"
        f"  year = {{{reference['year']}}}\n"
        f"}}"
    )

# luo bib-tiedoston ja kirjoittaa sinne
def export_bibtex(references, file_path):
        file_path = "references.bib"

        with open(file_path, "w", encoding="utf-8") as file:
            for reference in references:
                 bibtex = to_bibtex(reference)
                 file.write(bibtex+"\n\n")