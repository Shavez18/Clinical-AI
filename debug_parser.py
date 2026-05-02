import spacy
nlp = spacy.load("en_core_web_sm")

text = "The patient denies having shortness of breath, but confirms sweating."
doc = nlp(text)

print(f"{'Text':<15} | {'Dep':<10} | {'Head':<15} | {'Ancestors'}")
print("-" * 60)
for token in doc:
    ancestors = [a.text for a in token.ancestors]
    print(f"{token.text:<15} | {token.dep_:<10} | {token.head.text:<15} | {ancestors}")
