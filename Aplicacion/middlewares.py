# middlewares.py

class TemplateBaseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.groups.filter(name="GERENTE").exists():
                request.base_template = "base_gerente.html"
            elif request.user.groups.filter(name="ADMINISTRADOR").exists():
                request.base_template = "base_adm.html"
            elif request.user.groups.filter(name="INGENIERO").exists():
                request.base_template = "base_ing.html"
            # ... cualquier otra lógica para otros grupos
            else:
                request.base_template = "base.html"  # Un valor por defecto, si es necesario
        return self.get_response(request)
