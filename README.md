# A Functional util for recursive tree processing

### Usage
```python
from tree_utils.fs_recursion import RecursionStrategy, ProcessingFunctions, fs_tree_recursion, TreeNodeFunctions, get_children_paths
from tree_utils.tree_recursion import ProcessingFunctions, RecursionStrategy, TreeNodeFunctions

def example_extract_file_paths(root_dir_path: str, options={}, mode=RecursionStrategy.ANY):

    tree_node_functions: TreeNodeFunctions = TreeNodeFunctions()

    def process_file(path: str):
        logging.debug(f"Processing file: {path}")

        print(path)

        # Return the path as the desired content extracted from the node
        return path

    def process_dir(dir_path: str, children_paths: list[str], children_processing_results: list[str]):
        # The paths we returned in 'process_file' are collected and passed to the 'process_dir' function as the children_processing_results

        logging.debug(f"Processing dir: {dir_path}")
        return children_processing_results

    tree_node_functions.is_leaf = os.path.isfile
    tree_node_functions.is_node = os.path.isdir
    tree_node_functions.get_children_ids = get_children_paths
    tree_node_functions.process_leaf = process_file
    tree_node_functions.process_node = process_dir

    return fs_tree_recursion(root_dir_path, tree_node_functions, options, mode=mode)

example_extract_file_paths('/some/path')
```