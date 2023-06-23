from .syntax_graph import SyntaxGraph
from .syntax_node import SyntaxNode
from ..morphology.part_of_speech import PartOfSpeech


def subgraph_end(graph: SyntaxGraph, node: SyntaxNode):

    if node.is_phrase:
        return None

    # test each node from left to right
    segment_nodes = graph.segment_nodes
    for i in range(len(segment_nodes) - 1, node.index, -1):

        # the node to test
        end = segment_nodes[i]

        # walk the dependency chain, looking for rightwards dependencies
        start = end
        while start and start is not node:
            head = graph.head(start)

            if head and head.is_phrase:
                head = head.start

            # leftwards head
            if head and head.index >= start.index:
                head = None

            # if no head, check if we are at the start of a phrase
            if head is None:
                for phrase in graph.phrases:
                    if phrase.start is start:

                        phrase_head = graph.head(phrase)
                        if phrase_head and not phrase_head.is_phrase and phrase_head.index < start.index:
                            head = phrase_head
                            break

            # if no head, check incoming edges
            if head is None:
                for edge in graph.edges:
                    if edge.head is start:
                        dependent = edge.dependent
                        if dependent.is_phrase:
                            if dependent.start.index < start.index:
                                head = dependent.start
                        else:
                            if dependent.index < start.index:
                                head = dependent

            # disconnected POS:VOC, POS:PREV
            if head is None:
                previous = graph.previous_segment_node(start)
                if previous:
                    part_of_speech = previous.part_of_speech
                    if part_of_speech == PartOfSpeech.VOCATIVE or part_of_speech == PartOfSpeech.PREVENTIVE:
                        head = previous

            # disconnected POS:EXP
            if head is None and start.part_of_speech == PartOfSpeech.EXCEPTIVE:
                head = graph.previous_segment_node(start)

            start = head

        if start is node:
            return end

    return None
