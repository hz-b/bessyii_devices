import asyncio
import os
import pytest

from bluesky_queueserver import generate_zmq_keys

from .common import re_manager_cmd  # noqa: F401
from .common import fastapi_server_fs  # noqa: F401
from .common import (
    set_qserver_zmq_address,
    set_qserver_zmq_public_key,
    _is_async,
    _select_re_manager_api,
    instantiate_re_api_class,
)


# fmt: off
@pytest.mark.parametrize("option", ["params", "ev", "default_addr"])
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
@pytest.mark.parametrize("protocol", ["ZMQ", "HTTP"])
# fmt: on
def test_ReManagerAPI_parameters_01(
    monkeypatch, re_manager_cmd, fastapi_server_fs, protocol, library, option  # noqa: F811
):
    """
    ReManagerComm_ZMQ_Threads and ReManagerComm_ZMQ_Async,
    ReManagerComm_HTTP_Threads and ReManagerComm_HTTP_Async:
    Check that the server addresses are properly set with parameters and EVs.
    ZMQ: ``zmq_control_addr``, ``zmq_info_addr``, ``QSERVER_ZMQ_CONTROL_ADDRESS``,
    ``QSERVER_ZMQ_INFO_ADDRESS``. HTTP: ``http_server_uri``, ``QSERVER_HTTP_SERVER_URI``.
    """
    zmq_control_addr_server = "tcp://*:60616"
    zmq_control_addr_client = "tcp://localhost:60616"
    zmq_info_addr_server = "tcp://*:60617"
    zmq_info_addr_client = "tcp://localhost:60617"
    http_host = "localhost"
    http_port = 60611
    http_server_uri = f"http://{http_host}:{http_port}"

    zmq_public_key, zmq_private_key = generate_zmq_keys()

    set_qserver_zmq_address(monkeypatch, zmq_server_address=zmq_control_addr_client)
    set_qserver_zmq_public_key(monkeypatch, server_public_key=zmq_public_key)
    monkeypatch.setenv("QSERVER_ZMQ_PRIVATE_KEY_FOR_SERVER", zmq_private_key)
    re_manager_cmd(
        [
            "--zmq-publish-console=ON",
            f"--zmq-control-addr={zmq_control_addr_server}",
            f"--zmq-info-addr={zmq_info_addr_server}",
        ]
    )

    if protocol == "HTTP":
        monkeypatch.setenv("QSERVER_ZMQ_CONTROL_ADDRESS", zmq_control_addr_client)
        monkeypatch.setenv("QSERVER_ZMQ_INFO_ADDRESS", zmq_info_addr_client)
        monkeypatch.setenv("QSERVER_ZMQ_PUBLIC_KEY", zmq_public_key)
        fastapi_server_fs(http_server_host=http_host, http_server_port=http_port)
        if option in "params":
            params = {"http_server_uri": http_server_uri}
        elif option == "ev":
            params = {}
            monkeypatch.setenv("QSERVER_HTTP_SERVER_URI", http_server_uri)
        elif option == "default_addr":
            params = {}
        else:
            assert False, "Unknown option: {option!r}"
    elif protocol == "ZMQ":
        if option == "params":
            params = {
                "zmq_control_addr": zmq_control_addr_client,
                "zmq_info_addr": zmq_info_addr_client,
                "zmq_public_key": zmq_public_key,
            }
        elif option == "ev":
            params = {}
            monkeypatch.setenv("QSERVER_ZMQ_CONTROL_ADDRESS", zmq_control_addr_client)
            monkeypatch.setenv("QSERVER_ZMQ_INFO_ADDRESS", zmq_info_addr_client)
            monkeypatch.setenv("QSERVER_ZMQ_PUBLIC_KEY", zmq_public_key)
        elif option == "default_addr":
            params = {}
        else:
            assert False, "Unknown option: {option!r}"
    else:
        assert False, "Unknown protocol: {protocol!r}"

    rm_api_class = _select_re_manager_api(protocol, library)

    if not _is_async(library):
        RM = instantiate_re_api_class(rm_api_class, **params)
        if option == "default_addr":
            # ZMQ - RequestTimeoutError, HTTP - RequestError
            with pytest.raises((RM.RequestTimeoutError, RM.RequestError)):
                RM.status()
        else:
            RM.status()
            RM.console_monitor.enable()
            RM.environment_open()
            RM.wait_for_idle()
            RM.environment_close()
            RM.wait_for_idle()
            RM.console_monitor.disable()

            text = RM.console_monitor.text()
            assert "RE Environment is ready" in text, text

        RM.close()

    else:

        async def testing():
            RM = instantiate_re_api_class(rm_api_class, **params)
            if option == "default_addr":
                # ZMQ - RequestTimeoutError, HTTP - RequestError
                with pytest.raises((RM.RequestTimeoutError, RM.RequestError)):
                    await RM.status()
            else:
                await RM.status()
                RM.console_monitor.enable()
                await RM.environment_open()
                await RM.wait_for_idle()
                await RM.environment_close()
                await RM.wait_for_idle()
                RM.console_monitor.disable()

                text = await RM.console_monitor.text()
                assert "RE Environment is ready" in text, text

            await RM.close()

        asyncio.run(testing())


