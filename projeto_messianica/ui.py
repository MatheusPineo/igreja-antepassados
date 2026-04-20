import reflex as rx
from .models import Usuario, Antepassado
from .constants import TIPOS_USUARIO, IGREJAS, VINCULOS_ANTEPASSADOS, LINHAGENS, FAMILIAS

def renderizar_linha(antepassado: Antepassado, callback_edicao, callback_exclusao):
    return rx.table.row(
        rx.table.cell(antepassado.nome_completo),
        rx.table.cell(antepassado.vinculo),
        rx.table.cell(antepassado.linhagem),
        rx.table.cell(antepassado.familia),
        rx.table.cell(
            rx.hstack(
                rx.icon("pencil", size=18, cursor="pointer", on_click=lambda: callback_edicao(antepassado), color="blue"),
                rx.icon("trash-2", size=18, cursor="pointer", on_click=lambda: callback_exclusao(antepassado.id), color="red"),
            )
        ),
    )

def label_input(label, component):
    return rx.vstack(
        rx.text(label, size="1", weight="bold", color_scheme="gray", margin_bottom="-0.5em"),
        component, width="100%", spacing="2",
    )

def form_cadastro_antepassado(callback_submit, set_vinculo_func):
    return rx.form(
        rx.vstack(
            rx.input(name="nome_completo", placeholder="Nome do Espírito", width="100%"),
            rx.select(VINCULOS_ANTEPASSADOS, placeholder="Selecione o Vínculo", on_change=set_vinculo_func, width="100%"),
            rx.center(
                rx.vstack(
                    rx.text("Linhagem:", size="1", weight="bold"),
                    rx.radio(LINHAGENS, name="linhagem", direction="row", spacing="4", default_value="Paterna"),
                    align="center",
                ),
                width="100%"
            ),
            rx.center(
                rx.vstack(
                    rx.text("Pertence à:", size="1", weight="bold"),
                    rx.radio(FAMILIAS, name="familia", direction="row", spacing="4", default_value="Minha Família"),
                    align="center",
                ),
                width="100%"
            ),
            rx.button("Salvar Registro", type="submit", size="3", color_scheme="blue", width="100%", margin_top="1em"),
            spacing="4", align="center",
        ),
        on_submit=callback_submit, reset_on_submit=True, width="100%", max_width="480px",
    )
