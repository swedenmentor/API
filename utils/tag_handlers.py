from bs4.element import Tag
import re
from urllib.parse import urljoin

def clean_text(text: str) -> str:
    """Function for light text cleaning, like removing consecutive space or line breaks.
    """
    cleaned = re.sub('\n{3,}', '\n', text)
    cleaned = re.sub(r' {3,}', ' ', cleaned)
    return cleaned


def handle_table(elm: Tag) -> str:
    """Function to handle table Tag object produced by BeautifulSoup
    For example, a table with the following form
    | col1 | col 2|
    |------|------|
    | val1 | val2 |

    will be represented as '\ncol1 - col2\nval1 - val2\n

    Parameters
    ----------
    elm : Tag
        the table tag

    Returns
    -------
    str
        A string represent the table
    """

    if elm.name == 'table':
        rows_elm: list[Tag] = elm.find_all('tr')

        table = []
        table_str = '\n'

        for row in rows_elm:
            row_values = row.find_all(['td', 'th'])
            table.append(tuple(val.text for val in row_values))
            table_str += ' - '.join([clean_text(val.text) for val in row_values]) + ';\n'
        return table_str

    else:
        return None


def handle_list(elm: Tag) -> str:
    """Function to handle list Tag objects produced by BeautifulSOup
    For example, a list with the following form:
    - item 1
    - item 2
    will be represented as '\n- item1\n- item2'

    Parameters
    ----------
    elm : Tag
        A list Tag

    Returns
    -------
    str
    """
    if elm.name in ['ol', 'ul']:
        list_items = elm.find_all('li')
        list_str = ''
        for item in list_items:
            list_str += '- ' + clean_text(item.text) + '\n'
        return list_str
    else:
        return None

# def join_url(*args):
#     def join_slash(a: str, b: str):
#         return a.rstrip('/') + '/' + b.lstrip('/')
#     return reduce(join_slash, args) if args else ''



def handle_url(elm: Tag, base_url: str = '') -> str:
    """Function to handle URL with link text.
    
    For example, an 'a' tag in this form:
    <a href="https://example.com">Link text</a>
    
    will be converted to [Link text](https://example.com)


    Parameters
    ----------
    elm : Tag
        The 'a' tag object produced by BeautifulSoup
    base_url : str
        In case the link in a website is only the relative path (instead of a full URL),
        provide this to make the full path.

    Returns
    -------
    str
        
    """
    elm_text = clean_text(elm.text).strip(' \r\n')
    
    if elm.name == 'a' and elm.has_attr('href'):
        if elm['href'].startswith('http'):
            url_str = f"[{elm_text}]({elm['href']})"
        else:
            url_str = f"[{elm_text}]({urljoin(base_url, elm['href'])})"
        return url_str
    else:
        return None

