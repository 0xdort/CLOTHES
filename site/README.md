# Fits Like (static site)

Plain HTML + JS, no build step beyond bundling the data:

    python3 tools/build_site.py      # data/ -> site/data.js
    cd site && python3 -m http.server 8000   # open http://localhost:8000

Everything runs in the browser; the reference fit is stored in localStorage.
