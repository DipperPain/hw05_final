import datetime as dt


def year(request):
    """Добавляет переменную с текущим годом."""
    year_now = dt.datetime.now().year
    context = {'year': year_now}
    if request:
        return context
    else:
        pass
