# S1.10-LOGIN — Логин по login или email, страница «Восстановить пароль»

## Контекст

Сейчас на бэке юзер ищется только по `email`, но в модели `User` есть отдельное уникальное поле `login`. Клиент хочет:
- Юзер вводит login (или email — но об этом не пишем). Вход работает по обоим.
- На странице логина — ссылка «Восстановить пароль», ведёт на `/forgot-password`.
- Страница `/forgot-password` — форма с email, кнопка «Отправить» **ничего не делает** (заглушка до настройки SMTP).
- Тексты обновить: placeholder, label, нижний блок про регистрацию.

---

## Задача 1 — Бэкенд: общий хелпер поиска юзера

### `ucanspeack_api-master/user/utils.py` (создать новый файл если нет)

```python
"""Общие утилиты для приложения user."""
from django.contrib.auth import get_user_model


def find_user_by_login_or_email(value: str):
    """
    Ищет пользователя сначала по полю login, затем по email.
    Возвращает экземпляр User или None.

    Используется в:
    - CustomTokenCreateSerializer (логин)
    - ForceLoginView (выход отовсюду + вход)
    """
    if not value:
        return None

    User = get_user_model()
    value = value.strip()

    # Сначала ищем по login (точное совпадение, регистрозависимое)
    user = User.objects.filter(login=value).first()
    if user:
        return user

    # Потом по email (case-insensitive — email обычно нечувствителен)
    user = User.objects.filter(email__iexact=value).first()
    return user
```

Если файл `user/utils.py` уже существует — добавь функцию в конец файла.

---

## Задача 2 — Бэкенд: правка CustomTokenCreateSerializer

### `ucanspeack_api-master/user/serializers/auth.py`

В методе `validate()` найди блок:

**Было:**
```python
    def validate(self, attrs):
        login = attrs.get("login")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=login)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Пользователь не найден"})

        if not user.check_password(password):
            raise serializers.ValidationError({"detail": "Неверный пароль"})
```

**Станет:**
```python
    def validate(self, attrs):
        from user.utils import find_user_by_login_or_email

        login = attrs.get("login")
        password = attrs.get("password")

        user = find_user_by_login_or_email(login)
        if user is None:
            raise serializers.ValidationError({"detail": "Пользователь не найден"})

        if not user.check_password(password):
            raise serializers.ValidationError({"detail": "Неверный пароль"})
```

**Что важно:**
- Импорт хелпера — внутри функции (`from user.utils import ...`) чтобы не было циркулярных импортов между `serializers/auth.py` и `utils.py`.
- Остальная логика метода (проверка `max_logins`, `expires_at__lt`, `attrs["user"] = user`) **не меняется**.

---

## Задача 3 — Бэкенд: правка ForceLoginView

### `ucanspeack_api-master/user/views.py`

В классе `ForceLoginView.post()` найди блок:

**Было:**
```python
        User = get_user_model()
        try:
            user = User.objects.get(email=login)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден"}, status=400)
```

**Станет:**
```python
        from user.utils import find_user_by_login_or_email

        user = find_user_by_login_or_email(login)
        if user is None:
            return Response({"detail": "Пользователь не найден"}, status=400)
```

