class Context(object):
    def __init__(self, url_root, path):
        self.url_root = url_root
        self.template_context = {}

        if path.startswith(self.url_root):
            trimmed_path = path[len(url_root):]
        else:
            trimmed_path = path

        if trimmed_path.endswith('/') or trimmed_path == '':
            template_path = trimmed_path + 'index.html'
        else:
            template_path = trimmed_path

        self.template_candidates = [template_path]
