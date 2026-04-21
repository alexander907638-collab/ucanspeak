# Сессия 1.5 — Дофикс после S1

Контекст: S1 уже выполнен. В нём были упущения, которые надо закрыть точечно.

Все пути — от родительской папки, где запущен Claude Code:
- `ucanspeack_api-master/` — Django бэк
- `ucanspeak_front-master/` — Nuxt фронт

Выполни 5 задач последовательно. После каждой — короткий отчёт. В конце — финальная сводка.

---

## Задача 1 — восстановить кнопку «Выгнать ученика» в pupils.vue

В S1 я попросил удалить метод `logout_user` из `app/repository/auth/index.ts` и заменить вызовы на TODO. Это сломало UX школьного админа: в файле `app/pages/profile/pupils.vue` есть DataTable со списком учеников с кнопкой `<Button icon="pi pi-sign-out" severity="warn" ... @click="logout(data)" />`. После S1 эта кнопка не работает (метод-заглушка).

Это легитимная фича: школьный админ должен иметь возможность освободить слот сессии для своего ученика (когда у того превышен лимит и он не может войти).

Решение для S1.5: временное. Метод-заглушку оставляем, но даём пользователю понятный UX:
- кнопка не должна молча ничего не делать
- при клике — toast с сообщением что фича временно недоступна

В будущем (отдельной сессией) сделаем настоящий endpoint `POST /api/user/school-pupils/<id>/logout/` с проверкой что школьный админ — владелец ученика.

Сделай:
1. В `ucanspeak_front-master/app/pages/profile/pupils.vue` найди функцию `logout(data)`. Перепиши её так:
   ```typescript
   async function logout(data) {
     toast.add({
       severity: 'info',
       summary: 'Временно недоступно',
       detail: 'Фича выгона ученика временно отключена. Будет восстановлена в ближайшем обновлении.',
       life: 4000
     })
   }
   ```
2. В `ucanspeak_front-master/app/repository/auth/index.ts` метод `logout_user` (заглушка которая там сейчас после S1) — оставь как есть, либо удали полностью, чтобы не висел мёртвый код. Если удаляешь — убедись что `pupils.vue` его не вызывает (после п.1 не вызывает).

Проверка: открыть `/profile/pupils`, нажать на иконку выхода у ученика — появляется info-toast.

---

## Задача 2 — реальный фикс аудио на тренажёре

В S1 я просил поправить `AudioFileSerializer` через `SerializerMethodField`, считая что фронт читает `audio_file.file` через относительный URL. Это было неполная диагностика.

Реальная причина: фронт в `app/pages/courses/trainer/[course_slug]/[level_slug]/[topic_slug]/index.vue` использует `:src="audio_file.mp3"` — поле `mp3` (URLField, для внешних URL, у клиента пустое), а не `file` (FileField с реальным mp3).

Изменения бэка из S1 (получение `file` через build_absolute_uri) — оставь, они правильные. Но нужна правка фронта, без неё аудио всё равно не играет.

Сделай:
1. В `ucanspeak_front-master/app/pages/courses/trainer/[course_slug]/[level_slug]/[topic_slug]/index.vue` найди две строки:
   - `:src="audio_file.mp3"` (около строки 208, в мобильном плеере)
   - `:src="current_audio?.mp3"` (около строки 302, в десктопном плеере)
   
   Замени `mp3` на `file` в обеих:
   - `:src="audio_file.file"`
   - `:src="current_audio?.file"`
2. Проверь что других мест с `audio_file.mp3` или `current_audio.mp3` в этом файле нет (`grep -n "\.mp3" <файл>`). Если есть — тоже замени. Если есть упоминания именно как имя файла (например, в alt-тексте или хедере) — не трогай, там это просто строка.

Проверка: открыть тренажёр, любой topic, кликнуть «Аудиоурок 1» — длительность подгружается, плеер играет.

---

## Задача 3 — нормальный фикс DictionaryItem

В S1 я просил поправить вёрстку «карточкой и обёрткой», но не видел реального DOM. Теперь видел.

Файл: `ucanspeak_front-master/app/components/Card/DictionaryItem.vue`.

Реальная корневая причина: на родительской обёртке стоит `inline-flex` (контент задаёт ширину, родитель не ограничивает), плюс при `opened === true` появляется `<div class="absolute right-0 bottom-0">` с переводом — этот блок позиционируется относительно `inline-flex` родителя, который шире чем сама карточка → блок налезает на соседние элементы списка.

Сделай:
1. Открой файл, замени блок `<template>` на следующую структуру (сохраняя props, emits, классы которые уже работают для нормальной длины):

