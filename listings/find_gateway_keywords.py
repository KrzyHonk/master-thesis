def find_gateway_keywords(doc: Doc, svos: List[SvoConstruct]):
    for sentence in doc.sents:
        for word in sentence:
            if word.text.casefold() in Consts.gateways_keywords:
                head = word.head
                svo = next((svo for svo in svos if svo.get_verb().i == head.i), None)
                if svo is not None:
                    svo.set_gateway_keyword(word.text)
