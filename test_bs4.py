import sys
try:
    from bs4 import BeautifulSoup
    print('BeautifulSoup available')
except ImportError:
    print('BeautifulSoup not available')