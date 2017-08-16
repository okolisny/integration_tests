# -*- coding: utf-8 -*-
import fauxfactory
import pytest
from widgetastic.exceptions import NoSuchElementException

from cfme import test_requirements
from cfme.cloud.provider import CloudProvider
from cfme.cloud.provider.openstack import OpenStackProvider
from cfme.storage.volume import Volume
from cfme.web_ui import flash

from utils import testgen
from utils.appliance.implementations.ui import navigate_to
from utils.wait import wait_for


pytest_generate_tests = testgen.generate([CloudProvider])


pytestmark = [pytest.mark.tier(3),
              test_requirements.storage,
              pytest.mark.usefixtures('openstack_provider', 'setup_provider')]


@pytest.mark.uncollectif(lambda provider: not provider.one_of(OpenStackProvider))
def test_volume_navigation(openstack_provider):
    # grab a volume name, the table returns a generator so use next
    view = navigate_to(Volume, 'All')
    try:
        volume_name = view.entities.table[0].name.text
    except (StopIteration, NoSuchElementException):
        pytest.skip('Skipping volume navigation for details, no volumes present')
    volume = Volume(name=volume_name, provider=openstack_provider)

    assert view.is_displayed

    view = navigate_to(volume, 'Details')
    assert view.is_displayed

    view = navigate_to(Volume, 'Add')
    assert view.is_displayed


def test_create_volume(openstack_provider):
    volume = Volume(fauxfactory.gen_alpha(), provider=openstack_provider)
    volume.create(1, openstack_provider.get_yaml_data()['tenant'])
    flash.assert_success()
    wait_for(openstack_provider.is_refreshed, timeout=600)
    assert volume.exists()
