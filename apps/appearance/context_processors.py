from .services import get_active_appearance


def site_appearance(_request):
    return {"appearance": get_active_appearance(_request)}
