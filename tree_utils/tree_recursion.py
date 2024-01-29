from enum import Enum
from typing import Any, Callable, TypedDict
import logging


class DotDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class ProcessingFunctions(DotDict):
    # OPTIONAL: Process a node id, returning a dictionary of extracted data from the node - Pass node id, children ids, children processing results - Return dict of extracted data
    process_node: Callable[[str, list[str], list[dict]], dict]
    # OPTIONAL: Process a leaf id, returning a dictionary of extracted data from the leaf - Pass leaf id - Return dict of extracted data
    process_leaf: Callable[[str], dict]
    # OPTIONAL: Hook for controlling the control flow (example is for excluding tree branches that fulfill certain criterias)
    is_node_excluded: Callable[[str], bool]
    # OPTIONAL: Hook for controlling the control flow (excluding leaf processing)
    is_leaf_excluded: Callable[[str], bool]


class TreeNodeFunctions(ProcessingFunctions):
    # REQUIRED: Check if node is a fork in the tree (has children) -> passes NodeId as argument which should be useable to uniquely identify the node (in a filesystem tree this is the file path)
    is_node: Callable[[str], bool]
    is_leaf: Callable[[str], bool]
    # REQUIRED: Pass (parent) node id - Return list of children ids
    get_children_ids: Callable[[str], list[str]]

    # OPTIONAL: Process a node id, returning a dictionary of extracted data from the node - Pass node id, children ids, children processing results - Return dict of extracted data
    # process_node: Callable[[str, list[str], list[dict]], dict]
    # OPTIONAL: Process a leaf id, returning a dictionary of extracted data from the leaf - Pass leaf id - Return dict of extracted data
    # process_leaf: Callable[[str], dict]


def _validate_generic_tree_recursion_params(root_node_id: str, tree_node_functions: TreeNodeFunctions):
    if (not root_node_id):
        raise Exception(f"Root node to recurse from 'root_node_id' was not passed")

    if (not hasattr(tree_node_functions, 'is_node')):
        raise Exception('tree_node_functions.is_node is not defined')

    if (not hasattr(tree_node_functions, 'is_leaf')):
        raise Exception('tree_node_functions.is_leaf is not defined')

    if (not hasattr(tree_node_functions, 'get_children_ids')):
        raise Exception('tree_node_functions.get_children_ids is not defined')

    """if (not process_functions.process_node):
        raise Exception('process_functions.process_node is not defined')

    if (not process_functions.process_leaf):
        raise Exception('process_functions.process_leaf is not defined')"""


def call_if_defined(obj, fn_key, *args):
    # some_fn = obj[fn_key]
    # some_fn2 = obj['is_leaf']
    if (fn_key in obj):
        stored_fn = getattr(obj, fn_key)
        return stored_fn(*args)

    return None


def handle_leaf_node(node_id: str, tree_node_functions: TreeNodeFunctions):
    if (not tree_node_functions.is_leaf(node_id)):
        return None

    is_leaf_excluded = call_if_defined(tree_node_functions, 'is_leaf_excluded', node_id)
    if (is_leaf_excluded):
        return None

    if (not hasattr(tree_node_functions, 'process_leaf')):
        return None

    return tree_node_functions.process_leaf(node_id)


"""def handle_child_node(child_node_id, tree_node_functions: TreeNodeFunctions):
    child_processing_result = _generic_tree_recursion(child_node_id, tree_node_functions)
    child_processing_results.append(child_processing_result)"""


def handle_fork_node(node_id: str, tree_node_functions: TreeNodeFunctions):
    if (not tree_node_functions.is_node(node_id)):
        return None

    is_node_excluded = call_if_defined(tree_node_functions, 'is_node_excluded', node_id)
    if (is_node_excluded):
        return None

    children_ids: list[str] = tree_node_functions.get_children_ids(node_id)

    if (not children_ids or len(children_ids) <= 0):
        return None

    child_processing_results = []
    for child_node_id in children_ids:
        child_processing_result = _generic_tree_recursion(child_node_id, tree_node_functions)
        child_processing_results.append(child_processing_result)

    if (not hasattr(tree_node_functions, 'process_node')):
        return None

    return tree_node_functions.process_node(node_id, children_ids, child_processing_results)

    # child_processing_results: list[dict] = list(map(lambda child_node_id: _generic_tree_recursion(child_node_id, tree_node_functions), children_ids))

# Max stack size in python is 993, so if your tree is over 993 levels deep, this needs to be increased (and run in own thread)
# import sys
# sys.setrecursionlimit(2000)

# iterative by default
# data arguments can be used to store information in to retrieve and/or write to during processing (example: Maintain a hashmap of all walked dirs/files)

# def generic_tree_recursion(root_node_id: str, node_type_functions: NodeTypeFunctions, child_functions: ChildrenFunctions, process_functions: ProcessFunctions) -> dict:


