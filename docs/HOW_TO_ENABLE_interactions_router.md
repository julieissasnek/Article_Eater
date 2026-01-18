# Enable the Interactions Router

In `app/main.py`, add:

```python
from .routes import interactions
app.include_router(interactions.router)
```