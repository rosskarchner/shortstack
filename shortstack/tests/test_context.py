from ..context import Context

try:
    import unittest2 as unittest
except ImportError:
    import unittest



class TestContext(unittest.TestCase):
    def test_default_url_root(self):
        context = Context('/', '/index.html')
        candidate = context.template_candidates[0]
        self.assertEqual('index.html', candidate)

    def test_with_url_root(self):
        context = Context('/owning-a-home/', '/owning-a-home/learn-more/foo.html')
        candidate = context.template_candidates[0]
        self.assertEqual('learn-more/foo.html', candidate)

    def test_implied_index(self):
        context = Context('/', '/')
        candidate = context.template_candidates[0]
        self.assertEqual('index.html', candidate)

    def test_implied_index_subdirectory(self):
        context = Context('/', '/agents/')
        candidate = context.template_candidates[0]
        self.assertEqual('agents/index.html', candidate)