def _generic_tree_recursion(root_node_id: str, tree_node_functions: TreeNodeFunctions) -> dict:
    logging.debug(f"Processing node with id: {root_node_id}")

    # print(root_node_id)
    # validate_generic_tree_recursion_params(root_node_id, child_functions, process_functions)

    processing_result = handle_leaf_node(root_node_id, tree_node_functions)
    if (not processing_result):
        processing_result = handle_fork_node(root_node_id, tree_node_functions)

    return processing_result

    """if (tree_node_functions.is_leaf(root_node_id) and ):

        if (not tree_node_functions.is_leaf_excluded or not tree_node_functions.is_leaf_excluded(root_node_id)):
            return tree_node_functions.process_leaf(root_node_id)

    elif (tree_node_functions.is_node(root_node_id)):

        children_ids: list[str] = tree_node_functions.get_children_ids(root_node_id)

        if (children_ids and len(children_ids) > 0):

            child_processing_results = []
            for child_node_id in children_ids:

                if (not tree_node_functions.is_node_excluded or not tree_node_functions.is_node_excluded(child_node_id)):

                    child_processing_result = _generic_tree_recursion(child_node_id, tree_node_functions)
                    child_processing_results.append(child_processing_result)

            # child_processing_results: list[dict] = list(map(lambda child_node_id: _generic_tree_recursion(child_node_id, tree_node_functions), children_ids))

            if (tree_node_functions.process_node):
                return tree_node_functions.process_node(root_node_id, children_ids, child_processing_results)

    return None"""


def all_keys_in_dict(keys, dict):
    return all(map(lambda key: key in dict, keys))


def get_values_list_of_dict(keys, dict):
    list(map(lambda key: dict[key], keys))


def remove_keys_of_dict(keys, dict):
    for key in keys:
        del dict[key]


# 1. Process children before parent node (process leaves before nodes)
# 2. Retrieve child results to calculate parent node result
#
# Children NEED to be sorted leaf first for this to work

# Encounter node -> do nothing + push children onto stack (for making sure children are processed before the node)
# Encounter node -> if anything was already processed before that encounter -> then children must have been processed -> calculate processing result of node + pop from stack
# How to differentiate between the results of nodes/leafs that simply came before = siblings and the results of a node's children


def _iterative_generic_tree_processing(root_node_id: str, tree_node_functions: TreeNodeFunctions) -> dict:
    node_ids_to_process_stack: list = []
    node_ids_to_process_stack.push(root_node_id)

    # A particular problem of this method is that keys can get very very long -> very deep trees
    # For recursion for instance trees can only get 993 deep as that is the recursion limit
    # Might be optimized by providing a 'get_children_ids' and other tree_node_functions that map to a hash (through the caller would still need a memory efficient way to reverse lookup the hash -> needs a structure where redundancy is reduced -> maybe another tree)
    processing_results_dict = {}

    # processing_node_id_stack = []
    # node_children_ranges = []
    # node_children_ranges.append([len(processing_result_stack), len(processing_result_stack) + children_cnt])

    while len(node_ids_to_process_stack) > 0:
        # current_node_id = stack.pop()

        current_node_id = node_ids_to_process_stack[-1]

        leaf_processing_result = handle_leaf_node(current_node_id, tree_node_functions)

        # Leaf
        if (leaf_processing_result):
            # processing_result_leaf_stack.append(leaf_processing_result)

            processing_results_dict[current_node_id] = leaf_processing_result

            node_ids_to_process_stack.pop()
        # Node/Fork
        elif (not call_if_defined(tree_node_functions, 'is_node_excluded', current_node_id)):

            children_ids = tree_node_functions.get_children_ids(current_node_id)

            if (all_keys_in_dict(children_ids, processing_results_dict)):

                children_processing_results = get_values_list_of_dict(children_ids, processing_results_dict)
                node_processing_result = tree_node_functions.process_node(current_node_id, children_ids, children_processing_results)
                processing_results_dict[current_node_id] = node_processing_result

                # Clean already processed results from results dict -> defer saving child results if necessary to caller (with tree_node_functions)
                # -> Through this the children of processed braches are removed from tracking/memory
                remove_keys_of_dict(children_ids, processing_results_dict)

                node_ids_to_process_stack.pop()

            else:
                for child_node_id in children_ids:
                    node_ids_to_process_stack.push(child_node_id)


"""
# Original idea was to track the children results on a result stack -> which would be more memory efficient -> however it is more difficult to implement

processing_result_stack = []

processing_result_leaf_stack = []
processing_result_node_stack = []

node_result_tracking_stack = []
leaf_result_tracking_stack = []

encountered_ids_tracking_stack = []
encounter_tracking_stack = []

if (len(processing_result_leaf_stack) > 0, len(processing_result_node_stack) > 0):

    children_processing_results = processing_result_leaf_stack + processing_result_node_stack

    node_processing_result = tree_node_functions.process_node(current_node_id, [], children_processing_results)
    processing_result_node_stack.append(node_processing_result)

    processing_result_leaf_stack = []
    processing_result_node_stack = []
    stack.pop()"""

