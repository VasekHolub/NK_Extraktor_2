#! venv/Scripts/python
import spacy
import csv
import os


def txt_file_load(file_path: str) -> list:
    with open(file_path, encoding="UTF-8") as f:
        contents = f.read()
    return contents


def load_language_model():
    while True:
        lang_select = input(
            'Please enter either "en" or "de" for processing in the respective language: '
        ).lower()
        if lang_select == "en":
            return spacy.load("en_core_web_trf")
        elif lang_select == "de":
            return spacy.load("de_dep_news_trf")
        else:
            print(
                'Program requires input of either "en" or "de" on launch to select the English or German version respectively. Please try again with a valid argument.'
            )


def process_document(nlp):
    return nlp(txt_file_load(os.path.join("patent.txt")))


def exclusion_list_load(file_path: str) -> list:
    with open(file_path, encoding="UTF-8") as f:
        contents = f.read()
    return contents.split()


def ref_marks_extractor(doc):
    ref_marks = []
    for token in doc:
        if (
            token.pos_ == "NUM"
            and not token.is_alpha
            and doc[token.i - 1].lemma_
            not in exclusion_list_load(os.path.join("black_list.txt"))
            and doc[token.i - 1].pos_ == "NOUN"
        ):
            single_ref_mark = doc[token.i - 1]
            compund_ref_mark = list()
            count = 2
            while True:
                if (
                    doc[token.i - count].pos_ == "ADJ"
                    or doc[token.i - count].dep_ == "amod"
                    or (
                        doc[token.i - count].pos_ == "NOUN"
                        and doc[token.i - count].dep_ == "compound"
                    )
                ):
                    compund_ref_mark.append(doc[token.i - count].text)
                    count += 1
                else:
                    break
            if len(compund_ref_mark) != 0:
                compund_ref_mark.reverse()
                ref_marks.append(f"{' '.join(compund_ref_mark)} {single_ref_mark}")
            else:
                ref_marks.append(single_ref_mark.lemma_)
    return set(ref_marks)


def ref_marks_csv_exporter(ref_marks: list):
    with open("Vztah_znacky.csv", mode="w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file, delimiter=";", dialect="excel")
        writer.writerow(["en", "cs"])
        for item in ref_marks:
            writer.writerow([item, "."])


def main():
    nlp = load_language_model()
    doc = process_document(nlp)
    ref_marks = list(ref_marks_extractor(doc))
    ref_marks.sort()
    ref_marks_csv_exporter(ref_marks)


if __name__ == "__main__":
    main()
