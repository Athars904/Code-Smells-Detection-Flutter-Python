import ast
import os
import radon.complexity as radon_complexity
import re

# Global counter for code smells
code_smell_count = 0

class CodeSmellDetector:
    def __init__(self, directory):
        self.directory = directory

    def scan_for_smells(self):
        global code_smell_count
        code_smell_count = 0
        smells = []

        # Walk through the directory to find Python and Dart files
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if file.endswith('.py') or file.endswith('.dart'):
                    file_path = os.path.join(root, file)
                    if file.endswith('.py'):
                        smells.extend(self.analyze_python_file(file_path))
                    elif file.endswith('.dart'):
                        smells.extend(self.analyze_dart_file(file_path))

        return smells,code_smell_count

    def analyze_python_file(self, file_path):
        global code_smell_count
        smells = []

        try:
            with open(file_path, 'r', errors='ignore', encoding='utf-8') as file:
                content = file.read()
                tree = ast.parse(content)

                smells.extend(self.check_python_functions(tree, file_path))
                smells.extend(self.check_python_classes(tree, file_path))
                smells.extend(self.check_complexity(file_path, content))
                smells.extend(self.check_for_duplicates(content))
                smells.extend(self.check_for_magic_numbers(content))
                smells.extend(self.check_excessive_comments(content, file_path))
                smells.extend(self.check_long_lines(content, file_path))
                smells.extend(self.check_unreachable_code(tree, file_path))

        except Exception as e:
            smells.append(f"Error analyzing Python file {file_path}: {str(e)}")
            code_smell_count += 1

        return smells

    def analyze_dart_file(self, file_path):
        global code_smell_count
        smells = []

        try:
            with open(file_path, 'r', errors='ignore', encoding='utf-8') as file:
                content = file.read()
                if not content:  # Handle empty files
                    smells.append(f"File {file_path} is empty or unreadable.")
                    code_smell_count += 1
                    return smells

                smells.extend(self.check_for_duplicates(content))
                smells.extend(self.check_for_magic_numbers(content))
                smells.extend(self.check_excessive_comments(content, file_path))
                smells.extend(self.check_long_lines(content, file_path))
                smells.extend(self.check_dart_complexity(content, file_path))

        except Exception as e:
            smells.append(f"Error analyzing Dart file {file_path}: {str(e)}")
            code_smell_count += 1

        return smells

    def check_python_functions(self, tree, file_path):
        global code_smell_count
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 10:
                    issues.append(f"Large function: {node.name} in {file_path}")
                    code_smell_count += 1

                if len(node.args.args) > 5:
                    issues.append(f"Too many arguments: {node.name} in {file_path}")
                    code_smell_count += 1

                return_statements = sum(isinstance(n, ast.Return) for n in node.body)
                if return_statements > 2:
                    issues.append(f"Too many return statements: {node.name} in {file_path}")
                    code_smell_count += 1

        return issues

    def check_python_classes(self, tree, file_path):
        global code_smell_count
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_lines = len([n for n in node.body if isinstance(n, (ast.FunctionDef, ast.Assign))])
                if class_lines > 50:
                    issues.append(f"Large class: {node.name} in {file_path}")
                    code_smell_count += 1

        return issues

    def check_complexity(self, file_path, content):
        global code_smell_count
        issues = []

        try:
            results = radon_complexity.cc_visit(content)

            for result in results:
                if result.complexity > 10:
                    issues.append(f"High complexity: {result.name} in {file_path} with complexity {result.complexity}")
                    code_smell_count += 1

        except Exception as e:
            issues.append(f"Error analyzing complexity for {file_path}: {str(e)}")
            code_smell_count += 1

        return issues

    def check_dart_complexity(self, content, file_path):
        global code_smell_count
        issues = []
        try:
            lines = content.split('\n')
            complexity_threshold = 10  # Example threshold for Dart
            function_regex = re.compile(r'(?:void|int|String|bool|double|dynamic|Future<.*?>)\s+\w+\s*\(.*?\)\s*\{')

            for line_num, line in enumerate(lines, start=1):
                if function_regex.search(line):
                    nesting = line.count('{') - line.count('}')
                    if nesting > complexity_threshold:
                        issues.append(f"High complexity in function at line {line_num} in {file_path}")
                        code_smell_count += 1

        except Exception as e:
            issues.append(f"Error checking Dart complexity in {file_path}: {str(e)}")
            code_smell_count += 1

        return issues

    def check_for_duplicates(self, content):
        global code_smell_count
        issues = []
        lines = content.split('\n')
        seen_blocks = set()

        for i in range(len(lines) - 5):
            block = tuple(lines[i:i+5])
            if block in seen_blocks:
                issues.append(f"Duplicated code detected: Block starting at line {i+1}")
                code_smell_count += 1
            else:
                seen_blocks.add(block)

        return issues

    def check_for_magic_numbers(self, content):
        global code_smell_count
        issues = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, start=1):
            if any(char.isdigit() for char in line):
                issues.append(f"Magic number detected at line {line_num}")
                code_smell_count += 1

        return issues

    def check_excessive_comments(self, content, file_path):
        global code_smell_count
        issues = []

        comment_count = content.count("//") + content.count("#")
        if comment_count > 20:
            issues.append(f"Excessive comments in {file_path} (more than 20 comments)")
            code_smell_count += 1

        return issues

    def check_long_lines(self, content, file_path):
        global code_smell_count
        issues = []

        lines = content.split('\n')
        for i, line in enumerate(lines, start=1):
            if len(line) > 120:
                issues.append(f"Long line detected in {file_path} at line {i}")
                code_smell_count += 1

        return issues

    def check_unreachable_code(self, tree, file_path):
        global code_smell_count
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_return = False
                for stmt in node.body:
                    if isinstance(stmt, ast.Return):
                        has_return = True
                    elif has_return:
                        issues.append(f"Unreachable code after return in function {node.name} in {file_path}")
                        code_smell_count += 1
                        break

        return issues


if __name__ == "__main__":
    directory = input("Enter the directory to scan for code smells: ")
    detector = CodeSmellDetector(directory)
    smells = detector.scan_for_smells()

    if smells:
        print("\nCode smells detected:")
        for smell in smells:
            print(smell)

    print(f"\nTotal code smells detected: {code_smell_count}")
