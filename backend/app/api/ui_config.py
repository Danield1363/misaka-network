from fastapi import APIRouter

router = APIRouter()


@router.get("/ui-config")
async def get_ui_config() -> dict[str, str]:
    return {
        "theme": "misaka-hud",
        "primary_color": "#68d5ff",
        "secondary_color": "#7a7dff",
        "accent_color": "#b38cff",
        "background": "#081018",
        "panel_style": "glass",
        "animation_level": "medium"
    }