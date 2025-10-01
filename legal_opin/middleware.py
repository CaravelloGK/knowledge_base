from datetime import datetime, timedelta


class SessionCleanupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Очищаем устаревшие данные сессии
        self.cleanup_old_session_data(request)

        return response

    def cleanup_old_session_data(self, request):
        """Очистка старых данных сессии"""
        cleanup_keys = ['legal_entity_data']

        for key in cleanup_keys:
            if key in request.session:
                # Можно добавить проверку на время создания данных
                # если храните timestamp в сессии
                data = request.session.get(key)
                if isinstance(data, dict) and 'timestamp' in data:
                    created_at = datetime.fromisoformat(data['timestamp'])
                    if datetime.now() - created_at > timedelta(hours=1):
                        del request.session[key]
                else:
                    # Если нет timestamp, удаляем при следующем запросе
                    del request.session[key]