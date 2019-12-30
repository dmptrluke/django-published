NEVER_AVAILABLE = -1
AVAILABLE_AFTER = 0
AVAILABLE = 1

PUBLISH_CHOICES = (
    (-1, 'Never Available'),
    (1, 'Available Now'),
    (0, 'Available after "Publish Date"'),
)

__all__ = ['PUBLISH_CHOICES', 'NEVER_AVAILABLE', 'AVAILABLE_AFTER', 'AVAILABLE']
