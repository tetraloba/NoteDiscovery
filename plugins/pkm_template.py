"""
PKM Template Plugin for NoteDiscovery

NoteDiscovery has Template system, however it doesn't have advanced features
(e.g. string replacement). So this Plugin compensate it.
"""

import logging
from os import path
import copy
import re
from datetime import datetime

import yaml
import markdown

logger = logging.getLogger('__name__')

# to format Front Matter
class QuotedStr(str):
    pass
class Title(QuotedStr):
    pass
# customize PyYAML dumper
class CustomDumper(yaml.Dumper):
    # enforce indent (avoid list indentless style)
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)
# force double quotes ("") for QuotedStr (include inheritance)
yaml.add_multi_representer(
    QuotedStr,
    lambda dumper, data: dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"'),
    Dumper=CustomDumper
)
# force isoformat for datetime
yaml.add_representer(
    datetime,
    lambda dumper, data: dumper.represent_scalar('tag:yaml.org,2002:timestamp', data.isoformat()),
    Dumper=CustomDumper
)

class Plugin:
    def __init__(self):
        self.name = "PKM Template"
        self.version = "1.0.0"
        self.enabled = True
    def setup(self, ctx):
        """Swap the module logger for the per-plugin one the host provides."""
        global logger
        logger = ctx.logger
    def _format_note():
        pass
    def on_note_create(self, note_path: str, initial_content: str) -> str | None:
        md = markdown.Markdown(extensions=['meta'])
        _ = md.convert(initial_content)
        # header
        # header / title
        TITLE_FROM_FILENAME = r'^\d{8}-\d{6}_(.*)\.md$'
        filename = path.basename(note_path)
        title_match = re.match(TITLE_FROM_FILENAME, filename)
        if title_match == None:
            logging.warning(f"the filename format ({filename}) is not supported.")
            return None
        md.Meta['title'] = Title(title_match.groups()[0])
        # header / created and updated
        dt_now = datetime.now()
        md.Meta['created'] = dt_now
        md.Meta['updated'] = copy.copy(dt_now) # to avoid YAML Anchor
        header = yaml.dump(md.Meta, Dumper=CustomDumper, allow_unicode=True, sort_keys=False)
        # body
        if 'lines' in md.__dict__.keys():
            logger.debug('md has lines.')
            body = '\n'.join(md.lines)
        else:
            logger.debug('md doesn\'t have lines.')
            body = '\n'
        # dump
        return f"---\n{header}---\n" + body
