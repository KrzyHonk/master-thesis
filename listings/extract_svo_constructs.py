def extract_svo_constructs(sentence: Span, participants: List[Participant]):
    tmp_output = []
    root = sentence.root
    nsubj_list = utils.find_tokens_subtree(root, ["nsubj"])
    nsubjpass_list = utils.find_tokens_subtree(root, ["nsubjpass"])
    if len(nsubj_list) > 0:
        for token in nsubj_list:
            subject = token
            verb = subject.head
            output_obj = find_token_in_children(verb)
            if output_obj is None:
                output_obj = find_token_in_ancestors(verb)
            if subject is not None and verb is not None:
                svo = SvoConstruct(subject, verb, output_obj)
                if len(tmp_output) > 0:
                    if check_if_svo_is_unique(svo, tmp_output):
                        tmp_output.append(svo)
                else:
                    tmp_output.append(svo)

    if len(nsubjpass_list) > 0:
        for token in nsubjpass_list:
            subject = token
            verb = subject.head
            if subject is not None and verb is not None:
                svo = SvoConstruct(subject=subject, verb=verb, position=verb.i)
                if len(tmp_output) > 0:
                    if check_if_svo_is_unique(svo, tmp_output):
                        tmp_output.append(svo)
                else:
                    tmp_output.append(svo)

    # Check if conjunction exists in sentence and extract possible SVO
    for token in sentence:
        if token.dep_ == "conj" and token.pos_ == "VERB":
            output_obj = find_token_children(token)
            if output_obj is None:
                output_obj = find_token_ancestors(token)
            subject = find_subject_for_conjunction(token)

            if subject is not None and token is not None:
                svo = SvoConstruct(subject, token, output_obj)
                if len(tmp_output) > 0:
                    if check_if_svo_is_unique(svo, tmp_output):
                        tmp_output.append(svo)
                else:
                    tmp_output.append(svo)

    # Check if extracted svo can be assigned to verified participant
    assign_svo_to_participant(tmp_output, participants)
    return tmp_output