И **удали неиспользуемый импорт** `from django.contrib.auth import get_user_model` если он больше нигде в файле не используется (проверь grep'ом по файлу — если `get_user_model` встречается только тут, удаляй; если есть ещё — оставляй).

---

## Задача 4 — Фронт: правка формы логина

### `ucanspeak_front-master/app/components/Form/Login.vue`

**Правка 4.1 — placeholder и label поля логина**

Найди:
```vue
<UIInput fluid
         placeholder="Введите адрес почты или телефон"
         label="Email/Логин"
         id="email"
         v-model="form_data.login"/>
```

Замени на:
```vue
<UIInput fluid
         placeholder="Введите ваш логин"
         label="Логин"
         id="login"
         v-model="form_data.login"/>
```

**Правка 4.2 — добавить ссылку «Восстановить пароль» между кнопкой и текстом регистрации**

Найди блок:
```vue
<Button fluid
        class="mb-8"
        @click="login"
        :loading="loading"
        label="Войти" />
<p v-if="!school_auth">
  У вас нет аккаунта?
  <UILink label="Зарегистрируйтесь"
          link="#"
          @click.prevent="emits('change_form','register')"/>
  на нашей платформе и получите 7 дней пробного доступа ко всем урокам и разделам!
</p>
```

Замени на:
```vue
<Button fluid
        class="mb-4"
        @click="login"
        :loading="loading"
        label="Войти" />
<div class="text-center mb-6 w-full">
  <NuxtLink to="/forgot-password" class="text-sm text-[#7575F0] hover:underline">
    Восстановить пароль
  </NuxtLink>
</div>
<p v-if="!school_auth">
  У вас нет аккаунта?
  <UILink label="Зарегистрируйтесь"
          link="#"
          @click.prevent="emits('change_form','register')"/>
  на нашей платформе и получите 3 дня пробного доступа ко всем урокам и разделам!
</p>
```

**Что изменилось:**
- У кнопки `mb-8` → `mb-4` (отступ уменьшен — теперь между кнопкой и регистрацией стоит ещё одна ссылка).
- Добавлена ссылка `<NuxtLink to="/forgot-password">Восстановить пароль</NuxtLink>` в обёртке с центрированием и `mb-6`.
- В тексте «7 дней» → «3 дня».

**Правка 4.3 — watcher логина**

В `<script setup>` найди:
```ts
watch(
    () => form_data.value.login,
    (newEmail) => {
      form_data.value.login = newEmail.toLowerCase()
    }
)
```

Этот watcher принудительно приводит логин к нижнему регистру. Это **может ломать** вход юзеров с верхним регистром в логине (поле `login` в БД регистрозависимое). НО: убирать совсем — рискованно для юзеров которые сейчас входят по email с верхним регистром в начале.

**Оставляем как есть.** На бэке поиск по login — точное совпадение (case-sensitive), по email — `__iexact` (case-insensitive). Юзеру может прилететь «Пользователь не найден» если он завёл login с заглавной буквой и пытается войти со строчной. Это будет **известное поведение**, а не баг — обсудим если кто-то наткнётся.

---

## Задача 5 — Фронт: страница `/forgot-password`

### Создать новый файл `ucanspeak_front-master/app/pages/forgot-password.vue`

```vue
<script setup lang="ts">
definePageMeta({
  guest: true,
  layout: 'auth'
})

const email = ref('')
const sent = ref(false)
const loading = ref(false)

const handleSubmit = () => {
  // Заглушка: бэк-эндпоинт восстановления пароля будет реализован
  // отдельной задачей после настройки SMTP. Сейчас кнопка ничего не делает.
  // Намеренно НЕ показываем сообщение пользователю.
}
</script>

<template>
  <div class="pt-20 md:pt-0 md:h-[100vh] flex flex-col items-start justify-center">
    <CardBase padding="none" extra-class="w-full px-3 lg:px-[240px]">
      <div class="flex flex-col items-center justify-center py-4 md:py-10 md:p-[60px] w-full">

        <TypingText28 text="Восстановить пароль" class="mb-2"/>
        <p class="text-sm text-gray-500 text-center mb-6 max-w-md">
          Введите email, на который мы пришлём новый пароль.
        </p>

        <div class="space-y-3 w-full mb-6">
          <UIInput fluid
                   placeholder="your@mail.ru"
                   label="Email"
                   id="email"
                   v-model="email"/>
        </div>

        <Button fluid
                class="mb-4"
                @click="handleSubmit"
                :loading="loading"
                label="Отправить" />

        <p class="text-xs text-gray-500 text-center mb-6 max-w-md">
          Если вы ученик школы и у вас нет email — обратитесь к администратору вашей школы для смены пароля.
        </p>

        <div class="text-center w-full">
          <NuxtLink to="/login" class="text-sm text-[#7575F0] hover:underline">
            Вернуться ко входу
          </NuxtLink>
        </div>

      </div>
    </CardBase>
  </div>
</template>
```

**Замечания:**
- `definePageMeta({guest: true, layout: 'auth'})` — как у `/login`. Если в проекте middleware `guest` блокирует залогиненных — оно сюда тоже применится.
- Кнопка «Отправить» вызывает `handleSubmit` который **намеренно ничего не делает**. Никаких toast'ов, никаких изменений UI. Это бэклог для следующей задачи когда будет SMTP.
- Подсказка про учеников школы — мелким шрифтом снизу формы.
- Ссылка «Вернуться ко входу» ведёт на `/login`. **Проверь:** если у тебя страница логина по другому пути — например `/auth` или `/` — поправь `to="..."`. Поскольку `index.vue` файл находится в папке `app/pages/login/index.vue` (по структуре что ты прислал), маршрут — `/login`.

---

## Проверки после правок

**Бэк:**
1. `python manage.py check` проходит без ошибок.
2. Файл `user/utils.py` существует и содержит `find_user_by_login_or_email`.
3. `user/serializers/auth.py` использует хелпер вместо `User.objects.get(email=...)`.
4. `user/views.py` `ForceLoginView` использует хелпер вместо `User.objects.get(email=...)`.

**Фронт:**
5. `app/components/Form/Login.vue` placeholder = «Введите ваш логин», label = «Логин», текст про «3 дня».
6. На странице логина видна ссылка «Восстановить пароль» между кнопкой Войти и текстом регистрации.
7. Файл `app/pages/forgot-password.vue` создан, при переходе на `/forgot-password` отображается форма.
8. Клик по кнопке «Отправить» на `/forgot-password` ничего не делает (заглушка).

**Ручное тестирование после деплоя:**
9. Создать тестового юзера с заполненным полем `login` (например через Django admin: login=`test_user`, email=`test@test.ru`).
10. Войти под `test_user` + пароль → должен залогинить.
11. Войти под `test@test.ru` + пароль → должен залогинить.
12. Войти под `несуществующий` + пароль → должна быть ошибка «Пользователь не найден».
13. Превысить лимит сессий, войти ещё раз под `test_user` → диалог «Превышен лимит» → нажать «Выйти отовсюду и войти» → должен залогинить (раньше падал бы с «Пользователь не найден» т.к. force_login искал только по email).

## Не делать

- Не трогать форму регистрации `Form/Register.vue` — отдельная задача после утверждения с клиентом.
- Не создавать бэк-эндпоинт восстановления пароля.
- Не настраивать EMAIL_BACKEND, EMAIL_HOST и т.д. в settings.py.
- Не трогать `MultiTokenAuthentication`, `UserToken`, `SIMPLE_JWT`.
- Не менять формы регистрации, профиля, прогресса.
- Не пересобирать Docker / накатывать миграции (модели не менялись).
