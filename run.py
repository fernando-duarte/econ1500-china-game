#!/usr/bin/env python
"""
Run script for the China Growth Game API.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("china_growth_game.app:app", host="0.0.0.0", port=8000, reload=True)
