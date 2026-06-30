import pytest
from django.template import Template, Context

@pytest.mark.django_db
def test_get_item_templatetag():
    t = Template('{% load habit_extras %}{{ dict|get_item:"key" }}')
    c = Context({'dict': {'key': 'value'}})
    rendered = t.render(c)
    assert 'value' in rendered


@pytest.mark.django_db
def test_get_item_templatetag_missing_key():
    t = Template('{% load habit_extras %}{{ dict|get_item:"missing_key" }}')
    c = Context({'dict': {'key': 'value'}})
    rendered = t.render(c)
    assert rendered.strip() == ''


@pytest.mark.django_db
def test_get_item_templatetag_bad_input_type():
    t = Template('{% load habit_extras %}{{ not_a_dict|get_item:"key" }}')
    c = Context({'not_a_dict': "just a string"})
    rendered = t.render(c)
    assert rendered.strip() == ''