"""else:

    node_result_tracking_stack.push(len(processing_result_node_stack))
    leaf_result_tracking_stack.push(len(processing_result_leaf_stack))

    encounter_tracking_stack.append({
        'id': current_node_id,
        'node_ressults': len(processing_result_node_stack),
        'leaf_ressults': len(processing_result_leaf_stack)
    })

    for child_node_id in children_ids:
        stack.push(child_node_id)"""

# return processing_results_dict[root_node_id]


def get_node_class(classify_fn):

    def get_node_sorted_value(node_id):

        class_result = classify_fn

        if (isinstance(class_result, str)):
            return class_result

        return int(class_result)

    return get_node_sorted_value


def _order_nodes_leafs_first(node_ids: list[str], get_sort_value_of_node_id_fn: Callable[[str], bool]):
    return sorted(node_ids, key=get_node_class(get_sort_value_of_node_id_fn))


def _get_and_order_child_node_ids(node_id: str, get_children_ids: Callable[[str], list[str]], get_sort_value_of_node_id_fn: Callable[[str], bool]):
    node_children_ids = get_children_ids(node_id)

    return node_children_ids
    # return _order_nodes_leafs_first(node_children_ids, get_sort_value_of_node_id_fn)


# Breadth first search (leafs_first_tree_recursion)
def _bfs_generic_tree_recursion(root_node_id: str, tree_node_functions: TreeNodeFunctions):
    _validate_generic_tree_recursion_params(root_node_id, tree_node_functions)

    # Sort so that nodes come first in the child list (-> nodes are decended into first before going to the leaves)
    # Override get_children_ids to sort the returned node_ids by node type (leaf) before returning
    # This has the effect that the generic recursive function will handle all leaves before decending into the nodes that have children (resulting in a pseudo breadth first search)
    # algorithm -> pseudo because the order in the tree is not respected and modified while handling

    # A reference to the function needs to be saved here, to prevent a loop below
    get_children_without_sorting = tree_node_functions.get_children_ids

    def get_child_ids_order_leafs_first(fork_node_id: str) -> list[str]:
        return _get_and_order_child_node_ids(fork_node_id, get_children_without_sorting, tree_node_functions.is_leaf)

    tree_node_functions.get_children_ids = get_child_ids_order_leafs_first

    return _generic_tree_recursion(root_node_id, tree_node_functions)


# Breadth first search (nodes first recursion -> always goes to the deepest depth of the nodes first)
def _dfs_generic_tree_recursion(root_node_id: str, tree_node_functions: TreeNodeFunctions):

    _validate_generic_tree_recursion_params(root_node_id, tree_node_functions)

    get_children_without_sorting = tree_node_functions.get_children_ids

    def get_child_ids_order_forks_first(fork_node_id: str) -> list[str]:
        return _get_and_order_child_node_ids(fork_node_id, get_children_without_sorting, tree_node_functions.is_node)

    tree_node_functions.get_children_ids = get_child_ids_order_forks_first

    return _generic_tree_recursion(root_node_id, tree_node_functions)


def _any_first_generic_tree_recursion(root_node_id: str, tree_node_functions: TreeNodeFunctions):

    _validate_generic_tree_recursion_params(root_node_id, tree_node_functions)

    return _generic_tree_recursion(root_node_id, tree_node_functions)


def _non_recursive_iterative_generic_tree_processing(root_node_id: str, tree_node_functions: TreeNodeFunctions):

    _validate_generic_tree_recursion_params(root_node_id, tree_node_functions)
    return _iterative_generic_tree_processing(root_node_id, tree_node_functions)


class RecursionStrategy(Enum):
    ITER = 'iteration'
    ANY = 'anyfirst'
    BFS = 'breadth_first'
    DFS = 'depth_first'


recursion_mode_functions = {
    RecursionStrategy.ITER: _non_recursive_iterative_generic_tree_processing,
    RecursionStrategy.ANY: _any_first_generic_tree_recursion,
    RecursionStrategy.BFS: _bfs_generic_tree_recursion,
    RecursionStrategy.DFS: _dfs_generic_tree_recursion
}


def universal_tree_recursion(root_node_id: str, tree_node_functions: TreeNodeFunctions, mode=RecursionStrategy.ANY):
    print(f"Recursing tree at: '{root_node_id}'")
    print(f"With strategy: '{str(mode)}'")
    print("With functions: ")
    print(tree_node_functions)

    return recursion_mode_functions[mode](root_node_id, tree_node_functions)
