import os

def tree(dir_path, prefix=""):
    entries = sorted(os.listdir(dir_path))
    entries = [e for e in entries if e != '__pycache__']
    result = []

    for index, entry in enumerate(entries):
        path = os.path.join(dir_path, entry)
        connector = "└── " if index == len(entries) - 1 else "├── "
        result.append(f"{prefix}{connector}{entry}")

        if os.path.isdir(path):
            extension = "    " if index == len(entries) - 1 else "│   "
            result.extend(tree(path, prefix + extension))
    return result

def save_tree_to_file(root_dir="app", output_file="tree.txt"):
    structure = [root_dir + "/"]
    structure.extend(tree(root_dir))
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(structure))

if __name__ == "__main__":
    save_tree_to_file()
