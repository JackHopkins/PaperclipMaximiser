import time

from rich.console import Console
from rich.table import Table
from rich.traceback import install


class MCTSDebugger:
    def __init__(self):
        self.console = Console()
        self.start_times = {}
        install(show_locals=True)  # Better traceback formatting

    def create_timing_table(self, group_id: int, timing_data: dict) -> Table:
        table = Table(title=f"Group {group_id} Timing Breakdown")
        table.add_column("Operation", style="cyan")
        table.add_column("Duration (s)", justify="right", style="green")

        for operation, duration in timing_data.items():
            table.add_row(operation, f"{duration:.3f}")

        return table

    async def trace_operation(self, name: str, group_id: int, func, *args, **kwargs):
        """Trace an async operation with rich output"""
        start = time.time()
        self.console.print(f"[cyan]Starting {name} for group {group_id}...[/cyan]")

        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start
            self.console.print(f"[green]Completed {name} for group {group_id} in {duration:.3f}s[/green]")
            return result, duration
        except Exception as e:
            duration = time.time() - start
            self.console.print(f"[red]Error in {name} for group {group_id} after {duration:.3f}s: {str(e)}[/red]")
            raise