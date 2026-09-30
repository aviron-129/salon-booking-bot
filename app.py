"""Entry point for hosts that start `app.py` / `main.py` by default."""
import asyncio

from bot.__main__ import main

if __name__ == "__main__":
    asyncio.run(main())
