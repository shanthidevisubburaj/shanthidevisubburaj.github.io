AUTHOR = 'Raja CSP Raman'
SITENAME = 'RajaCSP'
SITETITLE = 'RajaCSP'
SITEURL = ""
PATH = "content"
TIMEZONE = 'America/Moncton'
DEFAULT_LANG = 'en'
THEME = 'theme'

# Disable URL hash fragments in article links
DISABLE_URL_HASH = True

# Copyright
COPYRIGHT_YEAR = 2026
COPYRIGHT_NAME = 'Raja CSP Raman'

# Dark mode support
THEME_COLOR_AUTO_DETECT_BROWSER_PREFERENCE = True
THEME_COLOR_ENABLE_USER_OVERRIDE = True

# Syntax highlighting
PYGMENTS_STYLE = 'github'  # Light mode
PYGMENTS_STYLE_DARK = 'native'  # Dark mode

# Static files
STATIC_PATHS = ['images']
SITELOGO = '/images/csp.jpeg'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Pages
DISPLAY_PAGES_ON_MENU = True

# Social widget
SOCIAL = (
    ("github", "https://github.com/rajacsp"),
    ("linkedin", "https://www.linkedin.com/in/raja-csp-raman/"),
    ("substack", "https://articlevil.substack.com/"),
    ("python", "https://rajacsp.github.io/mlnotes/"),
)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
