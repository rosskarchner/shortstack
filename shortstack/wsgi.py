import os
import itertools


import flask
from jinja2.loaders import FileSystemLoader

from .views import handle_request
from .filesystem import relative_urls_from_filesystem
from .routing import SSMap
from .url_manipulation import path_in_patterns, prepend_url
from .utility import build_search_path
from .config import configuration
from .extensions.loader import load_extensions


DEFAULT_IGNORE = ['_layouts/*', '_settings/*']


class Shortstack(flask.Flask):

    def __init__(self, *args, **kwargs):
        self.url_root = kwargs.pop('url_root', '/')
        assert self.url_root.startswith('/'), "url_root must start with slash"
        assert self.url_root.endswith('/'), "url_root must end with slash"

        # This helps us take the url_root into account
        # when translating URL paths to the filesystem
        self.trim_from_paths = len(self.url_root) - 1

        extensions_invoked_with = kwargs.pop('extensions')

        super(Shortstack, self).__init__(*args, **kwargs)

        extensions_config = self.get_configuration('extensions', optional=True)  or []
        extensions_names = extensions_config + extensions_invoked_with

        os.environ['SS_ROOT_DIR'] = kwargs['instance_path']
        self.ss_extensions = load_extensions(extensions_names)

        rules = []
        for ext in self.ss_extensions:
            for rule in ext.context_extenders:
                rules.append(rule)

            for blueprint_func in ext.flask_blueprints:
                self.register_blueprints_from_dict(blueprint_func())


        self.context_map = SSMap(rules)
        template_search_path = [self.join_path('_layouts'),
                                self.join_path('_includes')]

        @self.errorhandler(404)
        def _(e):
            return handle_request()

    @property
    def jinja_loader(self, *args, **kwargs):
        request = flask.request
        search_path = build_search_path(self.instance_path,
                                        request.path,
                                        append=['_layouts', '_includes'],
                                        include_start_directory=True)

        return FileSystemLoader(search_path)

        try:
            with self.open_instance_resource('.ssignore') as ignorefile:
                self.ignore_patterns = [l.strip() for l in ignorefile]
        except IOError:
            self.ignore_patterns = []


    def register_blueprints_from_dict(self, blueprints):
        for key, value in blueprints.iteritems():
            package = value['package']
            module = value['module']

            # Using a less elegant way of doing dynamic imports to support 2.6
            try:
                blueprint = __import__(package, fromlist=[module])
            except ImportError:
                print "Error importing package {0}".format(key)
                continue
            self.register_blueprint(getattr(blueprint, module))

    def get_configuration(self, config_name, optional=False):
        return configuration(config_name, config_directory=self.join_path('_settings'), optional=optional)

    def should_ignore_path(self, path):
        ignore_patterns = itertools.chain(DEFAULT_IGNORE, self.ignore_patterns)
        stripped_path = path[self.trim_from_paths + 1:]
        return path_in_patterns(ignore_patterns, stripped_path)

    def filtered_urls_from_filesystem(self):
        unfiltered = relative_urls_from_filesystem(
            self.instance_path, self.url_root)
        return (url for url in unfiltered if not self.should_ignore_path(url))

    def join_path(self, relative_path):
        if relative_path.startswith('/'):
            relative_path = relative_path[1:]
        return flask.safe_join(self.instance_path, relative_path)

    def trim_path(self, path):
        if path.startswith(self.url_root):
            return path[self.trim_from_paths:]
        else:
            return path

    def filesystem_path_for_request(self):
        trimmed = self.trim_path(flask.request.path)

        if trimmed.endswith('/'):
            trimmed += ('index.html')

        translated_path = self.join_path(trimmed)
        return translated_path

    def build_search_path(self, *args, **kwargs):
        return build_search_path(self.instance_path, *args, **kwargs)

    def dispatch_request(self):
        prepared_url = prepend_url(self.url_root,flask.request.path)
        if prepared_url != flask.request.path:
            return flask.redirect(prepared_url)
        super(Shortstack, self).dispatch_request()
