# Setup guide PDFs (25 Nov 2026)

Source for the PDFs in /guides/setup/ and the personalised copies Taj sends before a call.

    python3 build.py <guide> [people/<person>.json] [out.pdf]
    guide: getting-paid | clients-across | studio-setup | coaching

A person file fills in {{keys}} (for_name, title, lede, forme, plan_now and so on, see DEFAULTS in build.py).
Keep person files out of this repo (customer details). Rules: detailed but simple, accurate to the app, no upselling.
After changing a general guide, rebuild it and copy it into /guides/setup/ with the same file name.
