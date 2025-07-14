    {{ item.name }} = models.CharField(
        _("{{ item.name }}"),
        blank=False,
        max_length=100,
        default="",
    )
