import os
import csv
import re

import spacy
import stanza


def txt_file_load(file_path: str) -> list:
    with open(file_path, encoding="UTF-8") as f:
        contents = f.read()
    return contents


def load_language_model():
    while True:
        lang_select = input(
            'Please enter either "cs", "en" or "de" for processing in the respective language: '
        ).lower()
        if lang_select == "en":
            return spacy.load("en_core_web_sm"), lang_select
        elif lang_select == "de":
            return spacy.load("de_core_news_sm"), lang_select
        elif lang_select == "cs":
            return stanza.Pipeline("cs"), lang_select
        else:
            print(
                'Program requires input of either "cs", "en" or "de" on launch to select either Czech, English or German version respectively. Please try again with a valid argument.'
            )


def process_document(nlp, lang_choice: str):
    if lang_choice != "cs":
        return nlp(txt_file_load(os.path.join("patent.txt")))
    else:
        text = txt_file_load(os.path.join("patent.txt"))
        cleaned_text = re.sub(r"[()]", "", text)
        return nlp(cleaned_text)


def blacklist_load(file_path: str) -> list:
    with open(file_path, encoding="UTF-8") as f:
        contents = f.read()
    return contents.split()


def add_ref_mark_en_de(doc, token, numbers):
    """According to set linguistic parameters for English and German inside the if condition of the while loop, the function return either a single reference mark when the if conditions are not met or a compound reference mark when they are. When checking for compounds the function check backwards from the number string until conditions are no longer met."""
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
        if numbers:
            return f"{token.text.strip('.')} {' '.join(compund_ref_mark)} {single_ref_mark}"
        else:
            return f"{' '.join(compund_ref_mark)} {single_ref_mark}"
    else:
        if numbers:
            return f"{token.text.strip('.')} {single_ref_mark.lemma_}"
        else:
            return single_ref_mark.lemma_


def add_ref_mark_cs(i, words, numbers):
    """According to set linguistic parameters for Czech inside the if condition of the while loop, the function return either a single reference mark when the if conditions are not met or a compound reference mark when they are. When checking for compounds the function check backwards from the number string until conditions are no longer met."""
    single_ref_mark = words[i - 1]
    compund_ref_mark = list()
    count = 2
    while True:
        if words[i - count].pos == "ADJ" and words[i - count].deprel == "amod":
            compund_ref_mark.append(words[i - count].text)
            count += 1
        else:
            break
    if len(compund_ref_mark) != 0:
        compund_ref_mark.reverse()
        if numbers:
            return f"{words[i].text} {' '.join(compund_ref_mark).lower()} {single_ref_mark.text.lower()}"
        else:
            return (
                f"{' '.join(compund_ref_mark).lower()} {single_ref_mark.text.lower()}"
            )
    else:
        if numbers:
            return f"{words[i].text} {single_ref_mark.lemma.lower()}"
        else:
            return single_ref_mark.lemma.lower()


def extraction_en_de(doc, blacklist: list, mode="b", numbers=False):
    """According to the mode selected by the user, the function applies either broad conditions to the extraction of the reference marks from English or German or precise conditions. Precise mode adds reference mark numbers to the blacklist and ignores them if it encounters them again. Broad mode checks repeated reference mark numbers and adds them to the reference marks list."""
    ref_marks = list()
    if mode == "b":
        for token in doc:
            if (
                (token.pos_ == "NUM" or token.like_num)
                and not token.is_alpha
                and doc[token.i - 1].lemma_ not in blacklist
                and doc[token.i - 1].pos_ == "NOUN"
                and len(doc[token.i - 1]) > 1
            ):
                ref_marks.append(add_ref_mark_en_de(doc, token, numbers))
    elif mode == "p":
        for token in doc:
            if (
                token.pos_ == "NUM"
                and not token.is_alpha
                and token.text not in blacklist
                and doc[token.i - 1].lemma_ not in blacklist
                and doc[token.i - 1].pos_ == "NOUN"
                and len(doc[token.i - 1]) > 1
            ):
                ref_marks.append(add_ref_mark_en_de(doc, token, numbers))
                blacklist.append(token.text)
    return set(ref_marks)


def extraction_cs(doc, blacklist: list, mode="b", numbers=False):
    """According to the mode selected by the user, the function applies either broad conditions to the extraction of the reference marks from Czech or precise conditions. Precise mode adds reference mark numbers to the blacklist and ignores them if it encounters them again. Broad mode checks repeated reference mark numbers and adds them to the reference marks list."""
    ref_marks = list()
    if mode == "b":
        for sentence in doc.sentences:
            words = sentence.words
            for i in range(0, len(words)):
                if (
                    words[i].pos == "NUM"
                    and not words[i].text.isalpha()
                    and words[i - 1].lemma not in blacklist
                    and words[i - 1].pos in ["NOUN", "ADV"]
                    and len(words[i - 1].text) > 1
                ):
                    ref_marks.append(add_ref_mark_cs(i, words, numbers))
    elif mode == "p":
        for sentence in doc.sentences:
            words = sentence.words
            for i in range(0, len(words)):
                if (
                    words[i].pos == "NUM"
                    and words[i].text not in blacklist
                    and not words[i].text.isalpha()
                    and words[i - 1].lemma not in blacklist
                    and words[i - 1].pos in ["NOUN", "ADV"]
                    and len(words[i - 1].text) > 1
                ):
                    ref_marks.append(add_ref_mark_cs(i, words, numbers))
                    blacklist.append(words[i].text)
    return set(ref_marks)


def ref_marks_extractor(doc, lang_choice: str):
    while True:
        mode = input(
            "Please choose either Broad or Precision mode. Broad mode returns more hits that can be almost identical but is less likely to miss anything, and Precision mode returns only unique hits for each reference mark number, so it returns less identical results but is more likely to return a false positive and miss a reference mark. Write 'b' for Broad mode or 'p' for Precision mode: "
        ).lower()
        numbers = False
        while True:
            choice = input(
                "Do you want to display reference mark numbers in the CSV file? y/n: "
            ).lower()
            if choice == "y":
                numbers = True
                break
            elif choice == "n":
                break
            else:
                print('Please write either "y" or "n".')
        black_list = blacklist_load(os.path.join("blacklist.txt"))
        if lang_choice != "cs":
            return list(extraction_en_de(doc, black_list, mode, numbers)), mode
        elif lang_choice == "cs":
            return list(extraction_cs(doc, black_list, mode, numbers)), mode
        else:
            print("*" * 80)
            print("Please provide a valid input.")
            print("*" * 80)


def ref_marks_csv_exporter(ref_marks: list, lang_choice: str, mode: str):
    with open(
        f"Vztah_znacky_{mode}.csv", mode="w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.writer(file, delimiter=";", dialect="excel")
        if lang_choice != "cs":
            writer.writerow([lang_choice, "cs"])
            for item in ref_marks:
                writer.writerow([item, "."])
        else:
            writer.writerow([lang_choice, "Doplň jazyk"])
            for item in ref_marks:
                writer.writerow([item, "."])


def main():
    nlp, lang_choice = load_language_model()
    doc = process_document(nlp, lang_choice)
    ref_marks, mode = ref_marks_extractor(doc, lang_choice)
    ref_marks.sort()
    ref_marks_csv_exporter(ref_marks, lang_choice, mode)


if __name__ == "__main__":
    main()
