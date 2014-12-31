from ..routing import MatchEverything
from werkzeug.routing import Rule as URLRule


class Extension(object):

    def __init__(self):
        self.context_extenders = []
        self.flask_blueprints = []
        self.url_generators = []

    def extendcontext(self, *args):

        if callable(args[0]):
            return self.extendcontext_always(*args)
        else:
            return self.extendcontext_with_pattern(*args)

    def extendcontext_always(self, func):
        rule = MatchEverything(endpoint=func)
        self.context_extenders.append(rule)
        return func


    def extendcontext_with_pattern(self, url_pattern):
        def url_pattern_rule(func):

            rule = URLRule(url_pattern, endpoint=func)
            self.context_extenders.append(rule)
            return func

        return url_pattern_rule

    def url_generator(self, func):
        self.url_generators.append(func)

    def add_flask_blueprints(self, func):
        self.flask_blueprints.append(func)
