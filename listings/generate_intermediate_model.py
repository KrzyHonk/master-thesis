def generate_intermediate_model(doc: Doc):
    # elements extraction phase
    participants, svos = extract_elements_from_document(doc)

    # semantic analysis - find possible gateway relations
    gateways.find_gateway_keywords(doc, svos)

    # generate intermediate diagram model
    conditional_gateway_started = False
    parallel_gateway_started = False
    gateway_branch_index = 0
    activities_list = []
    end_event_jump_phases = []

    order = 0
    add_start_activity(activities_list)

    while svos:
        svo, svos = get_head_from_list(svos)
        # check if this svo is a part of conditional gateway
        if svo.get_gateway_keyword() is not None \
                and svo.get_gateway_keyword().casefold() in Consts.conditional_keywords:
            if parallel_gateway_started:
                parallel_gateway_started = False
            if not conditional_gateway_started:
                order += 1
                conditional_gateway_started = True
                gateway_branch_index = 0
            gateway_branch_index, conditional_gateway_started = \
                add_conditional_activity(svos, svo, order, gateway_branch_index,
                                         conditional_gateway_started, activities_list)

        # check if this svo is a part of parallel gateway
        elif svo.get_gateway_keyword() is not None \
                and svo.get_gateway_keyword().casefold() in Consts.parallel_keywords:
            if conditional_gateway_started:
                conditional_gateway_started = False
            if not parallel_gateway_started:
                order += 1
                parallel_gateway_started = True
                gateway_branch_index = 0
            gateway_branch_index, parallel_gateway_started = \
                add_parallel_activities(svos, svo, order, gateway_branch_index,
                                        parallel_gateway_started, activities_list)

        # check if this SVO is a default flow of gateway
        elif svo.get_gateway_keyword() is not None \
                and svo.get_gateway_keyword().casefold() in Consts.default_flow_keywords:
            # check if it is a default flow of conditional gateway
            if conditional_gateway_started:
                add_default_flow_to_gateway(svos, svo, order, 
				gateway_branch_index, activities_list)
                gateway_branch_index += 1
            # check if it is another flow of parallel gateway
            elif parallel_gateway_started:
                add_activity_to_parallel_gateway(svos, svo, order, 
				gateway_branch_index, activities_list)
                gateway_branch_index += 1
            # add it as a sequence flow
            else:
                if conditional_gateway_started:
                    conditional_gateway_started = False
                if parallel_gateway_started:
                    parallel_gateway_started = False
                gateway_branch_index = 0
                order = add_svo_as_task(svos, svo, order, activities_list)

        # add SVO as a task joined by sequence flow
        else:
            if conditional_gateway_started:
                # if conditional gateway has only one flow
				# add default flow which leads to end event
                if gateway_branch_index < 2:
                    suffix = string.ascii_lowercase[gateway_branch_index]
                    add_default_flow_pointing_to_end_event(activities_list, 
					end_event_jump_phases, order, suffix)
                conditional_gateway_started = False
            if parallel_gateway_started:
                parallel_gateway_started = False
            gateway_branch_index = 0
            order = add_svo_as_task(svos, svo, order, activities_list)

    if conditional_gateway_started and gateway_branch_index == 1:
        suffix = string.ascii_lowercase[gateway_branch_index]
        add_default_flow_pointing_to_end_event(activities_list, 
		end_event_jump_phases, order, suffix)

    order += 1
    for end_event_jump in end_event_jump_phases:
        end_event_jump[Consts.activity_prop] = "goto " + str(order)
    add_end_event(activities_list, order)

    export_phases_to_file(activities_list)