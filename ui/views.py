# ui/views.py
from discord.ui import View

class TimedView(View):
    """View with timeout that disables all components"""
    def __init__(self, timeout=300):
        super().__init__(timeout=timeout)
        self.message = None
    
    async def on_timeout(self):
        """Disable all buttons and selects when timeout occurs"""
        for item in self.children:
            item.disabled = True
        
        if self.message:
            try:
                await self.message.edit(view=self)
            except:
                pass