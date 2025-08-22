from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Generic

from fuzzyfinder.main import fuzzyfinder
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DataTable, Input, Static
from textual.widgets.data_table import CellType

if TYPE_CHECKING:
    from textual.widgets.data_table import ColumnKey, RowKey

STAR = ":star:"
NOT_STAR = ""


@dataclass
class Namespace:
    namespace: str
    cluster: str
    starred: bool = False


NamespaceKey = tuple[str, str]
DEFAULT_CSS = """
NamespaceList {
    color: $foreground;
    border: tall $primary;
    background: $surface;
    background-tint: $foreground 5%;
    margin-top: 1;

    & > .datatable--header {
        text-style: italic;
        background: $panel;
        color: $foreground;
    }
}

NamespacePicker > Container.top {
    background: $boost;
    height: 3;
}
NamespacePicker Input {
    width: 100%;
}
NamespacePicker DataTable {
    width: 100%;
    height: 100%;
}

.instructions {
    dock: bottom;
    height: 3;
    background: $boost;
    color: $foreground;
    content-align: center middle;
    text-style: italic;
}

.title {
    dock: top;
    height: 2;
    background: $boost;
    color: $primary;
    content-align: center middle;
    text-style: bold;
}
"""


class NamespaceList(DataTable, Generic[CellType]):
    """The list of namespaces."""

    namespace_filter = reactive("")
    can_focus = False

    def __init__(
        self,
        namespaces: list[Namespace],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.namespaces = namespaces
        self.namespaces_by_key: dict[NamespaceKey, Namespace] = {
            (ns.namespace, ns.cluster): ns for ns in namespaces
        }
        self._hidden_data: dict[RowKey, dict[ColumnKey, CellType]] = {}

    def default_sort(self) -> None:
        self.sort(
            self.star_column,
            self.namespace_column,
            key=lambda c: c[1] if not c[0] else f"1{c[1]}",
        )

    def on_mount(self) -> None:
        self.star_column = self.add_column(STAR)
        self.namespace_column = self.add_column("Namespace")
        self.add_column("Cluster")
        for ns in self.namespaces:
            self.add_row(
                STAR if ns.starred else NOT_STAR,
                ns.namespace,
                ns.cluster,
            )
        self.default_sort()

    async def watch_namespace_filter(self) -> None:
        """Watch for changes to the namespace filter."""
        all_data = self._data | self._hidden_data

        row_keys_to_display = (
            set(
                fuzzyfinder(
                    self.namespace_filter,
                    all_data.keys(),
                    accessor=lambda row_key: all_data[row_key][self.namespace_column],
                    sort_results=False,
                )
            )
            if self.namespace_filter
            else set(all_data.keys())
        )

        for row_key_to_hide in set(self._data.keys()) - row_keys_to_display:
            self._hidden_data[row_key_to_hide] = self._data[row_key_to_hide]
            self.remove_row(row_key_to_hide)

        for row_key_to_display in row_keys_to_display & set(self._hidden_data.keys()):
            self.add_row(*self._hidden_data[row_key_to_display].values())
            del self._hidden_data[row_key_to_display]
        self.default_sort()

    def toggle_star(self) -> None:
        """Handle the toggle star event."""
        current_row_key = self._row_locations.get_key(self.cursor_coordinate.row)
        if not current_row_key:
            return
        if self.get_cell(current_row_key, self.star_column) == STAR:
            self.update_cell(current_row_key, self.star_column, NOT_STAR)
        else:
            self.update_cell(current_row_key, self.star_column, STAR)

        _, namespace, cluster = self.get_row_at(self.cursor_coordinate.row)
        ns = self.namespaces_by_key[namespace, cluster]
        ns.starred = not ns.starred
        self.default_sort()


class NamespaceFilter(Input):
    """A filter input for the namespace list."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding(
            "down",
            "cursor_down",
            "Move cursor down",
            show=False,
        ),
        Binding(
            "up",
            "cursor_up",
            "Move cursor up",
            show=False,
        ),
        Binding("pageup", "page_up", "Page up", show=False),
        Binding("pagedown", "page_down", "Page down", show=False),
        Binding(
            "ctrl+s",
            "toggle_star",
            "Toggle star",
            tooltip="Mark the selected namespace as favorite.",
        ),
    ]

    class Down(Message):
        """Posted when the down key is pressed within an `Input`."""

    class Up(Message):
        """Posted when the up key is pressed within an `Input`."""

    class PageUp(Message):
        """Posted when the page up key is pressed within an `Input`."""

    class PageDown(Message):
        """Posted when the page down key is pressed within an `Input`."""

    class ToggleStar(Message):
        """Posted when toggle star is triggered."""

    def action_cursor_down(self) -> None:
        """Handle a cursor_down action."""
        self.post_message(self.Down())

    def action_cursor_up(self) -> None:
        """Handle a cursor_up action."""
        self.post_message(self.Up())

    def action_page_up(self) -> None:
        """Handle a page_up action."""
        self.post_message(self.PageUp())

    def action_page_down(self) -> None:
        """Handle a page_down action."""
        self.post_message(self.PageDown())

    def action_toggle_star(self) -> None:
        """Handle the toggle_star action."""
        self.post_message(self.ToggleStar())


class NamespacePicker(Widget):
    selected_namespace_row = reactive(0)

    def __init__(
        self,
        namespaces: list[Namespace],
        last_selected: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.namespaces = namespaces
        self.last_selected = last_selected

    def compose(self) -> ComposeResult:
        with Container(classes="top"):
            yield NamespaceFilter(placeholder="🔍 Type to filter namespaces...")
        with Container():
            yield NamespaceList(namespaces=self.namespaces, cursor_type="row")

    def on_mount(self) -> None:
        self.namespace_list = self.query_one(NamespaceList)
        if self.last_selected:
            self.namespace_filter = self.query_one(NamespaceFilter)
            self.namespace_filter.value = self.last_selected

    @on(NamespaceFilter.Down)
    async def handle_namespace_filter_down(self, message: NamespaceFilter.Down) -> None:
        """Handle the down key press in the namespace filter."""
        if self.selected_namespace_row < self.namespace_list.row_count - 1:
            self.selected_namespace_row += 1

    @on(NamespaceFilter.Up)
    async def handle_namespace_filter_up(self, message: NamespaceFilter.Up) -> None:
        """Handle the up key press in the namespace filter."""
        if self.selected_namespace_row > 0:
            self.selected_namespace_row -= 1

    @on(NamespaceFilter.PageUp)
    async def handle_namespace_filter_page_up(
        self, message: NamespaceFilter.PageUp
    ) -> None:
        """Handle the page up key press in the namespace filter."""
        self.namespace_list.action_page_up()

    @on(NamespaceFilter.PageDown)
    async def handle_namespace_filter_page_down(
        self, message: NamespaceFilter.PageDown
    ) -> None:
        """Handle the page down key press in the namespace filter."""
        self.namespace_list.action_page_down()

    def watch_selected_namespace_row(self) -> None:
        """Watch for changes to the selected namespace row."""
        self.namespace_list.move_cursor(row=self.selected_namespace_row)

    @on(NamespaceList.RowHighlighted)
    def handle_namespace_row_selected(
        self, message: NamespaceList.RowHighlighted
    ) -> None:
        """Handle the row selected event in the namespace list."""
        if self.selected_namespace_row != message.cursor_row:
            # always set to the highlighted row
            self.selected_namespace_row = message.cursor_row

    @on(NamespaceFilter.Changed)
    async def handle_namespace_filter_changed(
        self, message: NamespaceFilter.Changed
    ) -> None:
        """Handle the changed event in the namespace filter."""
        self.namespace_list.namespace_filter = message.value

    @on(NamespaceFilter.Submitted)
    async def handle_namespace_filter_submitted(
        self, message: NamespaceFilter.Submitted
    ) -> None:
        """Handle the submitted event in the namespace filter."""
        _, self.selected_namespace, self.selected_cluster = (
            self.namespace_list.get_row_at(self.namespace_list.cursor_coordinate.row)
        )

    @on(NamespaceFilter.ToggleStar)
    async def handle_namespace_filter_toggle_star(
        self, message: NamespaceFilter.ToggleStar
    ) -> None:
        """Handle the mark as favorite event in the namespace filter."""
        self.namespace_list.toggle_star()
        _, self.selected_namespace, self.selected_cluster = (
            self.namespace_list.get_row_at(self.namespace_list.cursor_coordinate.row)
        )


class OclApp(App):
    DEFAULT_CSS = DEFAULT_CSS
    ENABLE_COMMAND_PALETTE = False
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding(
            "escape",
            "quit",
            "Quit",
            tooltip="Quit the app and return to the command prompt.",
            priority=True,
        ),
    ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.namespaces: list[Namespace] = []
        self.selected_namespace: str = ""
        self.selected_cluster: str = ""
        self.last_selected: str = ""

    def compose(self) -> ComposeResult:
        yield Static("OpenShift Cluster Login", classes="title")
        yield NamespacePicker(self.namespaces, self.last_selected)
        yield Static(
            "↑/↓: Navigate • Enter: Select • Ctrl+S: Toggle Favorite • Esc: Quit",
            classes="instructions",
        )

    def on_mount(self) -> None:
        self.namespace_picker = self.query_one(NamespacePicker)

    @on(NamespaceFilter.Submitted)
    async def handle_namespace_filter_submitted(
        self, message: NamespaceFilter.Submitted
    ) -> None:
        self.selected_namespace = self.namespace_picker.selected_namespace
        self.selected_cluster = self.namespace_picker.selected_cluster
        await self.action_quit()


app = OclApp(watch_css=True, css_path=os.environ.get("OCL_CSS_PATH", None))

if __name__ == "__main__":
    app.run()
