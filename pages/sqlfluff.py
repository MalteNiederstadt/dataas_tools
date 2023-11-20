import streamlit as st
import difflib
from streamlit.components.v1 import html
import base64
import gzip

from sqlfluff.api import fix, lint




def sql_encode(data: str) -> str:
    """Gzip and base-64 encode a string."""
    return base64.urlsafe_b64encode(gzip.compress(data.encode())).decode()


def sql_decode(data: str) -> str:
    """Gzip and base-64 decode a string."""
    return gzip.decompress(base64.urlsafe_b64decode(data.encode())).decode()



def fluff_results(sql_code):
    """Serve the results page."""
    # we get carriage returns from the form somehow. so split on them and join via
    # regular newline. add a newline to avoid the annoying newline-at-end-of-file error.
    sql = sql_decode(sql_code).strip()
    sql = "\n".join(sql.splitlines()) + "\n"

    dialect = 'bigquery'
    linted = lint(sql, dialect=dialect)
    fixed_sql = fix(sql, dialect=dialect)
    return fixed_sql




col1, col2 = st.columns(2)

with col1:
    st.caption('Your awful SQL')
    code1 = sql_encode(st.text_area(label='code input',height=500, label_visibility='hidden'))

fluffed = fluff_results(code1)

if fluffed == '':
    fluffed = '\n ‎' * 25

with col2:
    st.caption("Pretty isn't it?")
    output = st.code(fluffed, language='sql', line_numbers = True)




