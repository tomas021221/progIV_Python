from datetime import date
from rest_framework import serializers
from .models import Project, Task, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"

class TaskSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    class Meta:
        model = Task
        fields = [
            "id", "project", "title", "description",
            "priority", "status", "due_date", "tags", "created_at",
        ]
    def validate_due_date(self, value):
        if value and value < date.today():
            raise serializers.ValidationError("La fecha límite no puede ser en el pasado.")
        return value
    def validate(self, data):
        # Validación 1: Tarea completada requiere fecha límite
        if data.get("status") == "completada" and not data.get("due_date"):
            raise serializers.ValidationError(
                "No se puede marcar una tarea como completada sin fecha límite registrada."
            )

        # Validación 2: No permitir 'en_progreso' si el proyecto no tiene tareas completadas
        status = data.get("status")
        if status == "en_progreso":
            # Obtenemos el proyecto desde los datos enviados o desde la tarea existente (si se está editando)
            project = data.get("project") or (self.instance.project if self.instance else None)
            
            # Verificamos con el ORM si el proyecto tiene al menos una tarea con status 'completada'
            if project and not project.tasks.filter(status="completada").exists():
                raise serializers.ValidationError(
                    "Una tarea no puede tener estado 'en progreso' si el proyecto no tiene al menos una tarea completada."
                )

        return data