import reflex as rx

config = rx.Config(
    app_name="projeto_messianica",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)