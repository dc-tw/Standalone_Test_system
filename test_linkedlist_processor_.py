# test_linkedlist_processor.py

import unittest
import ctypes
from main import (
    LinkedListProcessor, create_linked_list, NODE_VALUE_CTYPE,
    DLL_PATH, DLL_FUNC_NAME, CALL_CONV, LIST_KIND
)

class TestLinkedListProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = LinkedListProcessor(
            DLL_PATH, DLL_FUNC_NAME, CALL_CONV, NODE_VALUE_CTYPE, LIST_KIND
        )

    def tearDown(self):
        self.processor.dispose()

    def test_single_node(self):
        head = create_linked_list([2.0], LIST_KIND)
        result = self.processor.process(head)
        self.assertEqual(result["success"], 1)
        self.assertEqual(head.contents.value, 4.0)

    def test_three_nodes(self):
        head = create_linked_list([1.0, 2.0, 3.0], LIST_KIND)
        result = self.processor.process(head)
        self.assertEqual(result["success"], 3)
        self.assertEqual(head.contents.value, 2.0)
        self.assertEqual(head.contents.next.contents.value, 4.0)
        self.assertEqual(head.contents.next.contents.next.contents.value, 6.0)

    def test_error_node(self):
        head = create_linked_list([1.0, -2.0, 3.0], LIST_KIND)
        result = self.processor.process(head, on_error="skip")
        self.assertEqual(result["fail"], 1)
        self.assertEqual(head.contents.value, 2.0)
        self.assertEqual(head.contents.next.contents.value, -2.0)  # 未變
        self.assertEqual(head.contents.next.contents.next.contents.value, 6.0)

    def test_stop_condition(self):
        head = create_linked_list([1.0, 2.0, 10.0], LIST_KIND)
        result = self.processor.process(
            head, stop_condition=lambda node, idx, in_v, out_v, rc: out_v > 5
        )
        self.assertTrue(result["success"] < 3)

    def test_none_head(self):
        result = self.processor.process(None)
        self.assertEqual(result["success"], 0)
        self.assertEqual(result["fail"], 0)

if __name__ == "__main__":
    unittest.main()
