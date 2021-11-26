from modeltranslation.translator import TranslationOptions, register
from ..models import TestamoPage


@register(TestamoPage)
class TestamoPageTranslationOptions(TranslationOptions):
    pass
