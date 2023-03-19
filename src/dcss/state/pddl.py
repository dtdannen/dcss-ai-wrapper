from datetime import datetime


def get_pddl_problem(domainname: str = "dcss", problemname: str = "test_prob", objects: [str] = None,
                     init_facts: [str] = None, goals: [str] = None, map_s: str = None) -> str:
    """
    Returns a complete pddl state string ready to be passed to a planner, given the domain name, objects, init facts,
    and goals.

    :param domainname: name to match to the corresponding pddl domain file, by default this is "dcss" to match the
     "models/fastdownward_simple.pddl" domain file.
    :param problemname: name to identify this state file, change it if you'd like something more descriptive
    :param objects: all objects to be included under the :objects clause
    :param init_facts: all facts to be included under the :init clause
    :param goals: all goals to be included under the (:goal clause and if more than one is given, will automatically
     be listed as part of an "(and" clause
    :returns: a string containing a complete pddl state file, ready to be given to a pddl planner
    """

    pddl_str = ";; Generated on {}\n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    if map_s:
        # add comments to the beginning of lines
        map_s = ';; ' + map_s
        map_s = map_s.replace('\n', '\n;; ')
        pddl_str += map_s + "\n\n"

    pddl_str += "(define (problem {problemname})\n  (:domain {domainname})\n\n".format(problemname=problemname,
                                                                                    domainname=domainname)
    pddl_str += "  (:objects \n"
    for obj in objects:
        pddl_str += "    {}\n".format(obj)

    pddl_str += "  ) ;; closes the '(:objects' clause\n\n"

    pddl_str += "  (:init \n"
    for fact in init_facts:
        pddl_str += "    {}\n".format(fact)

    pddl_str += "  ) ;; closes the '(:init' clause\n\n"

    pddl_str += "  (:goal \n  (and \n"
    for goal in goals:
        pddl_str += "    {}\n".format(goal)
    pddl_str += "  )\n"
    pddl_str += ")\n\n)"

    return pddl_str
