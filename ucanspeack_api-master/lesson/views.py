from rest_framework import viewsets, status, generics, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from user.models.school import School
from .models import *
from .serializers import *
from rest_framework.decorators import action

from django.core.cache import cache
from django.db.models import Count, Q, F, Case, When, Value, IntegerField, BooleanField, ExpressionWrapper, Prefetch, Exists, OuterRef


class DictionaryItemFavoriteListAPIView(generics.ListAPIView):
    serializer_class = DictionaryItemSerializer

    def get_queryset(self):
        return (
            DictionaryItem.objects
            .filter(dictionaryitemfavorite__user=self.request.user)
            .annotate(is_favorite=Value(True, output_field=BooleanField()))
        )

class TariffsListAPIView(generics.ListAPIView):
    serializer_class = TariffSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return None
        is_pupil = School.objects.filter(pupils=self.request.user).exists()
        return Tariff.objects.filter(is_for_school=is_pupil)

class LessonItemFavoriteListAPIView(generics.ListAPIView):
    serializer_class = LessonItemFavoriteItemSerializer

    def get_queryset(self):
        return (
            LessonItem.objects
            .filter(lesson_item_favorites__user=self.request.user)
            .annotate(is_like=Value(True, output_field=BooleanField()))
        )

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = 'slug'
    http_method_names = ['get', 'head', 'options', 'post']
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        # Проверяем, залогинен ли пользователь
        if user.is_authenticated:
            cache_key = f'user_{user.id}_courses'
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

            # Для залогиненного пользователя - с прогрессом
            levels_qs = Level.objects.annotate(
                total_lessons=Count('lessons', distinct=True),
                done_lessons_count=Count(
                    'lessons__lessondone',
                    filter=Q(lessons__lessondone__user=user),
                    distinct=True
                ),
                progress=Case(
                    When(total_lessons=0, then=Value(0)),
                    default=ExpressionWrapper(
                        F('done_lessons_count') * 100 / F('total_lessons'),
                        output_field=IntegerField()
                    ),
                    output_field=IntegerField()
                ),
                is_done=Case(
                    When(total_lessons=0, then=Value(False)),
                    When(total_lessons=F('done_lessons_count'), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            ).order_by("order_num")

            courses = Course.objects.annotate(
                done_lessons_count=Count(
                    'levels__lessons__lessondone',
                    filter=Q(levels__lessons__lessondone__user=user),
                    distinct=True
                ),
                total_lessons=Count('levels__lessons', distinct=True),
                lessons_progress=Case(
                    When(total_lessons=0, then=Value(0)),
                    default=ExpressionWrapper(
                        F('done_lessons_count') * 100 / F('total_lessons'),
                        output_field=IntegerField()
                    ),
                    output_field=IntegerField()
                )
            ).prefetch_related(
                Prefetch('levels', queryset=levels_qs)
            )

            # материализуем для кеширования
            courses_list = list(courses)
            cache.set(cache_key, courses_list, timeout=300)
            return courses_list
        else:
            # Для незалогиненного пользователя - без прогресса
            levels_qs = Level.objects.annotate(
                total_lessons=Count('lessons', distinct=True),
                done_lessons_count=Value(0, output_field=IntegerField()),
                progress=Value(0, output_field=IntegerField()),
                is_done=Value(False, output_field=BooleanField())
            ).order_by("order_num")

            courses = Course.objects.annotate(
                done_lessons_count=Value(0, output_field=IntegerField()),
                total_lessons=Count('levels__lessons', distinct=True),
                lessons_progress=Value(0, output_field=IntegerField())
            ).prefetch_related(
                Prefetch('levels', queryset=levels_qs)
            )

        return courses


class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    lookup_field = 'slug'
    http_method_names = ['get', 'head', 'options', 'post']
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            cache_key = f'user_{user.id}_levels'
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        # ---------- Lessons queryset ----------
        if user.is_authenticated:
            lessons_qs = Lesson.objects.annotate(
                total_blocks=Count(
                    'modules__blocks',
                    filter=Q(modules__blocks__can_be_done=True),
                    distinct=True
                ),
                done_blocks=Count(
                    'modules__blocks__moduleblockdone',
                    filter=Q(
                        modules__blocks__moduleblockdone__user=user,
                        modules__blocks__can_be_done=True
                    ),
                    distinct=True
                ),
            ).annotate(
                progress=Case(
                    When(total_blocks=0, then=Value(0)),
                    default=ExpressionWrapper(
                        F('done_blocks') * 100 / F('total_blocks'),
                        output_field=IntegerField()
                    ),
                    output_field=IntegerField()
                ),
                is_done=Case(
                    When(total_blocks=0, then=Value(False)),
                    When(total_blocks=F('done_blocks'), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            ).order_by('order_num')
        else:
            lessons_qs = Lesson.objects.annotate(
                total_blocks=Count(
                    'modules__blocks',
                    filter=Q(modules__blocks__can_be_done=True),
                    distinct=True
                ),
                done_blocks=Value(0, output_field=IntegerField()),
                progress=Value(0, output_field=IntegerField()),
                is_done=Value(False, output_field=BooleanField())
            ).order_by('order_num')

        # Предзагрузка уроков с прогрессом
        levels = Level.objects.prefetch_related(
            Prefetch('lessons', queryset=lessons_qs)
        )

        # ---------- Levels queryset ----------
        if user.is_authenticated:
            levels = levels.annotate(
                total_lessons=Count('lessons', distinct=True),
                done_lessons=Count('lessons', filter=Q(lessons__modules__blocks__moduleblockdone__user=user),
                                   distinct=True),
            ).annotate(
                progress=Case(
                    When(total_lessons=0, then=Value(0)),
                    default=ExpressionWrapper(
                        F('done_lessons') * 100 / F('total_lessons'),
                        output_field=IntegerField()
                    ),
                    output_field=IntegerField()
                ),
                is_done=Case(
                    When(total_lessons=0, then=Value(False)),
                    When(total_lessons=F('done_lessons'), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )
        else:
            levels = levels.annotate(
                total_lessons=Count('lessons', distinct=True),
                done_lessons=Value(0, output_field=IntegerField()),
                progress=Value(0, output_field=IntegerField()),
                is_done=Value(False, output_field=BooleanField())
            )

        if user.is_authenticated:
            levels_list = list(levels)
            cache.set(cache_key, levels_list, timeout=300)
            return levels_list

        return levels


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    lookup_field = 'slug'
    http_method_names = ['get', 'head', 'options', 'post']
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'])
    def get_table(self, request, slug=None):
        """Возвращает HTML таблицы урока"""
        lesson = self.get_object()
        return Response({
            "slug": lesson.slug,
            "table": lesson.table
        })

    @action(detail=True, methods=['get'])
    def videos(self, request, slug=None):
        """Все видео урока с фразами"""
        lesson = self.get_object()
        all_videos = []

        # Проходим по модулям → блокам → видео
        for module in lesson.modules.all():
            for block in module.blocks.all():
                for video in block.videos.all():
                    all_videos.append(video)

        serializer = VideoSerializer(all_videos, many=True, context={"request": request})
        return Response(serializer.data)

    def get_queryset(self):

        user = self.request.user

        # ---------- DictionaryItem queryset ----------
        dictionary_items_qs = DictionaryItem.objects.all()

        if user.is_authenticated:
            favorites = DictionaryItemFavorite.objects.filter(
                user=user,
                dictionary_item=OuterRef("pk")
            )
            dictionary_items_qs = dictionary_items_qs.annotate(
                is_favorite=Exists(favorites)
            )
        else:
            dictionary_items_qs = dictionary_items_qs.annotate(
                is_favorite=Value(False, output_field=BooleanField())
            )

        # ---------- Modules queryset ----------
        if user.is_authenticated:
            modules_qs = Module.objects.annotate(
                total_blocks=Count(
                    'blocks',
                    filter=Q(blocks__can_be_done=True),
                    distinct=True
                ),
                done_blocks=Count(
                    'blocks__moduleblockdone',
                    filter=Q(
                        blocks__moduleblockdone__user=user,
                        blocks__can_be_done=True
                    ),
                    distinct=True
                )
            ).annotate(
                is_done=Case(
                    When(total_blocks=0, then=Value(False)),
                    When(total_blocks=F('done_blocks'), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            ).order_by('sorting')
        else:
            modules_qs = Module.objects.annotate(
                total_blocks=Count(
                    'blocks',
                    filter=Q(blocks__can_be_done=True),
                    distinct=True
                ),
                done_blocks=Value(0, output_field=IntegerField()),
                is_done=Value(False, output_field=BooleanField())
            ).order_by('sorting')

        # ---------- Lessons queryset ----------
        if user.is_authenticated:
            lessons_qs = Lesson.objects.annotate(
                total_blocks=Count(
                    'modules__blocks',
                    filter=Q(modules__blocks__can_be_done=True),
                    distinct=True
                ),
                done_blocks=Count(
                    'modules__blocks__moduleblockdone',
                    filter=Q(
                        modules__blocks__moduleblockdone__user=user,
                        modules__blocks__can_be_done=True
                    ),
                    distinct=True
                )
            ).annotate(
                progress=Case(
                    When(total_blocks=0, then=Value(0)),
                    default=F('done_blocks') * 100 / F('total_blocks'),
                    output_field=IntegerField()
                ),
                is_done=Case(
                    When(total_blocks=0, then=Value(False)),
                    When(total_blocks=F('done_blocks'), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            ).prefetch_related(
                Prefetch('modules', queryset=modules_qs),
                Prefetch(
                    'dictionary_groups__items',
                    queryset=dictionary_items_qs
                )
            )
        else:
            lessons_qs = Lesson.objects.annotate(
                total_blocks=Count(
                    'modules__blocks',
                    filter=Q(modules__blocks__can_be_done=True),
                    distinct=True
                ),
                done_blocks=Value(0, output_field=IntegerField()),
                progress=Value(0, output_field=IntegerField()),
                is_done=Value(False, output_field=BooleanField())
            ).prefetch_related(
                Prefetch('modules', queryset=modules_qs),
                Prefetch(
                    'dictionary_groups__items',
                    queryset=dictionary_items_qs
                )
            )

        return lessons_qs

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    lookup_field = 'id'
    http_method_names = ['get', 'head', 'options', 'post']
    permission_classes = [IsAuthenticatedOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        module = self.get_object()

        user = request.user

        module_id = module.id
        lesson_slug = module.lesson.slug
        level_slug = module.lesson.level.slug
        course_slug = module.lesson.level.course.slug

        last_url= f'/courses/{course_slug}/{level_slug}/{lesson_slug}?m_id={module_id}'
        if user.is_authenticated:
            user.last_lesson_url = last_url
            user.save(update_fields=['last_lesson_url'])

        serializer = self.get_serializer(
            module,
            context={"request": request}
        )


        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user

        # ---------- DictionaryItem queryset ----------
        dictionary_items_qs = DictionaryItem.objects.all()

        if user.is_authenticated:
            favorites = DictionaryItemFavorite.objects.filter(
                user=user,
                dictionary_item=OuterRef("pk")
            )
            dictionary_items_qs = dictionary_items_qs.annotate(
                is_favorite=Exists(favorites)
            )
        else:
            dictionary_items_qs = dictionary_items_qs.annotate(
                is_favorite=Value(False, output_field=BooleanField())
            )

        # ---------- LessonItem favorites ----------
        if user.is_authenticated:
            lesson_item_favorites_qs = LessonItemFavoriteItem.objects.filter(user=user)
        else:
            lesson_item_favorites_qs = LessonItemFavoriteItem.objects.none()

        # ---------- Module queryset ----------
        if user.is_authenticated:
            modules_qs = (
                Module.objects
                .annotate(
                    total_blocks=Count(
                        'blocks',
                        filter=Q(blocks__can_be_done=True),
                        distinct=True
                    ),
                    done_blocks=Count(
                        'blocks__moduleblockdone',
                        filter=Q(
                            blocks__moduleblockdone__user=user,
                            blocks__can_be_done=True
                        ),
                        distinct=True
                    ),
                )
                .annotate(
                    is_done=Case(
                        When(
                            total_blocks=F('done_blocks'),
                            total_blocks__gt=0,
                            then=True
                        ),
                        default=False,
                        output_field=BooleanField()
                    )
                )
                .prefetch_related(
                    Prefetch(
                        "module_dictionary_groups__items",
                        queryset=dictionary_items_qs
                    ),
                    Prefetch(
                        "blocks__items__lesson_item_favorites",
                        queryset=lesson_item_favorites_qs,
                        to_attr="user_favorites"
                    )
                )
            )
        else:
            modules_qs = (
                Module.objects
                .annotate(
                    total_blocks=Count(
                        'blocks',
                        filter=Q(blocks__can_be_done=True),
                        distinct=True
                    ),
                    done_blocks=Value(0, output_field=IntegerField()),
                    is_done=Value(False, output_field=BooleanField())
                )
                .prefetch_related(
                    Prefetch(
                        "module_dictionary_groups__items",
                        queryset=dictionary_items_qs
                    ),
                    Prefetch(
                        "blocks__items__lesson_item_favorites",
                        queryset=lesson_item_favorites_qs,
                        to_attr="user_favorites"
                    )
                )
            )

        return modules_qs


    @action(detail=False, methods=['post'], url_path='toggle_favorite', permission_classes=[IsAuthenticated])
    def toggle_favorite(self, request, id=None):
        user = request.user
        lesson_item_id = request.data.get('id')
        obj, created = LessonItemFavoriteItem.objects.get_or_create(
            user=user,
            lesson_item_id=lesson_item_id
        )
        if not created:
            obj.delete()
        return Response(status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'], url_path='toggle_block', permission_classes=[IsAuthenticated])
    def toggle_block(self, request, pk=None):
        user = request.user
        module_block_id = request.data.get('id')
        obj,created = ModuleBlockDone.objects.get_or_create(
           user=user,
           module_block_id=module_block_id
        )
        if not created:
           obj.delete()

        try:
            # Получаем урок и сразу считаем статистику
            from django.db.models import Count

            lesson_stats = ModuleBlock.objects.filter(
                id=module_block_id
            ).annotate(
                total_blocks=Count(
                    'module__lesson__modules__blocks',
                    filter=Q(module__lesson__modules__blocks__can_be_done=True)
                ),
                done_blocks=Count(
                    'module__lesson__modules__blocks__moduleblockdone',
                    filter=Q(
                        module__lesson__modules__blocks__moduleblockdone__user=user,
                        module__lesson__modules__blocks__can_be_done=True
                    )
                )
            ).values('module__lesson', 'total_blocks', 'done_blocks').first()

            if lesson_stats:
                lesson_id = lesson_stats['module__lesson']
                total_blocks = lesson_stats['total_blocks']
                done_blocks = lesson_stats['done_blocks']

                # Обновляем статус урока
                if total_blocks > 0 and done_blocks == total_blocks:
                    LessonDone.objects.get_or_create(
                        user=user,
                        lesson_id=lesson_id
                    )
                else:
                    LessonDone.objects.filter(
                        user=user,
                        lesson_id=lesson_id
                    ).delete()

        except Exception as e:
            # Логируем ошибку, но не прерываем выполнение
            print(f"Error updating lesson status: {e}")

        # Инвалидация кеша прогресса для этого юзера
        cache.delete_many([
            f'user_{user.id}_courses',
            f'user_{user.id}_levels',
        ])

        return Response(status=status.HTTP_200_OK)




class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @action(detail=True, methods=['post'], url_path='reorder_phrases',
            permission_classes=[permissions.IsAdminUser])
    def reorder_phrases(self, request, pk=None):
        """
        Body: {"ids": [3, 1, 2, 4]}
        Принимает список ID фраз в новом порядке.
        Все фразы должны принадлежать этому видео — иначе 400.
        """
        video = self.get_object()
        ids = request.data.get('ids', [])
        if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
            return Response({"detail": "ids должен быть списком целых чисел"},
                            status=status.HTTP_400_BAD_REQUEST)

        video_phrase_ids = set(video.phrases.values_list('id', flat=True))
        if set(ids) != video_phrase_ids:
            return Response({
                "detail": "Список ids должен содержать ровно все фразы этого видео"
            }, status=status.HTTP_400_BAD_REQUEST)

        cases = [When(id=phrase_id, then=Value(idx)) for idx, phrase_id in enumerate(ids)]
        Phrase.objects.filter(id__in=ids).update(
            order=Case(*cases, output_field=IntegerField())
        )

        return Response({"detail": "Порядок обновлён"}, status=status.HTTP_200_OK)


class PhraseViewSet(viewsets.ModelViewSet):
    queryset = Phrase.objects.all()
    serializer_class = PhraseSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class DictionaryGroupViewSet(viewsets.ModelViewSet):
    queryset = DictionaryGroup.objects.all()
    serializer_class = DictionaryGroupSerializer
    http_method_names = ['get', 'head', 'options', 'post']
    permission_classes = [IsAuthenticatedOrReadOnly]




class DictionaryItemViewSet(viewsets.ModelViewSet):
    queryset = DictionaryItem.objects.all()
    serializer_class = DictionaryItemSerializer
    lookup_field = 'id'
    http_method_names = ['get', 'head', 'options', 'post']
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = DictionaryItem.objects.all()

        if user.is_authenticated:
            favorites = DictionaryItemFavorite.objects.filter(
                user=user,
                dictionary_item=OuterRef("pk")
            )
            queryset = queryset.annotate(
                is_favorite=Exists(favorites)
            )
        else:
            queryset = queryset.annotate(
                is_favorite=models.Value(False, output_field=models.BooleanField())
            )

        return queryset

    @action(detail=True, methods=['post'], url_path='toggle_favorite', permission_classes=[IsAuthenticated])
    def toggle_favorite(self, request, id=None):
        user = request.user
        obj = self.get_object()
        obj, created = DictionaryItemFavorite.objects.get_or_create(
            user=user,
            dictionary_item=obj
        )
        if not created:
            obj.delete()
        return Response(status=status.HTTP_200_OK)


class ClearDictionaryFavoritesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        DictionaryItemFavorite.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_200_OK)


class ClearLessonItemFavoritesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        LessonItemFavoriteItem.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_200_OK)