```vue
<template>
  <div class="w-full">
    <div class="relative flex items-start gap-4 w-full" :class="opened ? 'min-h-[85px]' : ''">
      <Checkbox v-model="checked" binary class="shrink-0 mt-1" />
      <div class="bg-[#EFEFF5] hover:bg-[#e9e9e9] overflow-hidden p-2.5 rounded-lg flex-1 min-w-0 max-w-full">
        <div @click="emits('toggle_open', item.id)" class="flex items-center select-none gap-3">
          <div @click="play" class="flex flex-grow items-center gap-[3px] cursor-pointer min-w-0">
            <div class="text-base leading-[130%] break-words min-w-0">
              <span v-if="opened">{{dictionary_direction === 'ruEN' ?  item.text_ru :item.text_en}}</span>
              <span v-else>{{dictionary_direction === 'ruEN' ?  item.text_ru :item.text_en}}</span>
            </div>
          </div>
          <UILikeBtn v-if="user" :class="loading ? 'disabled opacity-50' : ''" @click.stop="emits('toggle_fav',item.id)" v-model:value="item.is_favorite" class="shrink-0" />
        </div>
        <div v-if="opened" class="mt-2 bg-[#7575F0] p-2.5 rounded-lg w-full">
          <p class="text-base text-right leading-[130%] tracking-[-0.01em] text-white break-words">
            {{dictionary_direction === 'ruEN' ?  item.text_en :item.text_ru}}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
```

Что изменилось:
- Корневой `<div class="">` → `<div class="w-full">` (карточка занимает доступную ширину родителя, не сжимается под текст)
- `inline-flex` → `flex` + `w-full`
- На блоке-обёртке (`bg-[#EFEFF5]`) добавлены `flex-1 min-w-0 max-w-full` (без `min-w-0` flex-child не ужимается ниже размера контента)
- На текст добавлены `break-words min-w-0` (длинные слова переносятся)
- Блок перевода (`v-if="opened"`) перенесён из `absolute` в **обычный поток ниже текста** — больше не выпрыгивает за границы карточки
- `h-[85px]` → `min-h-[85px]` (иначе при двух строках перевода контент обрежется)

Проверка: открыть страницу урока со словарной группой, найти длинную фразу типа «шутить, разыгрывать», кликнуть на неё — карточка раскрывается вниз, перевод не налезает на соседние слова.

---

## Задача 4 — full_name при регистрации

Баг: фронт в `Register.vue` отправляет поле `full_name`, бэк в `UserCreateSerializer` его игнорирует. Юзеры регистрируются без имени.

Файл: `ucanspeack_api-master/user/serializers/create.py`.

Сделай:
1. В `UserCreateSerializer.Meta.fields` добавь `'full_name'`. Должно стать:
   ```python
   fields = tuple(User.REQUIRED_FIELDS) + (
       'email',
       'is_school',
       'full_name',
       'password',
   )
   ```
2. Поле `full_name` уже есть на модели User (`CharField(max_length=255, blank=True, null=True)`), миграции не нужны.

Проверка: зарегистрировать нового юзера через `Register.vue`, ввести ФИО → после регистрации в админке `/admin/user/user/<id>/change/` поле «ФИО» заполнено.

---

## Задача 5 — почистить логи и мёртвый код, который я недокинул в S1

Это довески, разные файлы. Идут одним списком потому что мелкие.

1. Файл `ucanspeak_front-master/app/middleware/auth.global.ts` — удали `console.log(to);` (строка 2, мусор в консоли).
2. Файл `ucanspeak_front-master/app/components/Block/VideoWithPreview.vue` — найди и удали `console.log(props.data.file)` в `onMounted`.
3. Файл `ucanspeack_api-master/lesson/serializers.py` — в `VideoSerializer.get_file` удали строку `print(request.build_absolute_uri(obj.file.url))` (логирует на каждый запрос видео, мусор в stdout продакшна).
4. Файл `ucanspeack_api-master/user/services/school.py` — в методе `list` удали `print(serializer.data[0] if serializer.data else 'empty')`.
5. Файл `ucanspeack_api-master/user/models/user.py` — в `user_post_save` удали `print('created')`.
6. Файл `ucanspeak_front-master/app/pages/profile/pupils.vue` — функция `openEditDialog`, удали `console.log(pupil) // смотрим что приходит` (строка 41).
7. Файл `ucanspeak_front-master/app/pages/courses/trainer/[course_slug]/[level_slug]/[topic_slug]/index.vue` — в `handleToggleFav` удали `console.log('sdf', id)`.

Все остальные `console.log` оставь — не трогай, есть риск удалить нужное (например, отладочное сообщение которое автор поставил намеренно).

---

## Финальная сводка

Выведи:
1. Список изменённых файлов
2. Подтверждение что миграции **не нужны** (мы только меняли логику и сериализаторы, моделей не трогали)
3. Чеклист ручной проверки:
   - `/profile/pupils` — клик по иконке «Выгнать» → info-toast «Временно недоступно»
   - Тренажёр любой topic, вкладка «Аудиоурок 1» → плеер играет, длительность отображается
   - Урок с длинной фразой в словаре («шутить, разыгрывать») — карточка не налезает на соседей
   - Регистрация нового юзера с ФИО → в админке у юзера ФИО заполнено
   - В консоли браузера на главных страницах — нет `console.log(to)` и `sdf`
