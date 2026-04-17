from .utils import get_oficina

def oficina_context(request):
    return {'oficina_logada': get_oficina(request)}