# Сессия 7 — Endpoint «Выгнать ученика» для школьного администратора

Контекст: S1 + S1.5 + S2 + S3 + S4 + S6 + S5 уже выполнены. В S1 мы удалили небезопасный `POST /api/user/logout` который позволял любому авторизованному пользователю разлогинить любого другого. В S1.5 фронтовая кнопка «Выйти» в таблице учеников (`pages/profile/pupils.vue`) была заменена на заглушку-toast. Теперь делаем правильную реализацию.

Все пути — от родительской папки:
- `ucanspeack_api-master/` — Django бэк
- `ucanspeak_front-master/` — Nuxt фронт

Цели:
- Endpoint `POST /api/user/school-pupils/<id>/force_logout/` — удаляет все токены указанного ученика
- Проверка: вызывающий пользователь — владелец школы (`School.admin == request.user`), указанный ученик состоит в этой школе (`ученик in School.pupils`). Никаких других комбинаций быть не может.
- Фронт: убрать заглушку в `pupils.vue`, вернуть реальный вызов + toast «Ученик разлогинен»

Выполни 3 задачи последовательно.

---

## Задача 1 — action force_logout в SchoolPupilViewSet

Файл: `ucanspeack_api-master/user/services/school.py`.

Найди класс `SchoolPupilViewSet`. Добавь внутри него новый action (рядом с `destroy`):

```python
from rest_framework.decorators import action
# (если импорта ещё нет, добавь сверху файла)

# внутри класса SchoolPupilViewSet, рядом с destroy:
@action(detail=True, methods=['post'], url_path='force_logout')
def force_logout(self, request, pk=None):
    """
    Удаляет все активные токены указанного ученика.
    Доступно только владельцу школы, в которой этот ученик состоит.
    """
    from user.models import UserToken

    school = self.get_school(request)
    pupil = get_object_or_404(school.pupils, id=pk)

    deleted_count, _ = UserToken.objects.filter(user=pupil).delete()
    return Response({
        "detail": f"Ученик разлогинен. Удалено токенов: {deleted_count}"
    }, status=status.HTTP_200_OK)
```

Разбор безопасности:
- `self.get_school(request)` возвращает `School.objects.get(admin=request.user)` (или 404 если текущий юзер не админ школы). То есть школу берём именно **свою**, чужую взять нельзя.
- `get_object_or_404(school.pupils, id=pk)` — ищем ученика **в своей школе**. Если передать id чужого ученика — 404, потому что в `school.pupils` его нет.
- Удаляем токены этого ученика.

После этого — стандартный ресурсный маршрут DRF автоматически зарегистрирует этот action как `POST /api/user/school-pupils/<id>/force_logout/` (router уже есть в `user/urls.py`, ничего менять не нужно).

Проверь что в импортах файла присутствуют: `get_object_or_404`, `status`, `Response`, `action`. После предыдущих сессий большинство из них уже есть.

---

## Задача 2 — фронт repository: метод force_logout_pupil

Файл: `ucanspeak_front-master/app/repository/school/index.ts`.

Добавь в возвращаемый объект:

```typescript
force_logout_pupil(id: string | number) {
    return appFetch(`/api/user/school-pupils/${id}/force_logout/`, {
        method: 'POST'
    })
},
```

---

## Задача 3 — реальная кнопка выхода в pupils.vue

Файл: `ucanspeak_front-master/app/pages/profile/pupils.vue`.

Найди функцию `logout(data)` (после S1.5 она выдаёт info-toast «Временно недоступно»). Замени её реализацию целиком:

```typescript
async function logout(data) {
  loading.value = true
  try {
    await $api.school.force_logout_pupil(data.id)
    toast.add({
      severity: 'success',
      summary: 'Готово',
      detail: `Ученик ${data.full_name || data.email} разлогинен на всех устройствах`,
      life: 3000
    })
  } catch (e: any) {
    const detail = e?.data?.detail || 'Не удалось разлогинить ученика'
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail,
      life: 4000
    })
  } finally {
    loading.value = false
  }
}
```

(Логика с `loading.value` уже была в файле, просто возвращаем её на нормальный путь.)

---

## Финальная сводка

Выведи:
1. Список изменённых файлов
2. Подтверждение что миграции **не нужны**
3. **Чеклист ручной проверки:**
   - Залогиниться школьным админом (юзер с `is_school=True`)
   - Создать тестового ученика через `/profile/pupils`, добавить, получить его креды
   - В другом браузере (или инкогнито) залогиниться этим учеником
   - Вернуться в первый браузер школьного админа → `/profile/pupils` → кнопка «Выйти» (иконка pi-sign-out) напротив ученика → клик
   - Toast «Ученик разлогинен»
   - Проверить во втором браузере что следующий запрос к API возвращает 401 (ученик действительно разлогинен)
   - Попробовать через консоль браузера от имени обычного юзера (не школьного админа) сделать `fetch('/api/user/school-pupils/<любой_id>/force_logout/', {method: 'POST', ...})` — должен быть 403 или 404 (потому что школа не найдена у этого юзера)
4. Что НЕ сделано / отложено:
   - Rate-limiting на endpoint (злой школьный админ может разлогинить своих учеников бесконечно — но это не критичная угроза, одновременно ограничено `school.pupils` и максимум несколькими десятками людей)
