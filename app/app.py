import reflex as rx

from app.components.account_section import (
    account_category_section,
)
from app.components.header import header_component
from app.components.net_worth_graph import (
    net_worth_graph_component,
)
from app.components.net_worth_summary import (
    net_worth_summary,
)
from app.components.sidebar import sidebar
from app.components.summary_section import summary_section
from app.states.account_state import AccountState


def index() -> rx.Component:
    """The main page of the financial dashboard."""
    return rx.el.div(
        sidebar(),
        rx.el.main(
            # Pannello di controllo database
            rx.cond(
                ~AccountState.db_state.is_connected & AccountState.use_database,
                rx.el.div(
                    rx.el.div(
                        rx.text("⚠️ Database non connesso", class_name="text-orange-600 font-medium"),
                        rx.text(AccountState.db_state.error_message, class_name="text-sm text-gray-600"),
                        rx.button(
                            "Riprova connessione",
                            on_click=AccountState.initialize_app,
                            class_name="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                        ),
                        rx.button(
                            "Usa dati simulati",
                            on_click=AccountState.toggle_database_mode,
                            class_name="mt-2 ml-2 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                        ),
                        class_name="p-4 bg-orange-50 border border-orange-200 rounded-lg"
                    ),
                    class_name="mb-4"
                )
            ),
            header_component(),
            net_worth_summary(),
            net_worth_graph_component(),
            rx.el.div(
                rx.el.div(
                    rx.foreach(
                        AccountState.account_categories,
                        account_category_section,
                    ),
                    class_name="flex-grow pr-0 lg:pr-8 mb-8 lg:mb-0",
                ),
                rx.el.div(
                    summary_section(),
                    class_name="w-full lg:w-80 flex-shrink-0",
                ),
                class_name="flex flex-col lg:flex-row",
            ),
            rx.toast.provider(),
            class_name="p-8 flex flex-col w-full min-h-[100vh] overflow-y-auto",
        ),
        class_name="flex flex-row bg-gray-50 min-h-screen w-full",
    )


app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=False,
        radius="medium",
        accent_color="indigo",
    )
)

# Inizializza il database al caricamento dell'app
def on_load():
    """Funzione chiamata al caricamento dell'app.""" 
    return AccountState.initialize_app

app.add_page(index, title="Accounts Dashboard", on_load=on_load)
