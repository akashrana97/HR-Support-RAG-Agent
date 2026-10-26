"""Exercise workflow decisions without API credentials or model downloads."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]


def workflow_functions(**bindings):
    tree = ast.parse((ROOT / 'app/rag/workflow.py').read_text())
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    module = ast.Module(body=functions, type_ignores=[])
    env = {'AgentState': dict, 'Literal': __import__('typing').Literal, **bindings}
    exec(compile(module, 'workflow.py', 'exec'), env)
    env.update(bindings)
    return env


class HRWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.settings = SimpleNamespace(enable_web_fallback=True, max_retries=1)
        self.fn = workflow_functions(settings=self.settings)

    def test_all_substantive_requests_retrieve_private_knowledge(self):
        self.assertEqual(self.fn['route_after_router']({'source_used': 'kb'}), 'retrieve_kb')
        # Stale clients cannot bypass private retrieval using the removed flag.
        self.assertEqual(self.fn['route_after_router']({'source_used': 'kb', 'web_search': True}), 'retrieve_kb')

    def test_greetings_can_receive_direct_responses(self):
        self.assertEqual(self.fn['route_after_router']({'source_used': 'direct'}), 'direct_answer')

    def test_good_private_evidence_answers_without_web(self):
        self.assertEqual(self.fn['after_kb']({'kb_grade': 'good'}), 'generate_from_kb')

    def test_weak_private_evidence_falls_back_to_tavily(self):
        self.assertEqual(self.fn['after_kb']({'kb_grade': 'weak'}), 'search_web')

    def test_disabling_fallback_escalates_weak_evidence(self):
        self.settings.enable_web_fallback = False
        self.assertEqual(self.fn['after_kb']({'kb_grade': 'weak'}), 'insufficient')

    def test_web_evidence_is_graded_before_answering(self):
        self.assertEqual(self.fn['after_web']({'web_grade': 'good', 'retry_count': 0}), 'generate_from_web')
        self.assertEqual(self.fn['after_web']({'web_grade': 'weak', 'retry_count': 0}), 'rewrite_query')
        self.assertEqual(self.fn['after_web']({'web_grade': 'weak', 'retry_count': 1}), 'insufficient')

    def test_unresolved_question_refers_to_hr(self):
        result = self.fn['insufficient']({'trace': []})
        self.assertEqual(result['source_used'], 'insufficient_evidence')
        self.assertIn('HR team', result['answer'])
        self.assertNotIn('IT help desk', result['answer'])

    def test_private_answer_uses_hr_context_and_preserves_citations(self):
        prompts = []
        def invoke(prompt):
            prompts.append(prompt)
            return SimpleNamespace(content='This example policy requires manager review.')
        fn = workflow_functions(settings=self.settings, llm=lambda: SimpleNamespace(invoke=invoke))
        doc = SimpleNamespace(metadata={'source': 'data/sample_kb/hr_handbook.md'},
                              page_content='Fictional demo policy: manager review is required.')
        result = fn['generate_from_kb']({'question': 'How do I apply for leave?', 'kb_docs': [doc, doc], 'trace': []})
        self.assertIn('enterprise HR support copilot', prompts[0])
        self.assertIn('fictional/demo', prompts[0])
        self.assertIn(doc.page_content, prompts[0])
        self.assertEqual(result['source_used'], 'private_kb')
        self.assertEqual(len(result['citations']), 1)
        self.assertEqual(result['citations'][0]['title'], 'hr_handbook.md')


if __name__ == '__main__':
    unittest.main()
