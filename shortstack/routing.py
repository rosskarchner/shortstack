from werkzeug.routing import DEFAULT_CONVERTERS
from fnmatch import fnmatch

class MatchEverything():

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.map = None

    def match(self, path):
        return {}

    def bind(self, map):
        self.map=map

class SSMap(object):
    """
    Pretends to be a werkzeug.routing.map, and provides a 'multimatch'
    method that returns ALL matching rules (and their results).
    """

    strict_slashes = True
    default_subdomain = None
    host_matching = False
    converters = DEFAULT_CONVERTERS
    rules = []

    def __init__(self, rules=[]):
        for rule in rules:
            rule.bind(self)
            self.rules.append(rule)

    def multimatch(self, path):
        lookup = "|%s" % path
        matches = [(rule, rule.match(lookup)) for rule in self.rules]
        successful_matches = ((r, m) for r, m in matches if m is not None)
        return successful_matches
