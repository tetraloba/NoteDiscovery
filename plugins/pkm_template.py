"""
PKM Template Plugin for NoteDiscovery

NoteDiscovery has Template system, however it doesn't have advanced features
(e.g. string replacement). So this Plugin compensate it.
"""

import logging
import re

import yaml
import markdown

logger = logging.getLogger('__name__')

class Plugin:
    def __init__(self):
        self.name = "PKM Template"
        self.version = "1.0.0"
        self.enabled = True

    def setup(self, ctx):
        """Swap the module logger for the per-plugin one the host provides."""
        global logger
        logger = ctx.logger

    def on_note_create(self, note_path: str, initial_content: str) -> str | None:
        md = markdown.Markdown(extensions=['meta'])
        html = md.convert(initial_content)

        # flatten Meta values
        for key in md.Meta.keys():
            if isinstance(md.Meta[key], list) and len(md.Meta[key]) == 1:
                md.Meta[key] = md.Meta[key][0]

        logging.debug(md.Meta)
        
        TITLE_FROM_FILENAME = r'^"\d{8}-\d{6}_(.*)"$'
        title_match = re.match(TITLE_FROM_FILENAME, md.Meta['title'])
        if title_match == None:
            logging.warning(f"the filename format ({md.Meta['title']}) is not supported.")
            return None
        md.Meta['title'] = title_match.groups()[0]
        new_yaml_text = yaml.safe_dump(md.Meta, allow_unicode=True, default_flow_style=False, sort_keys=False)
        return f"---\n{new_yaml_text}---\n" + '\n'.join(md.lines)

