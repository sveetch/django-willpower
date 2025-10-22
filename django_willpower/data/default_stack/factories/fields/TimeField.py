    @factory.lazy_attribute
    def {{ field.name }}(self):
        return timezone.now().time()