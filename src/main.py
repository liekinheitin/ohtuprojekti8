
from storage import load_references, save_references
from validation import validate_reference
from keys import generate_key
from export import export_bibtex

DEFAULT_FILE = "references.json"
EDIT_FIELDS = [
    ("author", "Tekijä"),
    ("title", "Otsikko"),
    ("year", "Vuosi"),
]


class ConsoleIO:
    def read(self, prompt=""):
        return input(prompt)

    def write(self, value):
        print(value)


class App:
    def __init__(self, io, file_path=DEFAULT_FILE):
        self.io = io
        self.file_path = file_path
        self.references = load_references(file_path)

    def run(self):
        while True:
            command = self.io.read("Komento (lisaa, listaa, muokkaa, poista tai lopeta): ")

            if command == "lisaa":
                self.add_reference()
            elif command == "listaa":
                self.list_references()
            elif command == "muokkaa":
                self.edit_reference()
            elif command == "poista":
                self.remove_reference()
            elif command == "bibtex":
                export_bibtex(self.references, "references.bib")
            elif command == "lopeta":
                break
            else:
                self.io.write("Tuntematon komento")

    def add_reference(self):
        reference = {
            "type": self.io.read("Viitteen tyyppi (book, article, inproceedings): "),
            "author": parse_authors(self.io.read("Tekijät: ")),
            "title": self.io.read("Otsikko: "),
            "year": self.io.read("Julkaisuvuosi: "),
        }

        errors = validate_reference(reference)

        if errors:
            for error in errors:
                self.io.write(error)

            self.io.write("Viitettä ei tallennettu")
            return

        existing_keys = [ref.get("key", "") for ref in self.references]
        reference["key"] = generate_key(
            reference["author"], reference["year"], existing_keys
        )

        self.references.append(reference)
        save_references(self.references, self.file_path)
        self.io.write(f"Viite lisätty, viiteavain: {reference['key']}")

    def list_references(self):

        if not self.references:
            self.io.write("Ei tallennettuja viitteitä.")
            return

        for reference in sorted(self.references, key=sort_key):
            self.io.write(format_reference(reference))

    def remove_reference(self):
        if not self.references:
            self.io.write("Ei poistettavia viitteitä.")
            return

        key = self.io.read("Anna poistettavan viitteen avain: ")

        reference = next(
            (ref for ref in self.references if ref.get("key") == key),
            None
        )

        if reference is None:
            self.io.write("Viitettä ei löytynyt.")
            return

        self.io.write("Olet poistamassa seuraavaa viitettä:")
        self.io.write(format_reference(reference))

        confirmation = self.io.read(
            "Haluatko varmasti poistaa viitteen? (kyllä/ei): "
        ).lower()

        if confirmation == "kyllä":
            self.references.remove(reference)
            save_references(self.references, self.file_path)
            self.io.write("Viite poistettu.")
        else:
            self.io.write("Viitettä ei poistettu.")

    def find_reference(self, key):
        for reference in self.references:
            if reference.get("key", "").lower() == key.lower():
                return reference
        return None

    def ask_edits(self, reference):
        """Kysyy kentät nykyiset arvot hakasulkeissa.
        Palauttaa vain ne kentät, joihin käyttäjä kirjoitti uuden arvon."""
        changes = {}

        for field, label in EDIT_FIELDS:
            if field == "author":
                current = author_text(reference)
            else:
                current = reference[field]

            value = self.io.read(f"{label} [{current}]: ").strip()

            if value:
                changes[field] = value

        return changes

    def edit_reference(self):
        key = self.io.read("Muokattavan viitteen viiteavain: ").strip()
        reference = self.find_reference(key)

        if reference is None:
            self.io.write(f"Viitettä avaimella {key} ei löytynyt")
            return

        self.io.write(f"Muokataan viitettä {reference['key']}")
        self.io.write("")

        changes = self.ask_edits(reference)
        self.apply_edits(reference, changes)

    def apply_edits(self, reference, changes):
        """Validoi, päivittää ja tallentaa viitteen muokkaukset."""
        
        if not changes:
            self.io.write("Mitään muutoksia ei tehty.")
            return

        updated_reference = reference.copy()

        for field, value in changes.items():
            if field == "author":
                updated_reference[field] = parse_authors(value)
            else:
                updated_reference[field] = value.strip()

        errors = validate_reference(updated_reference)

        if errors:
            for error in errors:
                self.io.write(error)

            self.io.write("Muutoksia ei tallennettu.")
            return

        reference.update(updated_reference)

        save_references(self.references, self.file_path)

        self.io.write("Viite päivitetty onnistuneesti.")

def parse_authors(text):
    return [author.strip() for author in text.split(";") if author.strip()]

def author_text(reference):
    """Palauttaa tekijät yhtenä merkkijonona (lista tai merkkijono)."""
    authors = reference["author"]
    if isinstance(authors, list):
        return "; ".join(authors)
    return authors


def sort_key(reference):
    """Järjestää tekijän ja sitten otsikon mukaan kirjainkoosta riippumatta."""
    return (author_text(reference).casefold(), reference["title"].casefold())

def format_reference(reference):
    """Muodostaa viitteestä yhden rivin esityksen."""

    authors = author_text(reference)

    key = reference.get("key", "-")
    return (
        f"[{key}] "
        f"{authors} "
        f"({reference['year']}): "
        f"{reference['title']} "
        f"[{reference['type']}]"
    )

def main():
    App(ConsoleIO()).run()


if __name__ == "__main__":
    main()

