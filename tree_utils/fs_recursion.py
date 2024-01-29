import os
from typing import Any, Callable
from tree_utils.tree_recursion import DotDict, ProcessingFunctions, RecursionStrategy, TreeNodeFunctions
import tree_utils.tree_recursion as tree_recursion
import re


def get_children_paths(dir_path, sort_fn=None):
    child_paths = os.listdir(dir_path)

    if (sort_fn):
        child_paths = sort_fn(child_paths)

    return list(map(lambda child_path: os.path.join(dir_path, child_path), child_paths))


def compile_pattern_list(patterns: list[str]) -> list[re.Pattern]:
    return list(map(lambda pattern: re.compile(pattern), patterns))


def path_matches_any_pattern(path, regex_list: list[re.Pattern]):
    for reg_ex in regex_list:
        # print(f"Matching '{path}' against '{reg_ex}'")
        if (reg_ex.match(path)):
            return True

    return False


# Recursive function for filesystem transversal with then 'os' package
def fs_tree_recursion(node_path: str, node_processing_functions: ProcessingFunctions, options={}, mode=RecursionStrategy.ANY) -> dict:
    if (not os.path.exists(node_path)):
        raise Exception("fs_tree_recursion Error - Path: " + str(node_path) + " does not exist")

    tree_node_functions: TreeNodeFunctions = TreeNodeFunctions()

    tree_node_functions.is_leaf = os.path.isfile
    tree_node_functions.is_node = os.path.isdir
    tree_node_functions.get_children_ids = get_children_paths

    tree_node_functions.update(node_processing_functions)

    if ('sort_fn' in options):
        tree_node_functions.get_children_ids = lambda dir_path: get_children_paths(dir_path, options['sort_fn'])

    if ('exclude_regex_list' in options and options['exclude_regex_list']):
        exclude_regex_list = compile_pattern_list(options['exclude_regex_list'])

        def is_node_excluded(path: str) -> bool:
            return path_matches_any_pattern(path, exclude_regex_list)

        tree_node_functions.is_node_excluded = is_node_excluded
        tree_node_functions.is_leaf_excluded = is_node_excluded

    # tree_node_functions.process_leaf = node_processing_functions.process_leaf
    # tree_node_functions.process_node = node_processing_functions.process_node

    return tree_recursion.universal_tree_recursion(node_path, tree_node_functions, mode=mode)


# Transverse a fs tree and process it into another fs tree, but in a different format
# Each node in the output tree has "processed/calculated data, how defined from the caller function, where process_leaf, process_node calculate this additional (meta) data"
# The structure is saved that each node is defined by its path which is the key of the node
# Then the content value of the node has a 'files' and a 'dirs' property where the entries for the child files/dirs are stored respectively
def fs_tree_recursive_tree_extractor(root_node_path: str, data_extraction_node_processing_functions: ProcessingFunctions, options={}, mode=RecursionStrategy.ANY):

    # All children are evaluated, when evaluating a node
    mode: RecursionStrategy = RecursionStrategy.DFS

    if (not data_extraction_node_processing_functions.process_leaf):
        raise Exception("process_functions.process_leaf not defined")
    if (not data_extraction_node_processing_functions.process_node):
        raise Exception("process_functions.process_node not defined")

    result_data_store: dict = {}

    def process_leaf(path: str):
        file_results_dict = {}
        file_result = data_extraction_node_processing_functions.process_leaf(path)
        file_results_dict.update(file_result)
        file_results_dict['path'] = path
        return file_results_dict

    # children = [results of process_leaf]
    def process_node(path: str, children_paths: list[str], children_processing_results: list[str]):

        node_results_dict = {}
        for index, child_path in enumerate(children_paths):

            if child_path in result_data_store:

                if 'dirs' not in node_results_dict:
                    node_results_dict['dirs'] = []

                node_results_dict['dirs'].append(children_processing_results[index])
            else:
                if 'files' not in node_results_dict:
                    node_results_dict['files'] = []
                node_results_dict['files'].append(children_processing_results[index])

        dir_result = data_extraction_node_processing_functions.process_node(path, children_paths, children_processing_results)
        node_results_dict.update(dir_result)

        node_results_dict['path'] = path
        result_data_store[path] = node_results_dict

        return node_results_dict

    composed_processing_functions: ProcessingFunctions = ProcessingFunctions()
    composed_processing_functions.process_node = process_node
    composed_processing_functions.process_leaf = process_leaf

    fs_tree_recursion(root_node_path, composed_processing_functions, options=options, mode=mode)
    return result_data_store


def apply_file_function_recursive(node_path: str, file_apply_function: Callable[[str], Any], options={}, mode=RecursionStrategy.BFS):
    node_processing_functions: ProcessingFunctions = ProcessingFunctions()

    def process_node(dir_path: str, children_paths: list[str], children_processing_results: list[str]):
        return None

    node_processing_functions.process_node = process_node
    node_processing_functions.process_leaf = file_apply_function

    fs_tree_recursion(node_path, node_processing_functions, options=options, mode=mode)


def apply_dir_function_recursive(node_path: str, dir_apply_function: Callable[[str], Any], options={}, mode=RecursionStrategy.BFS):
    node_processing_functions: ProcessingFunctions = ProcessingFunctions()

    def process_leaf(path: str):
        return None

    node_processing_functions.process_node = dir_apply_function
    node_processing_functions.process_leaf = process_leaf

    fs_tree_recursion(node_path, node_processing_functions, options=options, mode=mode)
