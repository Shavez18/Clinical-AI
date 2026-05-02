import spacy
from spacy.matcher import Matcher
from src.symptom_engine.disease_rules import SYMPTOM_WEIGHTS, MASTER_SYMPTOMS_LIST

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: en_core_web_sm not found. Run: python -m spacy download en_core_web_sm")
    nlp = spacy.blank("en")

class ClinicalParser:
    def __init__(self):
        self.nlp = nlp
        self.matcher = Matcher(self.nlp.vocab)
        self._setup_patterns()

        # Synonym Normalization
        self.synonyms = {
            "breathlessness": "shortness of breath",
            "chest tightness": "chest pain",
            "heart hurts": "chest pain",
            "head ache": "headache",
            "migraine": "headache",
            "tummy ache": "stomach pain",
            "belly ache": "stomach pain",
            "belly": "stomach",
            "throwing up": "vomiting",
            "puking": "vomiting",
            "sweat": "sweating",
            "perspiration": "sweating",
            "high temp": "fever",
            "temperature": "fever",
            "tired": "fatigue",
            "tiredness": "fatigue",
            "exhausted": "fatigue",
            "dizzy": "dizziness",
            "spinning": "dizziness",
            "lightheaded": "dizziness"
        }

        self.weights = SYMPTOM_WEIGHTS
        self.neg_words = {"no", "not", "without", "denies", "deny", "never", "zero", "lacks", "none", "negative", "absent"}
        self.pos_words = {"confirm", "confirms", "confirmed", "presents", "has", "shows", "demonstrates", "positive", "presence"}

    def _setup_patterns(self):
        self.matcher.add("SEVERE", [[{"LOWER": {"IN": ["severe", "extreme", "unbearable", "high", "intense", "terrible", "worst"]}}]])
        self.matcher.add("MILD", [[{"LOWER": {"IN": ["mild", "slight", "low", "minor", "little"]}}]])

    def _normalize(self, text: str):
        lower_text = text.lower()
        for k, v in self.synonyms.items():
            lower_text = lower_text.replace(k, v)
        return lower_text

    def _is_token_negated(self, token):
        """Standard + Coordination-aware negation detection."""
        for child in token.children:
            if child.dep_ == "neg" or child.text.lower() in self.neg_words:
                return True
        if token.dep_ == "conj":
            if self._is_token_negated(token.head):
                return True
        for ancestor in token.ancestors:
            low_anc = ancestor.lemma_.lower()
            if low_anc in self.pos_words:
                return False
            if low_anc in ["deny", "lack", "negative", "exclude", "absent"]:
                return True
            for child in ancestor.children:
                if child.dep_ == "neg" or child.text.lower() in self.neg_words:
                    return True
        return False

    def _is_phrase_negated(self, doc, phrase: str):
        """Multi-word phrase negation using constituent logic."""
        phrase_tokens = []
        full_text = doc.text.lower()
        start_char = full_text.find(phrase)
        if start_char == -1: return False
        
        end_char = start_char + len(phrase)
        for t in doc:
            if t.idx >= start_char and (t.idx + len(t.text)) <= end_char:
                phrase_tokens.append(t)
        
        if not phrase_tokens:
            return any(neg in full_text[:start_char].split()[-3:] for neg in self.neg_words)

        for t in phrase_tokens:
            if t.pos_ in ["NOUN", "ADJ", "VERB"] and self._is_token_negated(t):
                return True
        return False

    def parse(self, text: str):
        text = self._normalize(text)
        doc = self.nlp(text)
        extracted_symptoms = []
        negated_symptoms = []
        duration = None
        severity = "Moderate"
        
        matches = self.matcher(doc)
        for m_id, start, end in matches:
            if self.nlp.vocab.strings[m_id] == "SEVERE": severity = "High"
            elif self.nlp.vocab.strings[m_id] == "MILD": severity = "Low"

        raw_text = text.lower()
        for c in sorted(MASTER_SYMPTOMS_LIST, key=len, reverse=True):
            if " " in c and c in raw_text:
                if self._is_phrase_negated(doc, c):
                    if c not in negated_symptoms: negated_symptoms.append(c)
                else:
                    if c not in extracted_symptoms: extracted_symptoms.append(c)

        for token in doc:
            if token.pos_ in ["NOUN", "ADJ", "VERB"] and not token.is_stop and len(token.text) > 2:
                word = token.lemma_.lower()
                text_word = token.text.lower()
                symp_hit = None
                if word in MASTER_SYMPTOMS_LIST: symp_hit = word
                elif text_word in MASTER_SYMPTOMS_LIST: symp_hit = text_word
                if symp_hit:
                    if any(symp_hit in c for c in extracted_symptoms if " " in c): continue
                    if any(symp_hit in c for c in negated_symptoms if " " in c): continue
                    if self._is_token_negated(token):
                        if symp_hit not in negated_symptoms: negated_symptoms.append(symp_hit)
                    else:
                        if symp_hit not in extracted_symptoms: extracted_symptoms.append(symp_hit)

        final_extracted = [s for s in set(extracted_symptoms) if s not in negated_symptoms]
        weights_dict = {s: self.weights.get(s, 3) for s in final_extracted}
        for s in weights_dict:
            if severity == "High": weights_dict[s] = min(10, weights_dict[s] + 2)
            elif severity == "Low": weights_dict[s] = max(1, weights_dict[s] - 1)
        max_weight = max(weights_dict.values()) if weights_dict else 0

        context_features = []
        for ent in doc.ents:
            if ent.label_ in ["DATE", "TIME"]:
                duration = ent.text
                context_features.append(f"duration: {duration}")

        if any(tk in raw_text for tk in ["travel", "trip", "visited", "africa", "asia", "india", "abroad", "tropical"]):
            context_features.append("travel_history: true")

        return {
            "clean_text": " ".join(final_extracted),
            "raw_symptoms_list": final_extracted,
            "negated_symptoms": list(set(negated_symptoms)),
            "symptom_weights": weights_dict,
            "max_symptom_weight": max_weight,
            "severity": severity,
            "duration": duration,
            "context_features": context_features,
            "flags": self._check_emergency_flags(final_extracted)
        }

    def _check_emergency_flags(self, final_extracted):
        critical_found = [e for e in ["chest pain", "shortness of breath", "stroke", "fainting", "loss of consciousness", "unilateral weakness", "speech difficulty"] if e in final_extracted]
        return critical_found if len(critical_found) >= 2 else []

clinical_parser = ClinicalParser()
