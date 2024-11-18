import unittest
import ast
from dataclasses import dataclass
from typing import List, Optional

from datasetgen.mcts.chunked_mcts import ChunkedMCTS


@dataclass
class ProgramChunk:
    docstring: str
    code: str
    state: Optional['GameState'] = None
    reward: float = 0.0


class TestProgramChunkSplitter(unittest.TestCase):
    def setUp(self):
        self.splitter = ChunkedMCTS(None, None, None, "", None)

    def test_single_chunk(self):
        code = '''
"""First task"""
x = 1
y = 2
'''
        chunks = self.splitter._split_into_chunks(code)
        self.assertEqual(len(chunks), 1)
        self.assertTrue("First task" in chunks[0].code)
        self.assertTrue( "x = 1\ny = 2" in chunks[0].code.strip())

    def test_comment(self):
        code = '''
"""First task"""
# This is a comment
x = 1
y = 2
'''
        chunks = self.splitter._split_into_chunks(code)
        self.assertEqual(len(chunks), 1)
        self.assertTrue("First task" in chunks[0].code)
        self.assertTrue("x = 1\ny = 2" in chunks[0].code.strip())
        self.assertTrue("# This is a comment" in chunks[0].code.strip())

    def test_multiple_chunks(self):
        code = '''
"""First task"""
x = 1

"""Second task"""
y = 2

"""Third task"""
z = 3
'''
        chunks = self.splitter._split_into_chunks(code)
        self.assertEqual(len(chunks), 3)
        for program, task, value in zip(chunks, ["First task", "Second task", "Third task"], ["x = 1", "y = 2", "z = 3"]):
            self.assertTrue(task in program.code)
            self.assertTrue(value in program.code)


    def test_multiline_code(self):
        code = '''
"""Build structure"""
x = 1
y = 2
z = x + y

"""Place items"""
items = [1, 2, 3]
for item in items:
    place(item)
'''
        chunks = self.splitter._split_into_chunks(code)
        self.assertEqual(len(chunks), 2)
        self.assertTrue("x = 1" in chunks[0].code)
        self.assertTrue("for item in items:" in chunks[1].code)

    def test_multiline_docstring(self):
        code = '''
"""
Build initial structure
With multiple lines
"""
x = 1

"""Place items"""
y = 2
'''
        chunks = self.splitter._split_into_chunks(code)
        self.assertEqual(len(chunks), 2)
        self.assertTrue("Build initial structure\nWith multiple lines" in chunks[0].code)

    def test_no_docstring(self):
        code = "x = 1\ny = 2"
        chunks = self.splitter._split_into_chunks(code)
        self.assertEqual(len(chunks), 0)

    def test_function_definitions(self):
        code = '''
"""Setup functions"""
def func1():
    return 1

def func2():
    x = 1
    return x

"""Use functions"""
result = func1() + func2()
'''
        chunks = self.splitter._split_into_chunks(code)
        self.assertEqual(len(chunks), 2)
        self.assertTrue("def func1():" in chunks[0].code)
        self.assertTrue("def func2():" in chunks[0].code)
        self.assertTrue("result = func1() + func2()" in chunks[1].code)

    def test_empty_chunks(self):
        code = '''
"""Task 1"""

"""Task 2"""
x = 1
'''
        chunks = self.splitter._split_into_chunks(code)
        self.assertEqual(len(chunks), 2)
        self.assertTrue("Task 2" in chunks[1].code)

    def test_code_with_strings(self):
        code = '''
"""First task"""
x = "This is a string"
y = """This is a multiline
string but not a docstring"""
'''
        chunks = self.splitter._split_into_chunks(code)
        self.assertEqual(len(chunks), 1)
        self.assertTrue('x = "This is a string"' in chunks[0].code)
        self.assertTrue('y = """This is a multiline' in chunks[0].code)


if __name__ == '__main__':
    unittest.main()