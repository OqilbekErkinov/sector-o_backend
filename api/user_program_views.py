from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .auth_views import get_user_lang
from .models import UserProgram, UserProgramDay, UserProgramExercise, Program
from .serializers import UserProgramSerializer


def _localized_name(obj, lang):
    return getattr(obj, f'name_{lang}', '') or obj.name_en or obj.name_uz or ''


class UserProgramListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        programs = UserProgram.objects.filter(user=request.user).prefetch_related('days__exercises')
        return Response(UserProgramSerializer(programs, many=True).data)

    def post(self, request):
        serializer = UserProgramSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)


class UserProgramDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        return UserProgram.objects.filter(pk=pk, user=request.user).first()

    def patch(self, request, pk):
        instance = self.get_object(request, pk)
        if not instance:
            return Response({'error': 'Not found'}, status=404)
        serializer = UserProgramSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        instance = self.get_object(request, pk)
        if not instance:
            return Response({'error': 'Not found'}, status=404)
        instance.delete()
        return Response(status=204)


class UserProgramActivateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        instance = UserProgram.objects.filter(pk=pk, user=request.user).first()
        if not instance:
            return Response({'error': 'Not found'}, status=404)
        # Only one active program per user — enforced here rather than with
        # a model constraint/signal, since this is the only place a program
        # ever becomes active.
        UserProgram.objects.filter(user=request.user).exclude(pk=pk).update(is_active=False)
        instance.is_active = True
        instance.save(update_fields=['is_active'])
        return Response(UserProgramSerializer(instance).data)


class ActiveUserProgramView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        instance = UserProgram.objects.filter(
            user=request.user, is_active=True
        ).prefetch_related('days__exercises').first()
        if not instance:
            return Response(None)
        return Response(UserProgramSerializer(instance).data)


class CopyProgramFromCatalogView(APIView):
    """Snapshots a catalog Program (admin-managed, shared) into a new,
    fully independent UserProgram the requesting user owns and can edit
    freely — later catalog changes never affect the copy."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        program_id = request.data.get('program_id')
        catalog_program = Program.objects.filter(pk=program_id).prefetch_related('days__exercises').first()
        if not catalog_program:
            return Response({'error': 'Program not found'}, status=404)

        lang = get_user_lang(request)
        user_program = UserProgram.objects.create(
            user=request.user, name=_localized_name(catalog_program, lang)
        )
        for day in catalog_program.days.all():
            new_day = UserProgramDay.objects.create(
                program=user_program, name=_localized_name(day, lang), order=day.order
            )
            for idx, exercise in enumerate(day.exercises.all()):
                # muscle_group is intentionally left blank: the catalog's
                # free-text muscles_* field doesn't map cleanly onto the
                # fixed MUSCLE_GROUP_CHOICES, so the user assigns it once,
                # the same way they already do for any freeform exercise.
                UserProgramExercise.objects.create(
                    day=new_day,
                    exercise=exercise,
                    name=_localized_name(exercise, lang),
                    order=idx,
                )

        instance = UserProgram.objects.filter(pk=user_program.pk).prefetch_related('days__exercises').first()
        return Response(UserProgramSerializer(instance).data, status=201)
