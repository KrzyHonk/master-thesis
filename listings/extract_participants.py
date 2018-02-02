def extract_participants(sentence: Span):
    participants_base_keywords_synonyms = prepare_base_keywords_synonyms()

    tmp_output = []
    output = []
    for word in sentence:
        if word.dep_ in {"nsubj", "nsubjpass"}:
            participant = Participant(word)
            if word.pos_ == "pron":
                participant.set_pronoun(True)
            tmp_output.append(participant)

    # Check if possible participant is a part of conjunction
    for word in sentence:
        if word.dep_ == "conj":
            for child in word.children:
                if child.dep_ in {"pobj", "dobj", "iobj", "attr"}:
                    participant = Participant(child)
                    if child.pos_ == "pron":
                        participant.set_pronoun(True)
                    tmp_output.append(participant)

    # Check if Participant is an acceptable entity
    for participant in tmp_output:
        participant_text = participant.get_participant_token().text

        insert_flag = False
        # Check whether participant is a pronoun
        if participant.is_pronoun():
            insert_flag = True

        if insert_flag is False:
            # Analyze participant hypernyms, in search for one of base keywords
            insert_flag = analyze_participants_hypernyms(participant_text, 
				participants_base_keywords_synonyms)

        if insert_flag is False:
            # Check if participant is one of keywords
            insert_flag = validate_participant_keyword_list(participant_text)
        if insert_flag:
            output.append(participant)

    return output