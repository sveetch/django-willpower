    {{ field.name }} = None{#
-- Currently disabled because we are unable to correctly resolve the model factory path
-- from the target that is especially done for model resolution but does not provide
-- the targeted model dataclass to get its name without wobject path or simple path
    @factory.post_generation
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
            objects = [{{ field.target|wobject_render(quote="")|str_format(appname=model_inventory.app.code) }}Factory()]
        # Take given objects
        else:
            objects = extracted

        # Add objects
        for item in objects:
            self.objects.add(item)#}