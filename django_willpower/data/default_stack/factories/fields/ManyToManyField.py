{% import '_utils.jinja' as utils %}    @factory.post_generation
    def fill_{{ field.name }}(self, create, extracted, **kwargs):
        """
        Add {{ field.name }} objects.

        Arguments:
            create (bool): True for create strategy, False for build strategy.
            extracted (object): If ``True``, will create a new single random
                object. If a list, assume it's a list of objects to add. Finally if
                empty don't do anything.
        """
        # Do nothing for build strategy
        if not create or not extracted:
            return

        # Create a new random object
        if extracted is True:
            objects = [{{ utils.get_subfactory_modulename(app.code, field.target.parsed_object) }}()]
        # Take given objects
        else:
            objects = extracted

        # Add objects
        for item in objects:
            self.objects.add(item)