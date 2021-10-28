# stdlib
import uuid

# third party
import pytest
import torch

# syft absolute
import syft as sy
from syft.core.node.common.action.exception_action import UnknownPrivateException

NETWORK_PORT = 9081
DOMAIN1_PORT = 9082
DOMAIN1_VPN_IP = "100.64.0.2"


@pytest.mark.integration
def test_domain1_via_network_proxy_client() -> None:
    unique_tag = str(uuid.uuid4())
    network_client = sy.login(
        email="info@openmined.org", password="changethis", port=NETWORK_PORT
    )
    domain_client = sy.login(
        email="info@openmined.org", password="changethis", port=DOMAIN1_PORT
    )

    x = torch.Tensor([1, 2, 3])
    x_ptr = x.send(domain_client, tags=[unique_tag])

    domain_list = network_client.domains.all(pandas=False)
    assert len(domain_list) > 0

    proxy_client = network_client.domains[domain_client.address.target_id.id]

    assert proxy_client.address == domain_client.address
    assert proxy_client.name == domain_client.name
    assert proxy_client.routes[0] != domain_client.routes[0]

    y_ptr = proxy_client.store[x_ptr.id_at_location.no_dash]
    assert x_ptr.id_at_location == y_ptr.id_at_location
    assert type(x_ptr).__name__ == type(y_ptr).__name__


@pytest.mark.integration
def test_search_network() -> None:
    unique_tag = str(uuid.uuid4())
    domain_client = sy.login(
        email="info@openmined.org", password="changethis", port=DOMAIN1_PORT
    )

    x = torch.Tensor([1, 2, 3])
    x.send(domain_client, tags=[unique_tag])

    network_client = sy.login(port=NETWORK_PORT)

    query = [unique_tag]
    result = network_client.search(query=query, pandas=False)

    assert len(result) == 1
    assert result[0]["name"] == "test_domain_1"
    assert result[0]["host_or_ip"] == DOMAIN1_VPN_IP


@pytest.mark.integration
def test_proxy_login_logout_network() -> None:
    unique_tag = str(uuid.uuid4())
    domain_client = sy.login(
        email="info@openmined.org", password="changethis", port=DOMAIN1_PORT
    )

    x = torch.Tensor([1, 2, 3])
    x.send(domain_client, tags=[unique_tag])

    network_client = sy.login(port=NETWORK_PORT)

    domain_list = network_client.domains.all(pandas=False)
    assert len(domain_list) > 0

    proxy_client = network_client.domains[0]

    # cant get it as a guest
    with pytest.raises(UnknownPrivateException):
        proxy_client.store[unique_tag].get(delete_obj=False)

    proxy_client.login(email="info@openmined.org", password="changethis")

    res = proxy_client.store[unique_tag].get(delete_obj=False)
    assert (res == torch.Tensor([1, 2, 3])).all()

    proxy_client.logout()
    # cant get it as a guest
    with pytest.raises(UnknownPrivateException):
        proxy_client.store[unique_tag].get(delete_obj=False)
