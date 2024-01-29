
# ----------------- Examples and Usage

import json
import logging
import os
from tree_utils.fs_recursion import fs_tree_recursion, fs_tree_recursive_tree_extractor, get_children_paths
from tree_utils.tree_recursion import ProcessingFunctions, RecursionStrategy, TreeNodeFunctions


def pretty_print(py_obj):
    obj_as_json_string = json.dumps(py_obj, indent=2)

    print(obj_as_json_string)
    # print(py_obj)


def example_extract_files(root_dir_path: str, options={}, mode=RecursionStrategy.ANY):

    tree_node_functions: TreeNodeFunctions = TreeNodeFunctions()

    def process_file(path: str):
        logging.debug(f"Processing file: {path}")
        print(path)
        return path

    def process_dir(dir_path: str, children_paths: list[str], children_processing_results: list[str]):
        logging.debug(f"Processing dir: {dir_path}")
        return children_processing_results

    tree_node_functions.is_leaf = os.path.isfile
    tree_node_functions.is_node = os.path.isdir
    tree_node_functions.get_children_ids = get_children_paths
    tree_node_functions.process_leaf = process_file
    tree_node_functions.process_node = process_dir

    return fs_tree_recursion(root_dir_path, tree_node_functions, options, mode=mode)


# Just print any path that would be processed
def print_fs_tree_recursion(node_path: str, options={}, mode=RecursionStrategy.ANY):

    node_processing_functions: ProcessingFunctions = ProcessingFunctions()

    def process_leaf(path: str):
        # print("Selected leaf: ")
        # print(path)

        return {
            'path': path
        }

    # children = [results of process_leaf]
    def process_node(dir_path: str, children_paths: list[str], children_processing_results: list[str]):
        print("Selected Node: ")
        print(dir_path)
        print("Children of node: ")
        print(children_paths)
        return None

    # def is_node_excluded(path):
    #    return True

    node_processing_functions.process_node = process_node
    node_processing_functions.process_leaf = process_leaf
    # node_processing_functions.is_node_excluded = is_node_excluded

    return fs_tree_recursion(node_path, node_processing_functions, options, mode=mode)


# Return a dict with a 'files' and 'dirs' key where all files and directories are sorted into
def example_split_dirs_files(node_path: str, options={}, mode=RecursionStrategy.BFS):

    result_data_store: dict = {}
    if 'files' not in result_data_store:
        result_data_store['files'] = []

    if 'dirs' not in result_data_store:
        result_data_store['dirs'] = []

    node_processing_functions: ProcessingFunctions = ProcessingFunctions()

    def process_leaf(path: str):
        result_data_store['files'].append(path)
        return None

    def process_node(dir_path: str, children_paths: list[str], children_processing_results: list[str]):
        result_data_store['dirs'].append(dir_path)
        return None

    node_processing_functions.process_node = process_node
    node_processing_functions.process_leaf = process_leaf

    fs_tree_recursion(node_path, node_processing_functions, options=options, mode=mode)

    return result_data_store


def example_collecting_fs_tree_recursive_tree_extractor(node_path: str, options={}, mode=RecursionStrategy.ANY):

    node_processing_functions: ProcessingFunctions = ProcessingFunctions()

    def process_leaf(path: str):
        # print("Selected leaf: ")
        # print(path)
        return {
            'path': path,
            'size': os.stat(path).st_size,
            'created': os.stat(path).st_atime
        }

    # children = [results of process_leaf]
    def process_node(dir_path: str, children_paths: list[str], children_processing_results: list[str]):
        # print("Selected Node: ")
        # print(dir_path)
        # print("Children of node: ")
        # print(children_paths)

        size = 0
        for child_proc_result in children_processing_results:
            if (child_proc_result and child_proc_result['size']):
                size += child_proc_result['size']

        return {
            'path': dir_path,
            'size': size,
            'created': os.stat(dir_path).st_atime,
        }

        # return children_processing_results

    node_processing_functions.process_node = process_node
    node_processing_functions.process_leaf = process_leaf

    return fs_tree_recursive_tree_extractor(node_path, node_processing_functions, options=options, mode=mode)


# example_path = '/home/pmarkus/repos/deduplicate-processor'
# processing_results_storage_dict = {}


# results = example_extract_files(example_path, {'exclude_regex_list': ['.+.git']}, mode=RecursionStrategy.ANY)
# results = example_extract_files(example_path, {'exclude_regex_list': ['.+.git']}, mode=RecursionStrategy.DFS)
# results = example_extract_files(example_path, {'exclude_regex_list': ['.+.git']}, mode=RecursionStrategy.BFS)
# results = example_extract_files(example_path)
# results = print_fs_tree_recursion(example_path, {'exclude_regex_list': ['.+.git']})
# results = example_split_dirs_files(example_path)

# results = example_collecting_fs_tree_recursive_tree_extractor(example_path, {'exclude_regex_list': ['.+.git']}, mode=RecursionStrategy.DFS)


# print("Returned results:")
# pretty_print(results)