# fmt: off
@pytest.mark.parametrize("tout, tout_login, tset, tset_login", [
    (0.5, 10, 0.5, 10),
    (None, None, 5.0, 60.0),  # Default values
    (0, 0, 0, 0),  # Disables timeout by default
])
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
@pytest.mark.parametrize("protocol", ["HTTP"])
# fmt: on
def test_ReManagerAPI_parameters_02(protocol, library, tout, tout_login, tset, tset_login):
    """
    classes ReManagerComm_HTTP_Threads and ReManagerComm_HTTP_Async:
    Test that 'timeout' and 'timeout_login' are set correctly.
    """
    rm_api_class = _select_re_manager_api(protocol, library)

    if not _is_async(library):
        RM = instantiate_re_api_class(rm_api_class, timeout=tout, timeout_login=tout_login)
        assert RM._timeout == tset
        assert RM._timeout_login == tset_login
        RM.close()

    else:

        async def testing():
            RM = instantiate_re_api_class(rm_api_class, timeout=tout, timeout_login=tout_login)
            assert RM._timeout == tset
            assert RM._timeout_login == tset_login
            await RM.close()

        asyncio.run(testing())


# fmt: off
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
@pytest.mark.parametrize("protocol", ["HTTP"])
# fmt: on
def test_send_request_1(re_manager_cmd, fastapi_server_fs, protocol, library):  # noqa: F811
    """
    ``send_request`` API: basic functionality and error handling (for HTTP requests).
    """
    re_manager_cmd()
    fastapi_server_fs()

    rm_api_class = _select_re_manager_api(protocol, library)

    if not _is_async(library):
        RM = instantiate_re_api_class(rm_api_class)

        status = RM.status()
        status2 = RM.send_request(method="status")
        assert status2 == status
        status3 = RM.send_request(method=("GET", "/api/status"))
        assert status3 == status

        with pytest.raises(KeyError, match="Unknown method"):
            RM.send_request(method="abc")

        with pytest.raises(TypeError, match="must be a string or an iterable"):
            RM.send_request(method=10)

        for method in (
            ("GET", "/api/status", "aaa"),
            ("GET",),
            (10, "/api/status"),
            ("GET", {}),
            (10, 20),
        ):
            print(f"Testing method: {method}")
            with pytest.raises(ValueError, match="must consist of 2 string elements"):
                RM.send_request(method=method)

        RM.close()
    else:

        async def testing():
            RM = instantiate_re_api_class(rm_api_class)

            status = await RM.status()
            status2 = await RM.send_request(method="status")
            assert status2 == status
            status3 = await RM.send_request(method=("GET", "/api/status"))
            assert status3 == status

            with pytest.raises(KeyError, match="Unknown method"):
                await RM.send_request(method="abc")

            with pytest.raises(TypeError, match="must be a string or an iterable"):
                await RM.send_request(method=10)

            for method in (
                ("GET", "/api/status", "aaa"),
                ("GET",),
                (10, "/api/status"),
                ("GET", {}),
                (10, 20),
            ):
                print(f"Testing method: {method}")
                with pytest.raises(ValueError, match="must consist of 2 string elements"):
                    await RM.send_request(method=method)

            await RM.close()

        asyncio.run(testing())


