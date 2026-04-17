def get_oficina(request):
    if request.user.is_authenticated:
        try:
            return request.user.perfilusuario.oficina
        except:
            return None
    return None