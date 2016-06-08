def set_attendees_string(sender, **kwargs):

    action = kwargs["action"]
    instance = kwargs["instance"]

    # Order attendees assuring that internal contacts come first
    attendees = instance.attendees.all().order_by("polymorphic_ctype_id")

    if action not in ("post_add", "post_remove", "post_clear"):
        return

    instance.attendees_string = ", ".join([str(a) for a in attendees])
    instance.save(update_fields=("attendees_string",))