# fmt: off
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
@pytest.mark.parametrize("protocol", ["HTTP"])
# fmt: on
def test_send_request_2(fastapi_server_fs, protocol, library):  # noqa: F811
    """
    ``send_request`` API: timeout (for HTTP requests).
    """
    fastapi_server_fs()
    rm_api_class = _select_re_manager_api(protocol, library)

    if not _is_async(library):
        RM = instantiate_re_api_class(rm_api_class)

        # No timeout
        status = RM.send_request(method=("GET", "/api/test/server/sleep"), params={"time": 3})
        assert status["success"] is True

        # Set timeout for the given request
        with pytest.raises(RM.RequestTimeoutError):
            RM.send_request(method=("GET", "/api/test/server/sleep"), params={"time": 3}, timeout=1)

        # Use the defaut timeout
        with pytest.raises(RM.RequestTimeoutError):
            RM.send_request(method=("GET", "/api/test/server/sleep"), params={"time": RM._timeout + 1})

        RM.close()
    else:

        async def testing():
            RM = instantiate_re_api_class(rm_api_class)

            # No timeout
            status = await RM.send_request(method=("GET", "/api/test/server/sleep"), params={"time": 3})
            assert status["success"] is True

            # Set timeout for the given request
            with pytest.raises(RM.RequestTimeoutError):
                await RM.send_request(method=("GET", "/api/test/server/sleep"), params={"time": 3}, timeout=1)

            # Use the defaut timeout
            with pytest.raises(RM.RequestTimeoutError):
                await RM.send_request(method=("GET", "/api/test/server/sleep"), params={"time": RM._timeout + 1})

            await RM.close()

        asyncio.run(testing())


# Configuration file for 'toy' authentication provider. The passwords are explicitly listed.
config_toy_yml = """
uvicorn:
    host: localhost
    port: 60610
authentication:
    providers:
        - provider: toy
          authenticator: bluesky_httpserver.authenticators:DictionaryAuthenticator
          args:
              users_to_passwords:
                  alice: alice_password
                  bob: bob_password
                  cara: cara_password
    qserver_admins:
        - provider: toy
          id: alice
"""


# fmt: off
@pytest.mark.parametrize("default_provider", [True, False])
@pytest.mark.parametrize("use_kwargs", [True, False])
@pytest.mark.parametrize("library", ["THREADS", "ASYNC"])
@pytest.mark.parametrize("protocol", ["HTTP"])
# fmt: on
def test_login_1(
    tmpdir,
    monkeypatch,
    re_manager_cmd,  # noqa: F811
    fastapi_server_fs,  # noqa: F811
    protocol,
    library,
    default_provider,
    use_kwargs,
):
    """
    ``send_request`` API: timeout (for HTTP requests).
    """
    re_manager_cmd()

    config_dir = os.path.join(tmpdir, "config")
    config_path = os.path.join(config_dir, "config_toy.yml")
    os.makedirs(config_dir)
    with open(config_path, "wt") as f:
        f.writelines(config_toy_yml)

    monkeypatch.setenv("QSERVER_HTTP_SERVER_CONFIG", config_path)
    monkeypatch.chdir(tmpdir)

    fastapi_server_fs()
    rm_api_class = _select_re_manager_api(protocol, library)

    if not _is_async(library):
        params = {"http_auth_provider": "/toy/token"} if default_provider else {}
        RM = instantiate_re_api_class(rm_api_class, **params)

        # Make sure access does not work without authentication
        with pytest.raises(RM.ClientError, match="401"):
            RM.status()

        login_args, login_kwargs = [], {}
        if not default_provider:
            login_kwargs.update({"provider": "/toy/token"})
        if use_kwargs:
            login_kwargs.update({"username": "bob", "password": "bob_password"})
        else:
            login_args.extend(["bob", "bob_password"])

        token_info = RM.login(*login_args, **login_kwargs)
        auth_key = RM.auth_key
        assert isinstance(auth_key, tuple), auth_key
        assert auth_key[0] == token_info["access_token"]
        assert auth_key[1] == token_info["refresh_token"]

        # Now make sure that access works
        RM.status()

        RM.close()
    else:

        async def testing():
            params = {"http_auth_provider": "/toy/token"} if default_provider else {}
            RM = instantiate_re_api_class(rm_api_class, **params)

            # Make sure access does not work without authentication
            with pytest.raises(RM.ClientError, match="401"):
                await RM.status()

            login_args, login_kwargs = [], {}
            if not default_provider:
                login_kwargs.update({"provider": "/toy/token"})
            if use_kwargs:
                login_kwargs.update({"username": "bob", "password": "bob_password"})
            else:
                login_args.extend(["bob", "bob_password"])

            token_info = await RM.login(*login_args, **login_kwargs)
            auth_key = RM.auth_key
            assert isinstance(auth_key, tuple), auth_key
            assert auth_key[0] == token_info["access_token"]
            assert auth_key[1] == token_info["refresh_token"]

            # Now make sure that access works
            await RM.status()

            await RM.close()

        asyncio.run(testing())
