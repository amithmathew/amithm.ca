# Configuration variables for PyJello

OUTPUT_DIR = 'output'
STATIC_DIRS = ['static']
STATIC_INDEX = True
INDEX_FILE = 'static/index.html'
COMMON_TEMPLATES = 'templates/common'
BACKUP_ROOT = "backup"
DEFAULT_POSTDATE_FORMAT = "%B %d, %Y"  # strftime format
DEFAULT_AUTHOR = ["Amith Mathew"]
DEFAULT_CATEGORY = ['Random']
SITE_URL = "http://amithm.ca"
MARKDOWN_EXTENSIONS = ['markdown.extensions.abbr',
                       'markdown.extensions.def_list',
                       'markdown.extensions.fenced_code',
                       'markdown.extensions.footnotes',
                       'markdown.extensions.tables',
                       'markdown.extensions.meta',
                       'markdown.extensions.nl2br',
                       'markdown.extensions.smarty',
                       'markdown.extensions.toc',
                       ]
                       
# any regex to ignore while parsing directories.
PYJELLO_IGNORE = ['^#', '#$', '.*\~$', '\~$', '\.DS_Store']

CONTENT_MAPPING = {
    'blog': {'content': 'content/blog',
             'output': 'output/blog',
             'templates': 'templates/blog'
             },
    'stories': {'content': 'content/stories',
                'output': 'output/stories',
                'templates': 'templates/stories'
                },
    'projects': {'content': 'content/projects',
                 'output': 'output/projects',
                 'templates': 'templates/projects'
                 }
}